import json
from fastlog_py import compress_json_raw, decompress_json_raw

def compress_json(events):
    raw = json.dumps(events).encode()
    return compress_json_raw(raw)

def decompress_json(blob):
    raw = decompress_json_raw(blob)
    return json.loads(raw.decode())

