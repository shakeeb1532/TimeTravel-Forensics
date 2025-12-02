use std::sync::atomic::{AtomicUsize, Ordering};
use std::ptr;

pub struct RingBuffer {
    buf: Vec<u8>,
    size: usize,
    write_idx: AtomicUsize,
}

impl RingBuffer {
    pub fn new(capacity: usize) -> Self {
        Self {
            buf: vec![0; capacity],
            size: capacity,
            write_idx: AtomicUsize::new(0),
        }
    }

    #[inline(always)]
    pub fn push(&self, data: &[u8]) {
        let mut idx = self.write_idx.load(Ordering::Relaxed);

        for &b in data {
            unsafe {
                *self.buf.as_ptr().add(idx) as *mut u8 = b;
            }

            idx = (idx + 1) % self.size;
        }

        self.write_idx.store(idx, Ordering::Relaxed);
    }

    pub fn snapshot_raw(&self) -> &[u8] {
        let idx = self.write_idx.load(Ordering::Relaxed);
        let (a, b) = self.buf.split_at(idx);
        unsafe {
            let mut out = Vec::with_capacity(self.size);
            out.extend_from_slice(b);
            out.extend_from_slice(a);
            Box::leak(out.into_boxed_slice())
        }
    }
}
