use fastlog_core::trigger_flush;

#[test]
fn test_trigger_name() {
    let name = trigger_flush("malware test");
    assert!(name.contains("malware_test"));
    assert!(name.ends_with(".ttfr"));
}

