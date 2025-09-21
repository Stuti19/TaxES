from typing import List, Dict, Optional


def extract_key_values(blocks: List[dict]) -> List[List[object]]:
    """[[Key, Value, Confidence], ...] using Textract KEY_VALUE_SET blocks."""
    id_map = {b.get("Id"): b for b in blocks if "Id" in b}
    out: List[List[object]] = []

    for b in blocks:
        if b.get("BlockType") == "KEY_VALUE_SET" and "KEY" in b.get("EntityTypes", []):
            key_text = _collect_text(b, id_map)

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

            val_text = _collect_text(value_block, id_map) if value_block else ""
            if key_text or val_text:
                key_conf = float(b.get("Confidence", 0.0) or 0.0)
                val_conf = float((value_block or {}).get("Confidence", 0.0) or 0.0)
                conf = round(min(key_conf, val_conf), 2)
                out.append([key_text.strip(), val_text.strip(), conf])

    out.sort(key=lambda r: (r[0] or "").lower())
    return out


def extract_table_cells(blocks: List[dict]) -> List[List[object]]:
    """[[Page, Table, Row, Column, Text, Confidence], ...]"""
    id_map = {b.get("Id"): b for b in blocks if "Id" in b}
    rows: List[List[object]] = []
    table_count: Dict[int, int] = {}

    for b in blocks:
        if b.get("BlockType") == "TABLE":
            page = b.get("Page")
            table_count[page] = table_count.get(page, 0) + 1
            t_idx = table_count[page]

            for rel in b.get("Relationships", []) or []:
                if rel.get("Type") == "CHILD":
                    for cid in rel.get("Ids", []):
                        cell = id_map.get(cid)
                        if not cell or cell.get("BlockType") != "CELL":
                            continue
                        text = _collect_text(cell, id_map)
                        conf = float(cell.get("Confidence", 0.0) or 0.0)
                        rows.append([
                            page, t_idx,
                            cell.get("RowIndex"),
                            cell.get("ColumnIndex"),
                            text.strip(),
                            round(conf, 2),
                        ])
    rows.sort(key=lambda r: (r[0] or 0, r[1], r[2], r[3]))
    return rows


def _collect_text(block: Optional[dict], id_map: Dict[str, dict]) -> str:
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
