import os
import io
import csv
import json
import time
import logging
import urllib.parse
from typing import List, Dict, Optional, Tuple

import boto3
from backend.passbook_parser import (
    extract_key_values,
    extract_table_cells,
    build_passbook_summary,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
textract = boto3.client("textract")


def lambda_handler(event, context):
    """AWS Lambda entry point for passbook processing"""
    logger.info("Event: %s", json.dumps(event))

    records = event.get("Records", [])
    if not records:
        return {"statusCode": 400, "body": "No S3 records found"}

    results = []
    for r in records:
        bucket = r["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(r["s3"]["object"]["key"])
        logger.info(f"Processing file: s3://{bucket}/{key}")
        result = process_document(bucket, key)
        results.append(result)

    return {"statusCode": 200, "body": json.dumps(results)}


# --------------------------- Core processing ---------------------------

def process_document(bucket: str, key: str) -> dict:
    base = os.path.splitext(os.path.basename(key))[0]
    out_dir = f"out/passbook/{base}/"

    # 1) Start Textract analysis
    job_id = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
        FeatureTypes=["FORMS", "TABLES"],
    )["JobId"]

    # 2) Collect results
    blocks, meta = collect_results(job_id)

    # 3) Parse FORMS and TABLES using parser
    kv_pairs = extract_key_values(blocks)
    table_cells = extract_table_cells(blocks)
    summary = build_passbook_summary(blocks, kv_pairs)

    # 4) Save outputs to S3
    put_csv(bucket, f"{out_dir}key_values.csv", ["Key", "Value", "Confidence"], kv_pairs)
    put_csv(bucket, f"{out_dir}transactions.csv",
            ["Page", "Table", "Row", "Column", "Text", "Confidence"], table_cells)
    put_json(bucket, f"{out_dir}summary.json", summary)

    return {
        "pages": meta.get("Pages"),
        "kv_pairs": len(kv_pairs),
        "table_cells": len(table_cells),
        "summary_s3": f"s3://{bucket}/{out_dir}summary.json",
    }


def collect_results(job_id: str, max_wait_seconds: int = 480) -> Tuple[List[dict], dict]:
    """Poll Textract GetDocumentAnalysis until all pages are returned."""
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


# --------------------------- S3 helpers ---------------------------

def put_csv(bucket: str, key: str, headers: List[str], rows: List[List[object]]):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buf.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )
    logger.info(f"Wrote s3://{bucket}/{key}")


def put_json(bucket: str, key: str, obj: dict):
    data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType="application/json",
    )
    logger.info(f"Wrote s3://{bucket}/{key}")
