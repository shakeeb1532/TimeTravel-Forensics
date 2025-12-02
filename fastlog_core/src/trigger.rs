use chrono::Utc;

/// Generates automatic forensic filename
pub fn trigger_flush(reason: &str) -> String {
    let ts = Utc::now().format("%Y-%m-%d_%H-%M-%S");
    format!("flush_{}_{}.ttfr", reason.replace(" ", "_"), ts)
}

