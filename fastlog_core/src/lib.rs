use lz4::block::{compress, decompress};

pub fn compress_raw(data: &[u8]) -> Vec<u8> {
    compress(data, None, true).expect("LZ4 compression failed")
}

pub fn decompress_raw(data: &[u8]) -> Vec<u8> {
    decompress(data, None).expect("LZ4 decompress failed")
}

