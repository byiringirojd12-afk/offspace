use std::io::{self, Read, Write};
use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use tauri::Manager;

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum BackendState {
    Starting,
    Ready,
    Failed,
    External,
}

pub struct BackendManager {
    state: Mutex<BackendState>,
    process: Mutex<Option<Child>>,
}

impl Default for BackendManager {
    fn default() -> Self {
        Self {
            state: Mutex::new(BackendState::Starting),
            process: Mutex::new(None),
        }
    }
}

impl BackendManager {
    pub fn state(&self) -> BackendState {
        *self.state.lock().unwrap()
    }

    pub fn start(&self, app: &tauri::AppHandle) {
        if self.state() != BackendState::Starting {
            return;
        }

        if Self::is_ready() {
            *self.state.lock().unwrap() = BackendState::External;
            return;
        }

        let data_dir = tauri_app_data_dir();
        if let Err(error) = std::fs::create_dir_all(&data_dir) {
            *self.state.lock().unwrap() = BackendState::Failed;
            eprintln!("Unable to prepare OFFSPACE data directory: {error}");
            return;
        }

        let sidecar = app
            .path()
            .resolve("offspace-backend.exe", tauri::path::BaseDirectory::Resource)
            .ok();
        let child = match Self::spawn_backend(&data_dir, sidecar.as_deref()) {
            Ok(child) => child,
            Err(error) => {
                *self.state.lock().unwrap() = BackendState::Failed;
                append_backend_log(&data_dir, &format!("Backend startup failed: {error}"));
                eprintln!("Unable to start OFFSPACE backend: {error}");
                return;
            }
        };

        *self.process.lock().unwrap() = Some(child);

        let deadline = Instant::now() + Duration::from_secs(30);
        while Instant::now() < deadline {
            if Self::is_ready() {
                *self.state.lock().unwrap() = BackendState::Ready;
                return;
            }

            let early_exit = {
                let mut process = self.process.lock().unwrap();
                match process.as_mut() {
                    Some(child) => match child.try_wait() {
                        Ok(Some(status)) => Some(Ok(status)),
                        Err(error) => Some(Err(error)),
                        Ok(None) => None,
                    },
                    None => None,
                }
            };
            if let Some(result) = early_exit {
                *self.state.lock().unwrap() = BackendState::Failed;
                let _ = self.process.lock().unwrap().take();
                match result {
                    Ok(status) => eprintln!(
                        "OFFSPACE backend exited before becoming ready: {status}"
                    ),
                    Err(error) => eprintln!(
                        "Unable to check OFFSPACE backend startup: {error}"
                    ),
                }
                return;
            }
            thread::sleep(Duration::from_millis(150));
        }

        *self.state.lock().unwrap() = BackendState::Failed;
        if let Some(mut child) = self.process.lock().unwrap().take() {
            let _ = child.kill();
            let _ = child.wait();
        }
        append_backend_log(
            &data_dir,
            "Backend did not return a healthy response within 30 seconds",
        );
    }

    fn spawn_backend(data_dir: &Path, sidecar: Option<&Path>) -> io::Result<Child> {
        if let Some(sidecar) = sidecar.filter(|path| path.is_file()) {
            let log = std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(data_dir.join("backend.log"))?;
            let error_log = log.try_clone()?;
            return Command::new(sidecar)
                .current_dir(data_dir)
                .env(
                    "OFFSPACE_DATABASE_URL",
                    format!("sqlite:///{}", data_dir.join("offspace.db").display()),
                )
                .stdin(Stdio::null())
                .stdout(Stdio::from(log))
                .stderr(Stdio::from(error_log))
                .spawn();
        }

        #[cfg(not(debug_assertions))]
        {
            return Err(io::Error::new(
                io::ErrorKind::NotFound,
                "The packaged OFFSPACE backend resource is missing; rebuild the installer",
            ));
        }

        #[cfg(debug_assertions)]
        {
            let repository = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
            let python = repository.join(".venv").join("Scripts").join("python.exe");
            let python = if python.is_file() {
                python
            } else {
                PathBuf::from("python")
            };

            Command::new(python)
                .arg("-m")
                .arg("backend.main")
                .current_dir(repository)
                .env(
                    "OFFSPACE_DATABASE_URL",
                    format!("sqlite:///{}", data_dir.join("offspace.db").display()),
                )
                .stdin(Stdio::null())
                .stdout(Stdio::inherit())
                .stderr(Stdio::inherit())
                .spawn()
        }
    }

    fn is_ready() -> bool {
        Self::is_health_ready("127.0.0.1:8000")
    }

    fn is_health_ready(address: &str) -> bool {
        let Ok(address) = address.parse() else {
            return false;
        };
        let Ok(mut stream) =
            TcpStream::connect_timeout(&address, Duration::from_millis(200))
        else {
            return false;
        };
        let _ = stream.set_read_timeout(Some(Duration::from_secs(1)));
        if write!(
            stream,
            "GET /api/v1/health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
        )
        .is_err()
        {
            return false;
        }

        let mut response = String::new();
        if stream.read_to_string(&mut response).is_err() {
            return false;
        }
        response
            .lines()
            .next()
            .and_then(|line| line.split_whitespace().nth(1))
            == Some("200")
            && response.contains("\"status\":\"online\"")
    }

    pub fn stop(&self) {
        if let Some(mut child) = self.process.lock().unwrap().take() {
            stop_owned_process(&mut child);
            let _ = child.wait();
        }
    }
}

fn append_backend_log(data_dir: &Path, message: &str) {
    if let Ok(mut log) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(data_dir.join("backend.log"))
    {
        let _ = writeln!(log, "{message}");
    }
}

#[cfg(target_os = "windows")]
fn stop_owned_process(child: &mut Child) {
    let _ = Command::new("taskkill")
        .args(["/PID", &child.id().to_string(), "/T", "/F"])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    let _ = child.try_wait();
}

#[cfg(not(target_os = "windows"))]
fn stop_owned_process(child: &mut Child) {
    let _ = child.kill();
}

impl Drop for BackendManager {
    fn drop(&mut self) {
        if let Some(mut child) = self.process.get_mut().unwrap().take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

fn tauri_app_data_dir() -> PathBuf {
    std::env::var_os("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(std::env::temp_dir)
        .join("Offspace")
}

#[cfg(test)]
mod tests {
    use super::BackendManager;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;

    #[test]
    fn readiness_requires_successful_offspace_health_response() {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let address = listener.local_addr().unwrap().to_string();
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            let mut request = [0; 128];
            let _ = stream.read(&mut request);
            let body = r#"{"status":"online"}"#;
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            )
            .unwrap();
        });

        assert!(BackendManager::is_health_ready(&address));
        server.join().unwrap();
    }

    #[test]
    fn readiness_rejects_non_health_listeners() {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let address = listener.local_addr().unwrap().to_string();
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            let mut request = [0; 128];
            let _ = stream.read(&mut request);
            let body = "not offspace";
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            )
            .unwrap();
        });

        assert!(!BackendManager::is_health_ready(&address));
        server.join().unwrap();
    }
}
