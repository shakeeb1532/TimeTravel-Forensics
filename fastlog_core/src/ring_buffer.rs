use serde::{Serialize, Deserialize};
use chrono::Utc;

/// A ring buffer storing timestamped event blobs (Vec<u8>)
#[derive(Clone, Serialize, Deserialize)]
pub struct RingBuffer {
    pub buffer: Vec<Option<Vec<u8>>>,
    pub capacity: usize,
    pub write_index: usize,
    pub len: usize,
}

impl RingBuffer {
    pub fn new(capacity_bytes: usize) -> Self {
        // Approx event size: ~60 bytes → we store ~capacity_bytes / 64 events
        let capacity = (capacity_bytes / 64).max(1);

        RingBuffer {
            buffer: vec![None; capacity],
            capacity,
            write_index: 0,
            len: 0,
        }
    }

    /// Push a new event into the ring
    pub fn push(&mut self, data: Vec<u8>) {
        self.buffer[self.write_index] = Some(data);
        self.write_index = (self.write_index + 1) % self.capacity;
        self.len = self.len.saturating_add(1).min(self.capacity);
    }

    /// Return only USED entries (not full allocated space)
    pub fn dump(&self) -> Vec<Vec<u8>> {
        let used = self.len;
        let cap = self.capacity;

        let mut out = Vec::with_capacity(used);

        if used == 0 {
            return out;
        }

        // Oldest element location
        let start = if used < cap {
            0
        } else {
            (self.write_index + cap - used) % cap
        };

        for i in 0..used {
            let idx = (start + i) % cap;
            if let Some(ref entry) = self.buffer[idx] {
                out.push(entry.clone());
            }
        }

        out
    }

    /// Dump only telemetry from the last X seconds  
    /// (Assumes each event includes timestamp as first 8 bytes: u64 ms)
    pub fn dump_last_seconds(&self, seconds: u64) -> Vec<Vec<u8>> {
        let mut out = Vec::new();
        let now_ms = Utc::now().timestamp_millis();

        for entry in self.dump() {
            if entry.len() < 8 {
                continue;
            }

            // First 8 bytes store timestamp
            let ts_bytes = &entry[0..8];
            let ts = i64::from_le_bytes(ts_bytes.try_into().unwrap_or([0; 8]));

            if now_ms - ts < (seconds as i64 * 1000) {
                out.push(entry.clone());
            }
        }

        out
    }
}

