mod fastlog;
mod ring_buffer;
mod trigger;

use lz4::block::{compress, decompress};

pub use fastlog::{fastlog_compress_json, fastlog_decompress_json, JsonEvent};
pub use ring_buffer::RingBuffer;
pub use trigger::trigger_flush;

pub fn compress_raw(data: &[u8]) -> Vec<u8> {
    compress(data, None, true).expect("LZ4 compression failed")
}

pub fn decompress_raw(data: &[u8]) -> Vec<u8> {
    decompress(data, None).expect("LZ4 decompress failed")
}

pub fn fastlog_compress(data: &[u8]) -> Vec<u8> {
    compress_raw(data)
}

pub fn fastlog_decompress(data: &[u8]) -> Vec<u8> {
    decompress_raw(data)
}
