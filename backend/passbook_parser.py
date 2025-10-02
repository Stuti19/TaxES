import json
import csv
import os
from dotenv import load_dotenv
import boto3

# Load environment variables
load_dotenv()

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

    def parse_json_to_csv(self, user_id, json_file=None):
        if not json_file:
            json_file = f"{user_id}_passbook_extracted.json"

        # Load JSON data
        with open(json_file, "r") as f:
            data = json.load(f)

        if not data:
            return {"status": "error", "message": "No data found in JSON file."}

        # Create CSV file
        csv_file = f"{user_id}_passbook_parsed.csv"
        with open(csv_file, "w", newline="") as f:
            fieldnames = ["Key", "Value", "Confidence"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow({
                    "Key": item.get("Key", ""),
                    "Value": item.get("Value", ""),
                    "Confidence": item.get("Confidence", 0)
                })

        # Upload CSV back to S3
        self.s3.upload_file(csv_file, S3_BUCKET_NAME, f"out/{user_id}/{csv_file}")

        return {"status": "success", "json_file": json_file, "csv_file": csv_file}

    def parse_json_to_structured_csv(self, user_id, json_file=None):
        """
        Optional: structure CSV into columns for easier analysis
        Example columns: Date, Description, Debit, Credit, Balance
        """
        if not json_file:
            json_file = f"{user_id}_passbook_extracted.json"

        with open(json_file, "r") as f:
            data = json.load(f)

        # Example heuristic: find transactions by key-value patterns
        transactions = []
        for item in data:
            key = item.get("Key", "").lower()
            value = item.get("Value", "")
            if any(k in key for k in ["date", "txn date"]):
                txn = {"Date": value, "Description": "", "Debit": "", "Credit": "", "Balance": ""}
                transactions.append(txn)
            elif transactions:
                # Append other fields based on order
                txn = transactions[-1]
                if "description" in key:
                    txn["Description"] = value
                elif "debit" in key:
                    txn["Debit"] = value
                elif "credit" in key:
                    txn["Credit"] = value
                elif "balance" in key:
                    txn["Balance"] = value

        structured_csv = f"{user_id}_passbook_structured.csv"
        if transactions:
            with open(structured_csv, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Date", "Description", "Debit", "Credit", "Balance"])
                writer.writeheader()
                for txn in transactions:
                    writer.writerow(txn)

            # Upload structured CSV to S3
            self.s3.upload_file(structured_csv, S3_BUCKET_NAME, f"out/{user_id}/{structured_csv}")

            return {
                "status": "success",
                "structured_csv": structured_csv,
                "transaction_count": len(transactions)
            }

        return {"status": "error", "message": "No transactions found in JSON."}


def parse_passbook(user_id, json_file=None):
    parser = PassbookParser()
    result_basic = parser.parse_json_to_csv(user_id, json_file)
    result_structured = parser.parse_json_to_structured_csv(user_id, json_file)
    return {
        "basic_csv": result_basic,
        "structured_csv": result_structured
    }


if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    result = parse_passbook(user_id)
    print(json.dumps(result, indent=2))
