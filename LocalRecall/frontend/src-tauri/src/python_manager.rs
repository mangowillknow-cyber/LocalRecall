use std::process::{Child, Command};
use std::sync::Mutex;

pub struct PythonManager {
    child: Mutex<Option<Child>>,
    port: u16,
}

impl PythonManager {
    pub fn new(port: u16) -> Self {
        Self {
            child: Mutex::new(None),
            port,
        }
    }

    pub fn start(&self) -> Result<(), String> {
        let python = self.find_python();

        // Determine backend directory relative to the executable
        // Exe is at: <project>/frontend/src-tauri/target/debug/localrecall.exe
        // Backend is at: <project>/backend
        let exe_dir = std::env::current_exe()
            .map_err(|e| format!("Failed to get exe path: {}", e))?;
        let project_root = exe_dir
            .parent().ok_or("no exe parent")?  // debug/
            .parent().ok_or("no debug parent")?  // target/
            .parent().ok_or("no target parent")?  // src-tauri/
            .parent().ok_or("no src-tauri parent")?;  // frontend/
        let backend_dir = project_root.parent()
            .ok_or("no project root")?
            .join("backend");

        if !backend_dir.exists() {
            return Err(format!("Backend directory not found: {}", backend_dir.display()));
        }

        let child = Command::new(&python)
            .args([
                "-m", "uvicorn", "app.main:app",
                "--host", "127.0.0.1",
                "--port", &self.port.to_string(),
            ])
            .current_dir(&backend_dir)
            .spawn()
            .map_err(|e| format!("Failed to start Python: {}", e))?;

        *self.child.lock().unwrap() = Some(child);
        Ok(())
    }

    pub fn stop(&self) {
        if let Some(mut child) = self.child.lock().unwrap().take() {
            let _ = child.kill();
        }
    }

    fn find_python(&self) -> String {
        for name in &["python", "python3", "py"] {
            if Command::new(name).arg("--version").output().is_ok() {
                return name.to_string();
            }
        }
        "python".to_string()
    }
}
