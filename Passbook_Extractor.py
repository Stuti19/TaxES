import os
import io
import csv
import json
import time
import logging
import urllib.parse
from typing import List, Dict, Optional, Tuple

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
textract = boto3.client("textract")


def lambda_handler(event, context):
    """Handles S3 ObjectCreated events (recommended) or a manual test event."""
    logger.info("Event: %s", json.dumps(event))

    records = event.get("Records", [])
    if not records:
        return {"statusCode": 400, "body": "No S3 records found"}

    results = []
    for r in records:
        bucket = r["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(r["s3"]["object"]["key"])  # handles spaces/%20
        logger.info(f"Processing file: s3://{bucket}/{key}")
        result = process_document(bucket, key)
        results.append(result)

    return {"statusCode": 200, "body": json.dumps(results)}


# --------------------------- Core processing ---------------------------

def process_document(bucket: str, key: str) -> dict:
    base = os.path.splitext(os.path.basename(key))[0]
    out_dir = f"out/{base}/"

    # 1) Start Textract (no regex; ML-only)
    job_id = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
        FeatureTypes=["FORMS", "TABLES"],
    )["JobId"]

    # 2) Collect all result pages
    blocks, meta = collect_results(job_id)

    # 3) Parse FORMS and TABLES
    kv_pairs = extract_key_values(blocks)     # -> [[Key, Value, Confidence], ...]
    table_cells = extract_table_cells(blocks) # -> [[Page, Table, Row, Col, Text, Confidence], ...]

    # 4) Build a human-friendly summary JSON (IFSC, Bank, Account No, Name, etc.)
    summary = build_passbook_summary(blocks, kv_pairs)

    # 5) Write outputs back to S3
    put_csv(bucket, f"{out_dir}key_values.csv", ["Key", "Value", "Confidence"], kv_pairs)
    put_csv(bucket, f"{out_dir}transactions.csv",
            ["Page", "Table", "Row", "Column", "Text", "Confidence"], table_cells)
    put_json(bucket, f"{out_dir}summary.json", summary)
    put_json(bucket, f"{out_dir}all_key_values.json",
             {"pairs": [{"Key": k, "Value": v, "Confidence": c} for k, v, c in kv_pairs]})

    return {
        "pages": meta.get("Pages"),
        "kv_pairs": len(kv_pairs),
        "table_cells": len(table_cells),
        "summary_s3": f"s3://{bucket}/{out_dir}summary.json",
        "key_values_csv": f"s3://{bucket}/{out_dir}key_values.csv",
        "transactions_csv": f"s3://{bucket}/{out_dir}transactions.csv",
    }


def collect_results(job_id: str, max_wait_seconds: int = 480) -> Tuple[List[dict], dict]:
    """Poll GetDocumentAnalysis until all pages are returned."""
    blocks: List[dict] = []
    meta: dict = {}
    next_token = None
    start = time.time()
    backoff = 1.2

    while True:
        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"Textract job {job_id} timed out")

        kwargs = {"JobId": job_id, "MaxResults": 1000}
        if next_token:
            kwargs["NextToken"] = next_token

        resp = textract.get_document_analysis(**kwargs)
        status = resp.get("JobStatus")
        blocks.extend(resp.get("Blocks", []))
        meta = resp.get("DocumentMetadata", meta)
        next_token = resp.get("NextToken")

        if not next_token and status in ("SUCCEEDED", "PARTIAL_SUCCESS"):
            break
        if status == "FAILED":
            raise RuntimeError(f"Textract job failed: {job_id}")

        time.sleep(backoff)
        backoff = min(backoff * 1.5, 8.0)

    return blocks, meta


# ------------------------------ Parsing ------------------------------

def extract_key_values(blocks: List[dict]) -> List[List[object]]:
    """Return [[Key, Value, Confidence], ...] using Textract KEY_VALUE_SET semantics."""
    id_map = {b.get("Id"): b for b in blocks if "Id" in b}
    out: List[List[object]] = []

    for b in blocks:
        if b.get("BlockType") == "KEY_VALUE_SET" and "KEY" in b.get("EntityTypes", []):
            key_text = collect_text(b, id_map)

            value_block = None
            for rel in b.get("Relationships", []) or []:
                if rel.get("Type") == "VALUE":
                    for vid in rel.get("Ids", []):
                        cand = id_map.get(vid)
                        if cand and cand.get("BlockType") == "KEY_VALUE_SET":
                            value_block = cand
                            break
                if value_block:
                    break

            val_text = collect_text(value_block, id_map) if value_block else ""
            if key_text or val_text:
                key_conf = float(b.get("Confidence", 0.0) or 0.0)
                val_conf = float((value_block or {}).get("Confidence", 0.0) or 0.0)
                conf = round(min(key_conf, val_conf), 2)
                out.append([key_text.strip(), val_text.strip(), conf])

    out.sort(key=lambda r: (r[0] or "").lower())
    return out


def extract_table_cells(blocks: List[dict]) -> List[List[object]]:
    """Return raw table cells: [[Page, Table, Row, Column, Text, Confidence], ...]."""
    id_map = {b.get("Id"): b for b in blocks if "Id" in b}
    rows: List[List[object]] = []
    table_count: Dict[int, int] = {}  # page -> index

    # First find TABLE blocks so we can number them per page
    for b in blocks:
        if b.get("BlockType") == "TABLE":
            page = b.get("Page")
            table_count[page] = table_count.get(page, 0) + 1
            t_index = table_count[page]

            for rel in b.get("Relationships", []) or []:
                if rel.get("Type") == "CHILD":
                    for cid in rel.get("Ids", []):
                        cell = id_map.get(cid)
                        if not cell or cell.get("BlockType") != "CELL":
                            continue
                        text = collect_text(cell, id_map)
                        conf = round(float(cell.get("Confidence", 0.0) or 0.0), 2)
                        rows.append([
                            page,
                            t_index,
                            cell.get("RowIndex"),
                            cell.get("ColumnIndex"),
                            text.strip(),
                            conf
                        ])

    rows.sort(key=lambda r: (r[0] or 0, r[1], r[2], r[3]))
    return rows


def collect_text(block: Optional[dict], id_map: Dict[str, dict]) -> str:
    """Concatenate text from WORD / LINE / SELECTION_ELEMENT children."""
    if not block:
        return ""
    parts: List[str] = []
    for rel in block.get("Relationships", []) or []:
        if rel.get("Type") == "CHILD":
            for cid in rel.get("Ids", []):
                child = id_map.get(cid)
                if not child:
                    continue
                bt = child.get("BlockType")
                if bt == "WORD":
                    parts.append(child.get("Text", ""))
                elif bt == "LINE":
                    parts.append(child.get("Text", ""))
                elif bt == "SELECTION_ELEMENT":
                    parts.append("☑" if child.get("SelectionStatus") == "SELECTED" else "☐")
    return " ".join([p for p in parts if p])


# ------------------------- Summary JSON builder -------------------------

def build_passbook_summary(blocks: List[dict], kv_pairs: List[List[object]]) -> dict:
    """
    Build a clean summary of common passbook fields without regex:
    bank_name, account_number, cif_number, customer_name, ifsc, branch,
    branch_code, address, phone, email, date_of_issue.
    """
    # Normalize KV pairs -> {label_lower: value}
    kv_dict = {}
    for k, v, _c in kv_pairs:
        if k:
            kv_dict[k.strip().lower()] = (v or "").strip()

    def first_match(needles: List[str]) -> Optional[str]:
        for needle in needles:
            for label, value in kv_dict.items():
                if needle in label and value:
                    return value
        return None

    # Common variants
    account_number = first_match(["account no", "a/c no", "ac no", "account number"])
    cif_number     = first_match(["cif", "cif no"])
    customer_name  = first_match(["customer name", "account holder", "name"])
    ifsc           = first_match(["ifsc", "ifsc code"])
    branch         = first_match(["branch", "branch name"])
    branch_code    = first_match(["branch code"])
    address        = first_match(["address"])
    phone          = first_match(["phone", "mobile"])
    email          = first_match(["email", "e-mail"])
    date_of_issue  = first_match(["date of issue", "date of opening", "date"])

    # Fallbacks from LINE text (for bank name / IFSC shape)
    lines = [b.get("Text", "") for b in blocks if b.get("BlockType") == "LINE"]

    bank_name = None
    for t in lines:
        if "bank" in t.lower():
            bank_name = t.strip()
            break

    # IFSC fallback: look for 11-char alphanumeric token where first 4 are letters; prefer 5th char '0'
    if not ifsc:
        for t in lines:
            tokens = t.replace(":", " ").replace(",", " ").split()
            for tok in tokens:
                tok = tok.strip()
                if len(tok) == 11 and tok.isalnum() and tok[:4].isalpha():
                    if ifsc is None:
                        ifsc = tok
                    if tok[4] == "0":   # prefer standard pattern
                        ifsc = tok
                        break
            if ifsc:
                break

    summary = {
        "bank_name": bank_name,
        "account_number": account_number,
        "cif_number": cif_number,
        "customer_name": customer_name,
        "ifsc": (ifsc.upper() if ifsc else None),
        "branch": branch,
        "branch_code": branch_code,
        "address": address,
        "phone": phone,
        "email": email,
        "date_of_issue": date_of_issue,
    }
    # Remove empty fields
    return {k: v for k, v in summary.items() if v}


# ------------------------------ S3 helpers ------------------------------

def put_csv(bucket: str, key: str, headers: List[str], rows: List[List[object]]):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    for r in rows:
        w.writerow(r)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue().encode("utf-8"),
                  ContentType="text/csv")
    logger.info(f"Wrote s3://{bucket}/{key}")


def put_json(bucket: str, key: str, obj: dict):
    data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType="application/json")
    logger.info(f"Wrote s3://{bucket}/{key}")
