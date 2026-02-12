import fastlog_py


def main():
    data = [{"ts": 1, "msg": "hello"}]
    blob = fastlog_py.compress_json(data)
    out = fastlog_py.decompress_json(blob)
    assert out == data

    try:
        fastlog_py.decompress_json(b"not-lz4")
    except Exception:
        pass
    else:
        raise AssertionError("Expected decompress_json to fail on invalid LZ4")


if __name__ == "__main__":
    main()
