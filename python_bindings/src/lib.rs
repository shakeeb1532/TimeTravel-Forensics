use lz4::block::{compress, decompress};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyfunction]
fn compress_json(py: Python<'_>, obj: &PyAny) -> PyResult<Vec<u8>> {
    let json = py.import("json")?;
    let json_str: String = json
        .call_method1("dumps", (obj,))?
        .extract()
        .map_err(|e| PyRuntimeError::new_err(format!("JSON encode error: {e}")))?;

    compress(json_str.as_bytes(), None, true)
        .map_err(|e| PyRuntimeError::new_err(format!("LZ4 compress error: {e}")))
}

#[pyfunction]
fn decompress_json(py: Python<'_>, data: &PyAny) -> PyResult<PyObject> {
    let bytes: Vec<u8> = data.extract()?;
    let decompressed = decompress(&bytes, None)
        .map_err(|e| PyRuntimeError::new_err(format!("LZ4 decompress error: {e}")))?;

    let json_str = String::from_utf8(decompressed)
        .map_err(|e| PyRuntimeError::new_err(format!("UTF-8 error: {e}")))?;

    let json = py.import("json")?;
    let obj = json
        .call_method1("loads", (json_str,))?
        .to_object(py);

    Ok(obj)
}

#[pymodule]
fn fastlog_py(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_json, m)?)?;
    m.add_function(wrap_pyfunction!(decompress_json, m)?)?;
    Ok(())
}
