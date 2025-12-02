use fastlog_core::*;

#[test]
fn test_fastlog_roundtrip() {
    let input = b"The quick brown fox jumps over the lazy dog.";
    let compressed = fastlog_compress(input);
    let out = fastlog_decompress(&compressed);
    assert_eq!(input.to_vec(), out);
}

