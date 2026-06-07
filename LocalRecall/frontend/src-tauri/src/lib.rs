mod python_manager;

use python_manager::PythonManager;
use std::sync::OnceLock;

static PYTHON: OnceLock<PythonManager> = OnceLock::new();

#[tauri::command]
fn get_backend_url() -> String {
    "http://127.0.0.1:8420".to_string()
}

pub fn run() {
    let manager = PythonManager::new(8420);
    manager
        .start()
        .expect("Failed to start Python backend");
    let _ = PYTHON.set(manager);

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_backend_url])
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                if let Some(mgr) = PYTHON.get() {
                    mgr.stop();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error running tauri");
}
