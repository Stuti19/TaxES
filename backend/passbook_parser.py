# parser.py
"""
parser.py

Helper utilities for Textract outputs used by extractor.py

Provides:
- collect_text(blocks)
- extract_key_values(blocks) -> list of (Key, Value, Confidence)
- extract_table_cells(blocks) -> list of tuples (Page, TableIndex, Row, Column, Text, Confidence)
- build_passbook_summary(blocks, kv_pairs) -> dict
- put_csv(s3_client, bucket, key, headers, rows)
- put_json(s3_client, bucket, key, obj)
"""
import io
import json
import csv
from typing import List, Tuple, Dict, Any, Iterable
from collections import defaultdict

def collect_text(blocks: List[Dict[str, Any]]) -> Dict[str, str]:
    id_to_block = {b['Id']: b for b in blocks}
    text_map: Dict[str, str] = {}

    # Word/Line direct extraction
    for b in blocks:
        if b['BlockType'] in ('WORD', 'LINE'):
            text_map[b['Id']] = b.get('Text', '')

    # For blocks that have CHILD relationships, join children's text
    for b in blocks:
        if 'Relationships' not in b:
            continue
        parts = []
        for rel in b['Relationships']:
            if rel['Type'] == 'CHILD':
                for cid in rel.get('Ids', []):
                    child = id_to_block.get(cid)
                    if not child:
                        continue
                    if child.get('BlockType') in ('WORD', 'LINE'):
                        parts.append(child.get('Text', ''))
                    else:
                        # dive one level deeper
                        if 'Relationships' in child:
                            for crel in child['Relationships']:
                                if crel['Type'] == 'CHILD':
                                    for ccid in crel.get('Ids', []):
                                        cchild = id_to_block.get(ccid)
                                        if cchild and cchild.get('BlockType') in ('WORD', 'LINE'):
                                            parts.append(cchild.get('Text', ''))
        if parts:
            text_map[b['Id']] = ' '.join(parts).strip()

    return text_map

def extract_key_values(blocks: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
    id_map = {b['Id']: b for b in blocks}
    key_blocks = [b for b in blocks if b['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in b.get('EntityTypes', [])]
    value_blocks = {b['Id']: b for b in blocks if b['BlockType'] == 'KEY_VALUE_SET' and 'VALUE' in b.get('EntityTypes', [])}

    def get_text_from_block(block):
        texts = []
        for rel in block.get('Relationships', []) or []:
            if rel['Type'] == 'CHILD':
                for cid in rel.get('Ids', []):
                    child = id_map.get(cid)
                    if not child:
                        continue
                    if child.get('BlockType') in ('WORD', 'LINE'):
                        texts.append(child.get('Text', ''))
                    else:
                        for crel in child.get('Relationships', []) or []:
                            if crel['Type'] == 'CHILD':
                                for ccid in crel.get('Ids', []):
                                    cchild = id_map.get(ccid)
                                    if cchild and cchild.get('BlockType') in ('WORD', 'LINE'):
                                        texts.append(cchild.get('Text', ''))
        return ' '.join(texts).strip()

    kv_pairs = []
    for k in key_blocks:
        value_text = ''
        key_text = get_text_from_block(k) or k.get('Text', '')
        confidence = float(k.get('Confidence', 0.0))
        for rel in k.get('Relationships', []) or []:
            if rel['Type'] == 'VALUE':
                for vid in rel.get('Ids', []):
                    vblock = value_blocks.get(vid) or id_map.get(vid)
                    if not vblock:
                        continue
                    vtext = get_text_from_block(vblock) or vblock.get('Text', '')
                    if vtext:
                        if value_text:
                            value_text = value_text + ' | ' + vtext
                        else:
                            value_text = vtext
        kv_pairs.append((key_text, value_text, confidence))
    return kv_pairs

def extract_table_cells(blocks: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int, str, float]]:
    id_map = {b['Id']: b for b in blocks}
    tables = [b for b in blocks if b['BlockType'] == 'TABLE']
    results = []
    cell_map = {b['Id']: b for b in blocks if b['BlockType'] == 'CELL'}

    def get_text(block):
        texts = []
        for rel in block.get('Relationships', []) or []:
            if rel['Type'] == 'CHILD':
                for cid in rel.get('Ids', []):
                    child = id_map.get(cid)
                    if child and child.get('BlockType') in ('WORD', 'LINE'):
                        texts.append(child.get('Text', ''))
        return ' '.join(texts).strip()

    for t_index, table in enumerate(tables):
        page = table.get('Page', None)
        cell_ids = []
        for rel in table.get('Relationships', []) or []:
            if rel['Type'] in ('CHILD', 'CHILDREN'):
                cell_ids.extend(rel.get('Ids', []))
        if not cell_ids:
            # fallback: include cells which might belong to this table if they have Table attributes
            for cid, cblock in cell_map.items():
                # some Textract outputs don't label parent - keep them out unless obviously linked
                if cblock.get('Table', None) == t_index:
                    cell_ids.append(cid)

        for cid in cell_ids:
            cell = cell_map.get(cid)
            if not cell:
                continue
            row = int(cell.get('RowIndex', 0))
            col = int(cell.get('ColumnIndex', 0))
            conf = float(cell.get('Confidence', 0.0))
            text = get_text(cell)
            results.append((page, t_index + 1, row, col, text, conf))

    return results

def build_passbook_summary(blocks: List[Dict[str, Any]], kv_pairs: Iterable[Tuple[str, str, float]]) -> Dict[str, Any]:
    summary = {}
    kv_lower = [(k.lower() if k else '', v, c) for k, v, c in kv_pairs]

    def find_first(key_words):
        for k, v, c in kv_lower:
            for kw in key_words:
                if kw in k:
                    return v
        return None

    account_no = find_first(['account no', 'account number', 'account#', 'a/c no', 'a/c number', 'acc no'])
    holder = find_first(['name', 'account name', 'holder'])
    closing = find_first(['closing balance', 'closing bal', 'available balance', 'available bal', 'balance', 'total balance', 'current balance'])

    summary['account_number'] = account_no
    summary['account_holder'] = holder
    summary['closing_balance'] = closing
    summary['kv_count'] = sum(1 for _ in kv_pairs)

    recent_pairs = list(kv_pairs)[-5:]
    summary['recent_kv'] = [{'key': k, 'value': v, 'confidence': c} for k, v, c in recent_pairs]

    return summary

# S3 helpers
def put_csv(s3_client, bucket: str, key: str, headers: List[str], rows: Iterable[Tuple]):
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    if headers:
        writer.writerow(headers)

    # If rows is empty, just write header
    wrote_rows = False
    for r in rows:
        wrote_rows = True
        if isinstance(r, dict):
            writer.writerow([r.get(h, '') for h in headers])
        else:
            # ensure sequence
            writer.writerow([('' if c is None else c) for c in r])

    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    s3_client.put_object(Bucket=bucket, Key=key, Body=csv_bytes, ContentType='text/csv; charset=utf-8')

def put_json(s3_client, bucket: str, key: str, obj: Any):
    body = json.dumps(obj, ensure_ascii=False, indent=2).encode('utf-8')
    s3_client.put_object(Bucket=bucket, Key=key, Body=body, ContentType='application/json; charset=utf-8')
