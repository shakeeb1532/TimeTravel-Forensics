use fastlog_core::fastlog_decompress_json;
use lz4::block::compress;

#[test]
fn test_decompress_json_rejects_invalid_lz4() {
    let bogus = vec![0x00, 0x01, 0x02, 0x03, 0xFF];
    let out = fastlog_decompress_json(&bogus);
    assert!(out.is_err());
}

#[test]
fn test_decompress_json_rejects_invalid_json() {
    let raw = b"not json";
    let compressed = compress(raw, None, true).expect("lz4 compress");
    let out = fastlog_decompress_json(&compressed);
    assert!(out.is_err());
}
