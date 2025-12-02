#!/usr/bin/env python3
import time
import random
import json
import gzip
import lzma
import zlib
from statistics import mean

from ttfr_fastlog import compress_json, decompress_json
from ttfr_fastlog import RingBuffer   # if not exposed yet, can comment out


# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------
def hr(bytes_val):
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} TB"


def banner(title):
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)


# ------------------------------------------------------------
# 1. Compression Benchmark
# ------------------------------------------------------------
def bench_compression(events):
    input_json = json.dumps(events).encode()

    results = {}

    # Fastlog
    t0 = time.time()
    blob = compress_json(events)
    t1 = time.time()

    results["fastlog"] = {
        "size": len(blob),
        "ratio": len(blob) / len(input_json),
        "latency": t1 - t0,
    }

    # gzip
    t0 = time.time()
    gz = gzip.compress(input_json)
    t1 = time.time()
    results["gzip"] = {
        "size": len(gz),
        "ratio": len(gz) / len(input_json),
        "latency": t1 - t0,
    }

    # zlib
    t0 = time.time()
    zb = zlib.compress(input_json)
    t1 = time.time()
    results["zlib"] = {
        "size": len(zb),
        "ratio": len(zb) / len(input_json),
        "latency": t1 - t0,
    }

    # lzma
    t0 = time.time()
    xm = lzma.compress(input_json)
    t1 = time.time()
    results["lzma"] = {
        "size": len(xm),
        "ratio": len(xm) / len(input_json),
        "latency": t1 - t0,
    }

    return results


# ------------------------------------------------------------
# 2. Decode Benchmark
# ------------------------------------------------------------
def bench_decode(blob, trials=20):
    times = []
    for _ in range(trials):
        t0 = time.time()
        _ = decompress_json(blob)
        t1 = time.time()
        times.append(t1 - t0)

    return {
        "avg_latency": mean(times),
        "worst": max(times),
        "best": min(times)
    }


# ------------------------------------------------------------
# 3. RingBuffer ingest throughput test
# ------------------------------------------------------------
def bench_ingest():
    try:
        rb = RingBuffer(100 * 1024 * 1024)  # 100 MB buffer
    except Exception:
        print("RingBuffer not available, skipping ingest test")
        return None

    payload = b"A" * 512

    count = 0
    t0 = time.time()
    end_time = t0 + 3  # run for 3 seconds

    while time.time() < end_time:
        rb.push(payload)
        count += 1

    total_bytes = count * len(payload)
    throughput_mb = total_bytes / (1024 * 1024)
    eps = count / 3

    return {
        "events": count,
        "event_rate": eps,
        "mb_rate": throughput_mb / 3,
        "snapshot_size": len(rb.snapshot_raw()),
    }


# ------------------------------------------------------------
# 4. Snapshot + Flush benchmark
# ------------------------------------------------------------
def bench_snapshot():
    try:
        rb = RingBuffer(50 * 1024 * 1024)
    except:
        print("No RingBuffer, skipping snapshot test")
        return None

    # fill buffer
    for _ in range(50000):
        rb.push(b"event-log-line")

    t0 = time.time()
    snap = rb.snapshot_raw()
    t1 = time.time()

    return {
        "snapshot_bytes": len(snap),
        "latency": t1 - t0,
    }


# ------------------------------------------------------------
# 5. MITRE ATT&CK replay test
# ------------------------------------------------------------
def bench_mitre_replay():
    # simple MITRE pattern simulation
    events = []
    for i in range(2000):
        if i % 300 == 0:
            msg = "MALWARE_BEACON_C2"
        elif i % 500 == 0:
            msg = "CREDENTIAL_SPRAY"
        else:
            msg = "OK"
        events.append({"ts": i, "msg": msg})

    # compress/decompress cycle
    blob = compress_json(events)
    decoded = decompress_json(blob)

    # detection quality check
    attacks = sum(1 for e in decoded if "MALWARE" in e["msg"] or "CRED" in e["msg"])

    return {
        "attacks_detected": attacks,
        "total_events": len(decoded),
        "blob_size": len(blob),
    }


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":

    # Generate synthetic log events
    test_events = [
        {"ts": i, "msg": f"event_{i}_value_{random.randint(1,999)}"}
        for i in range(5000)
    ]

    banner("1. Compression Benchmark")
    comp_results = bench_compression(test_events)
    for k, v in comp_results.items():
        print(f"{k}: size={hr(v['size'])}, ratio={v['ratio']:.3f}, latency={v['latency']*1000:.3f} ms")

    banner("2. Decode Benchmark")
    blob = compress_json(test_events)
    dec_results = bench_decode(blob)
    print(dec_results)

    banner("3. Ingest Throughput Benchmark")
    ingest = bench_ingest()
    print( ingest if ingest else "Skipped" )

    banner("4. Snapshot/Flush Benchmark")
    snap = bench_snapshot()
    print( snap if snap else "Skipped" )

    banner("5. MITRE ATT&CK Replay Benchmark")
    mitre = bench_mitre_replay()
    print(mitre)

    banner("SUMMARY")
    print(json.dumps({
        "compression": comp_results,
        "decode": dec_results,
        "ingest": ingest,
        "snapshot": snap,
        "mitre": mitre
    }, indent=4))

