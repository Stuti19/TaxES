import time
from typing import Tuple, List, Dict

import boto3

_textract = boto3.client("textract")


def start_job_and_collect(bucket: str, key: str, max_wait_seconds: int = 480) -> Tuple[List[dict], Dict]:
    """Start Textract FORMS+TABLES job and poll until complete. Returns (blocks, metadata)."""
    job = _textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
        FeatureTypes=["FORMS", "TABLES"],
    )
    job_id = job["JobId"]

    blocks: List[dict] = []
    meta: Dict = {}
    next_token = None
    start = time.time()
    backoff = 1.2

    while True:
        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"Textract job {job_id} timed out")

        params = {"JobId": job_id, "MaxResults": 1000}
        if next_token:
            params["NextToken"] = next_token

        resp = _textract.get_document_analysis(**params)
        status = resp.get("JobStatus")

        if status == "FAILED":
            raise RuntimeError(f"Textract job failed: {job_id}")

        blocks.extend(resp.get("Blocks", []))
        meta = resp.get("DocumentMetadata", meta)
        next_token = resp.get("NextToken")

        if not next_token and status in ("SUCCEEDED", "PARTIAL_SUCCESS"):
            break

        time.sleep(backoff)
        backoff = min(backoff * 1.5, 8.0)

    return blocks, meta
