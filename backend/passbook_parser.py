from typing import List, Dict, Optional


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
    table_count: Dict[int, int] = {}

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
                if bt in ("WORD", "LINE"):
                    parts.append(child.get("Text", ""))
                elif bt == "SELECTION_ELEMENT":
                    parts.append("☑" if child.get("SelectionStatus") == "SELECTED" else "☐")
    return " ".join([p for p in parts if p])


def build_passbook_summary(blocks: List[dict], kv_pairs: List[List[object]]) -> dict:
    """Build a clean summary of common passbook fields."""
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

    account_number = first_match(["account no", "a/c no", "ac no", "account number"])
    cif_number = first_match(["cif", "cif no"])
    customer_name = first_match(["customer name", "account holder", "name"])
    ifsc = first_match(["ifsc", "ifsc code"])
    branch = first_match(["branch", "branch name"])
    branch_code = first_match(["branch code"])
    address = first_match(["address"])
    phone = first_match(["phone", "mobile"])
    email = first_match(["email", "e-mail"])
    date_of_issue = first_match(["date of issue", "date of opening", "date"])

    lines = [b.get("Text", "") for b in blocks if b.get("BlockType") == "LINE"]

    bank_name = None
    for t in lines:
        if "bank" in t.lower():
            bank_name = t.strip()
            break

    if not ifsc:
        for t in lines:
            tokens = t.replace(":", " ").replace(",", " ").split()
            for tok in tokens:
                tok = tok.strip()
                if len(tok) == 11 and tok.isalnum() and tok[:4].isalpha():
                    if ifsc is None:
                        ifsc = tok
                    if tok[4] == "0":
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
    return {k: v for k, v in summary.items() if v}
