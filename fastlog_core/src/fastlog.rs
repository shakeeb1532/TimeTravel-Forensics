use serde::{Serialize, Deserialize};
use lz4::block::{compress, decompress};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JsonEvent {
    pub ts: u64,
    pub msg: String,
}

pub fn fastlog_compress_json(events: &Vec<JsonEvent>) -> Vec<u8> {
    let encoded = serde_json::to_vec(events).unwrap();
    compress(&encoded, None, true).unwrap()
}

pub fn fastlog_decompress_json(data: &[u8]) -> Result<Vec<JsonEvent>, String> {
    let decompressed = decompress(data, None)
        .map_err(|e| format!("LZ4 error {}", e))?;
    serde_json::from_slice(&decompressed)
        .map_err(|e| format!("JSON error {}", e))
}
