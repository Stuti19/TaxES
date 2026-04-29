import os
import io
import csv
import json
import logging
import urllib.parse
from typing import List, Dict

import boto3

from extractor.textract_io import start_job_and_collect
from extractor.parsing import extract_key_values, extract_table_cells
from parser.summary import build_passbook_summary

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    S3 ObjectCreated event -> Textract -> write:
      - out/<file>/key_values.csv
      - out/<file>/transactions.csv
      - out/<file>/summary.json
      - out/<file>/all_key_values.json
    """
    logger.info("Event: %s", json.dumps(event))

    records = event.get("Records", [])
    if not records:
        return {"statusCode": 400, "body": "No S3 records found"}

    results = []
    for r in records:
        bucket = r["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(r["s3"]["object"]["key"])
        logger.info(f"Processing file: s3://{bucket}/{key}")

        base = os.path.splitext(os.path.basename(key))[0]
        out_dir = f"out/{base}/"

        # 1) Textract (FORMS + TABLES)
        blocks, meta = start_job_and_collect(bucket, key)

        # 2) Parse
        kv_pairs = extract_key_values(blocks)       # [[Key, Value, Confidence], ...]
        table_cells = extract_table_cells(blocks)   # [[Page,Table,Row,Col,Text,Conf], ...]
        summary = build_passbook_summary(blocks, kv_pairs)

        # 3) Save to S3
        put_csv(bucket, f"{out_dir}key_values.csv", ["Key", "Value", "Confidence"], kv_pairs)
        put_csv(bucket, f"{out_dir}transactions.csv",
                ["Page", "Table", "Row", "Column", "Text", "Confidence"], table_cells)
        put_json(bucket, f"{out_dir}summary.json", summary)
        put_json(bucket, f"{out_dir}all_key_values.json",
                 {"pairs": [{"Key": k, "Value": v, "Confidence": c} for k, v, c in kv_pairs]})

        results.append({
            "pages": meta.get("Pages"),
            "kv_pairs": len(kv_pairs),
            "table_cells": len(table_cells),
            "summary_s3": f"s3://{bucket}/{out_dir}summary.json"
        })

    return {"statusCode": 200, "body": json.dumps(results)}


# ----------------- Simple S3 writers ----------------- #

def put_csv(bucket: str, key: str, headers: List[str], rows: List[List[object]]):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    for r in rows:
        w.writerow(r)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue().encode("utf-8"),
                  ContentType="text/csv")
    logger.info(f"Wrote s3://{bucket}/{key}")


def put_json(bucket: str, key: str, obj: Dict):
    data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType="application/json")
    logger.info(f"Wrote s3://{bucket}/{key}")
