use fastlog_core::RingBuffer;

#[test]
fn test_ringbuffer_overwrite() {
    let mut rb = RingBuffer::new(3);

    rb.push(vec![1]);
    rb.push(vec![2]);
    rb.push(vec![3]);

    // Now overwrite
    rb.push(vec![9]);

    let dump = rb.dump();

    assert_eq!(dump[0], vec![9]);
}

