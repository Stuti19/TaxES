# extractor.py
#!/usr/bin/env python3
"""
extractor.py

Start Textract analysis for an S3 object and write outputs (CSV/JSON)
to the same bucket under out/<base>/.

Assumptions:
- Input bucket is 'ocrdocstorage' (change S3_BUCKET_DEFAULT if you want)
- Uploaded files are in 'in/' folder but extractor accepts full key
- Outputs are written to 'out/<base>/' inside the same bucket
- Uses helper functions from parser.py (extract_key_values, extract_table_cells, build_passbook_summary, put_csv, put_json, collect_text)
"""
import os
import time
import json
import logging
import random
import urllib.parse
from typing import Tuple, List, Dict, Optional

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from passbook_parsar import (
    extract_key_values,
    extract_table_cells,
    build_passbook_summary,
    put_csv,
    put_json,
    collect_text
)

logger = logging.getLogger(_name_)
logger.setLevel(logging.INFO)

# Default bucket & region - your project uses 'ocrdocstorage' for in/out
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_DEFAULT = os.getenv("S3_BUCKET_NAME", "ocrdocstorage")
OUTPUT_S3_BUCKET = os.getenv("OUTPUT_S3_BUCKET")  # optional override

boto3_kwargs = {"region_name": AWS_REGION} if AWS_REGION else {}
s3 = boto3.client("s3", **boto3_kwargs)
textract = boto3.client("textract", **boto3_kwargs)


def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event))
    records = event.get("Records", [])
    if not records:
        return {"statusCode": 400, "body": "No S3 records found"}

    results = []
    for r in records:
        try:
            bucket = r["s3"]["bucket"]["name"]
            key = urllib.parse.unquote_plus(r["s3"]["object"]["key"])
        except Exception:
            logger.exception("Malformed S3 event record: %s", r)
            results.append({"error": "Malformed record", "record": r})
            continue

        try:
            result = process_document(bucket, key)
            results.append(result)
        except Exception as e:
            logger.exception("Error processing %s/%s", bucket, key)
            results.append({"bucket": bucket, "key": key, "error": str(e)})

    return {"statusCode": 200, "body": json.dumps(results)}


def _start_textract_analysis_with_retries(document_bucket: str, document_key: str, max_attempts: int = 3) -> str:
    attempt = 0
    last_exc: Optional[Exception] = None
    while attempt < max_attempts:
        try:
            kwargs = {
                "DocumentLocation": {"S3Object": {"Bucket": document_bucket, "Name": document_key}},
                "FeatureTypes": ["FORMS", "TABLES"],
            }
            resp = textract.start_document_analysis(**kwargs)
            job_id = resp["JobId"]
            logger.info("Started Textract job %s for s3://%s/%s", job_id, document_bucket, document_key)
            return job_id
        except (ClientError, BotoCoreError) as e:
            last_exc = e
            backoff = (2 ** attempt) + random.uniform(0, 1)
            logger.warning("start_document_analysis attempt %d failed: %s — retrying in %.1fs", attempt + 1, e, backoff)
            time.sleep(backoff)
            attempt += 1

    raise RuntimeError(f"Failed to start Textract job after {max_attempts} attempts: {last_exc}")


def collect_results(job_id: str, max_wait_seconds: int = 600) -> Tuple[List[Dict], Dict]:
    blocks: List[Dict] = []
    meta: Dict = {}
    next_token: Optional[str] = None
    start_time = time.time()
    attempt = 0

    while True:
        if time.time() - start_time > max_wait_seconds:
            raise TimeoutError(f"Textract job {job_id} timed out after {max_wait_seconds} seconds")
        try:
            kwargs = {"JobId": job_id, "MaxResults": 1000}
            if next_token:
                kwargs["NextToken"] = next_token

            resp = textract.get_document_analysis(**kwargs)
            status = resp.get("JobStatus")
            logger.info("Textract job %s status=%s (collected_blocks=%d)", job_id, status, len(blocks))

            returned_blocks = resp.get("Blocks", [])
            if returned_blocks:
                blocks.extend(returned_blocks)

            if "DocumentMetadata" in resp:
                meta = resp.get("DocumentMetadata", meta)

            next_token = resp.get("NextToken")

            if status in ("SUCCEEDED", "PARTIAL_SUCCESS") and not next_token:
                logger.info("Textract job %s finished with status=%s; total blocks=%d", job_id, status, len(blocks))
                break
            if status == "FAILED":
                raise RuntimeError(f"Textract job failed: {job_id} - {json.dumps(resp)}")

            attempt += 1
            sleep_seconds = min(1.0 * (1.5 ** attempt), 8.0) + random.uniform(0, 0.5)
            time.sleep(sleep_seconds)

        except ClientError as e:
            attempt += 1
            if attempt > 6:
                logger.exception("Exceeded retries while calling get_document_analysis: %s", e)
                raise
            backoff = min(2 ** attempt, 16) + random.uniform(0, 1)
            logger.warning("get_document_analysis ClientError: %s — retrying in %.1fs", e, backoff)
            time.sleep(backoff)
        except BotoCoreError as e:
            logger.exception("Unexpected boto core error: %s", e)
            raise

    return blocks, meta


def process_document(bucket: str, key: str) -> dict:
    if not bucket or not key:
        raise ValueError("Bucket and key must be provided")

    base = os.path.splitext(os.path.basename(key))[0]
    out_dir = f"out/{base}/"

    logger.info("Starting Textract job for s3://%s/%s", bucket, key)
    job_id = _start_textract_analysis_with_retries(bucket, key)

    blocks, meta = collect_results(job_id)

    if not blocks:
        logger.warning("No blocks returned for job %s (s3://%s/%s)", job_id, bucket, key)

    kv_pairs = extract_key_values(blocks)
    table_cells = extract_table_cells(blocks)
    summary = build_passbook_summary(blocks, kv_pairs)

    dest_bucket = OUTPUT_S3_BUCKET or bucket or S3_BUCKET_DEFAULT

    # Write outputs into the same bucket under out/<base>/
    put_csv(s3, dest_bucket, f"{out_dir}key_values.csv", ["Key", "Value", "Confidence"], kv_pairs)
    put_csv(s3, dest_bucket, f"{out_dir}transactions.csv",
            ["Page", "Table", "Row", "Column", "Text", "Confidence"], table_cells)
    put_json(s3, dest_bucket, f"{out_dir}summary.json", summary)
    put_json(s3, dest_bucket, f"{out_dir}all_key_values.json",
             {"pairs": [{"Key": k, "Value": v, "Confidence": c} for k, v, c in kv_pairs]})

    logger.info("Wrote outputs to s3://%s/%s", dest_bucket, out_dir)

    return {
        "job_id": job_id,
        "pages": meta.get("Pages"),
        "kv_pairs": len(kv_pairs),
        "table_cells": len(table_cells),
        "summary_s3": f"s3://{dest_bucket}/{out_dir}summary.json",
        "key_values_csv": f"s3://{dest_bucket}/{out_dir}key_values.csv",
        "transactions_csv": f"s3://{dest_bucket}/{out_dir}transactions.csv",
        "all_key_values_json": f"s3://{dest_bucket}/{out_dir}all_key_values.json",
    }


if _name_ == "_main_":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run Textract processing on an S3 object")
    parser.add_argument("--bucket", required=False, default=S3_BUCKET_DEFAULT, help="S3 bucket name (default: ocrdocstorage)")
    parser.add_argument("--key", required=True, help="S3 object key (e.g. in/myfile.pdf)")
    parser.add_argument("--region", required=False, help="AWS region override (optional)")
    args = parser.parse_args()

    if args.region:
        os.environ["AWS_REGION"] = args.region

    result = process_document(args.bucket, args.key)
    print(json.dumps(result, indent=2))
