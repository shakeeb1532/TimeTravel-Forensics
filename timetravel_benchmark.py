import json
import os
import time
import random
from fastlog_py import compress_json, decompress_json

print("\n============================")
print(" FASTLOG — FULL BENCHMARK")
print("============================\n")

SIZES = [1_000, 10_000, 50_000, 100_000, 250_000]   # number of events
RESULTS = []

for n in SIZES:
    print(f"\n--- Testing {n} JSON events ---")

    # Generate sample events
    events = []
    for i in range(n):
        events.append({
            "ts": i,
            "msg": f"hello {i}",
            "level": random.choice(["INFO", "WARN", "DEBUG"]),
            "user": random.randint(1, 99999),
            "value": random.random()
        })

    # Compress test
    t1 = time.time()
    blob = compress_json(events)
    t2 = time.time()

    # Decompress test
    restored = decompress_json(blob)
    t3 = time.time()

    # Verify correctness
    ok = restored == events

    RESULTS.append({
        "events": n,
        "raw_size": len(json.dumps(events)),
        "compressed_size": len(blob),
        "ratio": len(blob) / len(json.dumps(events)),
        "compress_ms": round((t2 - t1) * 1000, 2),
        "decompress_ms": round((t3 - t2) * 1000, 2),
        "correct": ok
    })

    print(f"Compressed size: {len(blob)} bytes")
    print(f"Compression time: {round((t2 - t1)*1000,2)} ms")
    print(f"Decompression time: {round((t3 - t2)*1000,2)} ms")
    print(f"Validation: {'OK' if ok else 'FAIL'}")


print("\n============================")
print(" BENCHMARK RESULTS SUMMARY")
print("============================")
for r in RESULTS:
    print(f"{r['events']:>7} events | {r['raw_size']:>8} → {r['compressed_size']:>8} bytes "
          f"| ratio {r['ratio']:.2f} | C={r['compress_ms']}ms D={r['decompress_ms']}ms | {'OK' if r['correct'] else 'FAIL'}")

