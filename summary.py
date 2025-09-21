from typing import List, Dict, Optional


def build_passbook_summary(blocks: List[dict], kv_pairs: List[List[object]]) -> Dict[str, str]:
    """
    Create a simple summary from kv_pairs + line text.
    Fields: bank_name, account_number, cif_number, customer_name,
            ifsc, branch, branch_code, address, phone, email, date_of_issue
    No regex; only substring heuristics and token checks.
    """
    kv = {}
    for k, v, _c in kv_pairs:
        if k:
            kv[k.strip().lower()] = (v or "").strip()

    def first_match(needles: List[str]) -> Optional[str]:
        for needle in needles:
            for label, value in kv.items():
                if needle in label and value:
                    return value
        return None

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

    # Fallbacks from LINE blocks (for bank name & IFSC-like token)
    lines = [b.get("Text", "") for b in blocks if b.get("BlockType") == "LINE"]

    bank_name = None
    for t in lines:
        if "bank" in t.lower():
            bank_name = t.strip()
            break

    if not ifsc:
        for t in lines:
            for tok in t.replace(":", " ").replace(",", " ").split():
                tok = tok.strip()
                if len(tok) == 11 and tok.isalnum() and tok[:4].isalpha():
                    ifsc = tok if tok[4] == "0" else (ifsc or tok)
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
    return {k: v for k, v in summary.items() if v}
