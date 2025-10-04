import json
import os
from dotenv import load_dotenv
import boto3
import re

# Load environment variables
load_dotenv('passbook.env')

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


class PassbookParser:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

    def parse_json(self, user_id, json_file=None):
        """
        Load JSON extracted data, check for missing IFSC, and update JSON.
        """
        if not json_file:
            json_file = f"{user_id}_passbook_extracted.json"

        # Download JSON from S3 if it exists
        try:
            self.s3.download_file(S3_BUCKET_NAME, f"out/{user_id}/{json_file}", json_file)
        except Exception:
            pass  # If not on S3, use local file

        # Load JSON data
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {"status": "error", "message": "JSON file not found."}

        # Concatenate all text to search for missing IFSC
        full_text = " ".join(item.get("Key", "") + " " + item.get("Value", "") for item in data)

        # Check for IFSC using regex if missing
        if not any("IFSC" in item.get("Key", "").upper() for item in data):
            ifsc_match = re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', full_text)
            if ifsc_match:
                data.append({
                    "Key": "IFSC",
                    "Value": ifsc_match.group(0)
                })

        # Update any empty IFSC keys
        for item in data:
            if "IFSC" in item.get("Key", "").upper() and not item.get("Value"):
                item["Value"] = "Not found"

        # Save updated JSON
        updated_json_file = f"{user_id}_passbook_parsed.json"
        with open(updated_json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Upload updated JSON to S3
        self.s3.upload_file(updated_json_file, S3_BUCKET_NAME, f"out/{user_id}/{updated_json_file}")

        return {
            "status": "success",
            "json_file": updated_json_file,
            "data": data
        }


def parse_passbook(user_id, json_file=None):
    parser = PassbookParser()
    return parser.parse_json(user_id, json_file)


if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    result = parse_passbook(user_id)
    print(json.dumps(result, indent=2))
