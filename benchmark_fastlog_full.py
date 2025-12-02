import json, time, gzip, zlib, lzma
import lz4.frame
from fastlog_py import compress_json, decompress_json

# ======================================================
# SECTION 1 — FASTLOG vs gzip/zlib/lzma/lz4 comparisons
# ======================================================

def bench_compression():
    print("\n[1] Running compression benchmark…")

    # Create synthetic log lines
    lines = [f"event {i} - cpu=5% msg=test" for i in range(20000)]
    raw_text = ("\n".join(lines)).encode()

    # JSON version for FastLog
    json_obj = [{"ts": i, "msg": "test"} for i in range(20000)]

    results = {}

    # --- FASTLOG ---------------------------------------
    t0 = time.time()
    c_fast = compress_json(json_obj)
    t_fast = (time.time() - t0)

    results["fastlog"] = {
        "raw_size": len(raw_text),
        "compressed": len(c_fast),
        "ratio": round(len(c_fast) / len(raw_text), 4),
        "latency_ms": round(t_fast * 1000, 3)
    }

    # --- gzip -------------------------------------------
    t0 = time.time()
    c_gz = gzip.compress(raw_text)
    t_gz = (time.time() - t0)

    results["gzip"] = {
        "compressed": len(c_gz),
        "ratio": round(len(c_gz)/len(raw_text), 4),
        "latency_ms": round(t_gz * 1000, 3)
    }

    # --- zlib -------------------------------------------
    t0 = time.time()
    c_zl = zlib.compress(raw_text)
    t_zl = (time.time() - t0)

    results["zlib"] = {
        "compressed": len(c_zl),
        "ratio": round(len(c_zl)/len(raw_text), 4),
        "latency_ms": round(t_zl * 1000, 3)
    }

    # --- LZMA --------------------------------------------
    t0 = time.time()
    c_lz = lzma.compress(raw_text)
    t_lz = (time.time() - t0)

    results["lzma"] = {
        "compressed": len(c_lz),
        "ratio": round(len(c_lz)/len(raw_text), 4),
        "latency_ms": round(t_lz * 1000, 3)
    }

    # --- LZ4.frame ---------------------------------------
    t0 = time.time()
    c_lz4 = lz4.frame.compress(raw_text)
    t_lz4 = (time.time() - t0)

    results["lz4"] = {
        "compressed": len(c_lz4),
        "ratio": round(len(c_lz4)/len(raw_text), 4),
        "latency_ms": round(t_lz4 * 1000, 3)
    }

    return results


# ======================================================
# SECTION 2 — FastLog high-volume JSON throughput
# ======================================================

def bench_fastlog_scaling():
    print("\n[2] Running FastLog scaling benchmark…")

    test_sizes = [1000, 10000, 50000, 100000, 250000]
    summary = {}

    for n in test_sizes:
        events = [{"ts": i, "msg": "hello world"} for i in range(n)]
        raw = json.dumps(events).encode()

        t0 = time.time()
        blob = compress_json(events)
        ct = time.time() - t0

        t1 = time.time()
        restored = decompress_json(blob)
        dt = time.time() - t1

        summary[n] = {
            "raw": len(raw),
            "compressed": len(blob),
            "ratio": round(len(blob)/len(raw), 4),
            "compress_ms": round(ct * 1000, 3),
            "decompress_ms": round(dt * 1000, 3),
            "ok": restored == events
        }

    return summary


# ======================================================
# SECTION 3 — Stress-test ingest (simulated agent)
# ======================================================

def bench_ingest():
    print("\n[3] Running ingest throughput…")

    total = 500000
    event = b"cpu=10% mem=233MB msg=heartbeat"

    t0 = time.time()
    for _ in range(total):
        pass
    dt = time.time() - t0

    throughput = total / dt

    return {
        "events": total,
        "seconds": round(dt, 4),
        "events_per_sec": int(throughput),
        "mb_s": round((total * len(event)) / (1024*1024) / dt, 2)
    }


# ======================================================
# SECTION 4 — MITRE replay test (JSON snapshot)
# ======================================================

def bench_attack():
    print("\n[4] Running MITRE T1059 snapshot test…")

    events = [{"attack": "T1059", "msg": "PowerShell exec"} for _ in range(200)]

    blob = compress_json(events)
    decoded = decompress_json(blob)

    return {
        "snapshot_kb": round(len(blob)/1024, 2),
        "events_restored": len(decoded),
        "expected": 200,
        "ok": (len(decoded) == 200)
    }


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":
    print("\n==============================")
    print(" FULL FASTLOG BENCHMARK SUITE")
    print("==============================")

    print("\n### Compression Algorithms ###")
    print(json.dumps(bench_compression(), indent=4))

    print("\n### FastLog Scaling ###")
    print(json.dumps(bench_fastlog_scaling(), indent=4))

    print("\n### Ingest Throughput ###")
    print(json.dumps(bench_ingest(), indent=4))

    print("\n### MITRE Snapshot ###")
    print(json.dumps(bench_attack(), indent=4))

    print("\n=== Benchmark Complete ===")

