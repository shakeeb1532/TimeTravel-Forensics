import json, time, gzip, zlib, lzma, os, statistics, tracemalloc, random
from ttfr_cli.engine import get_engine
import ttfr_fastlog


# -----------------------------------------------------------
# Utility for timing
# -----------------------------------------------------------
def bench(fn, *args, repeat=5):
    times = []
    for _ in range(repeat):
        t0 = time.time()
        fn(*args)
        times.append((time.time() - t0) * 1000)
    return {
        "p50_ms": round(statistics.median(times), 4),
        "p95_ms": round(statistics.quantiles(times, n=20)[-1], 4),
        "p99_ms": round(sorted(times)[int(0.99 * len(times))], 4),
        "samples": times
    }


# -----------------------------------------------------------
# 1 — Compression Research Test
# -----------------------------------------------------------
def test_compression():
    print("\n### COMPRESSION ANALYSIS ###")

    sample = "\n".join([f"log event {i} cpu=4% mem=18% msg=test"
                        for i in range(50000)]).encode()

    events = [{"ts": i, "msg": "hello world"} for i in range(50000)]
    json_raw = json.dumps(events).encode()

    results = {}

    # FASTLOG
    t0 = time.time()
    c_fast = ttfr_fastlog.compress_json(events)
    t_fast = (time.time() - t0) * 1000

    results["fastlog"] = {
        "raw_json": len(json_raw),
        "compressed": len(c_fast),
        "ratio": round(len(c_fast) / len(json_raw), 4),
        "latency_ms": round(t_fast, 4)
    }

    # gzip
    t0 = time.time()
    c_gz = gzip.compress(json_raw)
    results["gzip"] = {"compressed": len(c_gz),
                       "ratio": round(len(c_gz)/len(json_raw),4),
                       "latency_ms": round((time.time()-t0)*1000,4)}

    # zlib
    t0 = time.time()
    c_z = zlib.compress(json_raw)
    results["zlib"] = {"compressed": len(c_z),
                       "ratio": round(len(c_z)/len(json_raw),4),
                       "latency_ms": round((time.time()-t0)*1000,4)}

    # lzma
    t0 = time.time()
    c_l = lzma.compress(json_raw)
    results["lzma"] = {"compressed": len(c_l),
                       "ratio": round(len(c_l)/len(json_raw),4),
                       "latency_ms": round((time.time()-t0)*1000,4)}

    # Validate correctness
    restored = ttfr_fastlog.decompress_json(c_fast)
    results["fastlog_correct"] = restored == events

    print(json.dumps(results, indent=4))


# -----------------------------------------------------------
# 2 — Ingest Throughput Research Test
# -----------------------------------------------------------
def test_ingest():
    print("\n### INGEST THROUGHPUT ANALYSIS ###")
    engine = get_engine()

    message = b"cpu=3% net=14kb msg=heartbeat"
    size = len(message)

    # Measure event ingest rate
    t0 = time.time()
    for _ in range(1_000_000):
        engine.ingest(message)
    dt = time.time() - t0

    throughput_mb = (1_000_000 * size) / (1024*1024) / dt

    results = {
        "events": 1_000_000,
        "seconds": round(dt, 4),
        "events_per_sec": int(1_000_000 / dt),
        "mb_sec": round(throughput_mb, 2)
    }

    print(json.dumps(results, indent=4))


# -----------------------------------------------------------
# 3 — Snapshot Correctness / MITRE Replay
# -----------------------------------------------------------
def test_snapshot_correctness():
    print("\n### SNAPSHOT + MITRE T1059 REPLAY ###")
    engine = get_engine()
    engine.events.clear()

    # Create 200 simulated MITRE attack logs
    for _ in range(200):
        engine.ingest(b"ATTACK:T1059 PowerShell execution detected")

    snapshot = engine.dump_snapshot()

    restored = ttfr_fastlog.decompress_json(snapshot)
    ok = (len(restored) == 200)

    return {
        "snapshot_kb": round(len(snapshot)/1024, 3),
        "restored": len(restored),
        "expected": 200,
        "ok": ok
    }


# -----------------------------------------------------------
# 4 — Adversarial Input / Corruption Tests
# -----------------------------------------------------------
def test_adversarial():
    print("\n### ADVERSARIAL INPUT SAFETY ###")

    engine = get_engine()
    engine.events.clear()

    malformed_inputs = [
        b"",
        b"\x00\xff\x00\xff",
        b"!!!!@@@###",
        b"{not:json}",
        os.urandom(64),  # random binary
        b"\xF0\x9F\x92\xA9 BAD UTF8",
    ]

    results = {}

    for i, m in enumerate(malformed_inputs):
        try:
            engine.ingest(m)
            results[f"input_{i}"] = "accepted"
        except Exception as e:
            results[f"input_{i}"] = f"error: {e}"

    return results


# -----------------------------------------------------------
# 5 — Memory Profiling
# -----------------------------------------------------------
def test_memory_growth():
    print("\n### MEMORY GROWTH / LEAK CHECK ###")
    engine = get_engine()

    tracemalloc.start()

    for _ in range(300000):
        engine.ingest(b"cpu=4% mem=22% test")

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    biggest = top_stats[:5]

    result = []
    for stat in biggest:
        result.append(str(stat))

    return result


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------
if __name__ == "__main__":
    print("\n==============================")
    print("  FULL TTFR RESEARCH SUITE")
    print("==============================\n")

    test_compression()
    test_ingest()

    print("\n### MITRE Test ###")
    print(json.dumps(test_snapshot_correctness(), indent=4))

    print("\n### Adversarial Test ###")
    print(json.dumps(test_adversarial(), indent=4))

    print("\n### Memory Usage ###")
    print(json.dumps(test_memory_growth(), indent=4))

    print("\n=== Research Suite Complete ===")

