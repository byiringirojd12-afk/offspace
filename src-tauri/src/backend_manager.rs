use serde::Deserialize;
use std::io::{self, Read, Write};
use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, Command, ExitStatus, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use tauri::Manager;

const HEALTH_ADDRESS: &str = "127.0.0.1:8000";
const STARTUP_TIMEOUT: Duration = Duration::from_secs(30);
const SHUTDOWN_GRACE_PERIOD: Duration = Duration::from_secs(5);
const SHUTDOWN_FORCE_WAIT: Duration = Duration::from_secs(2);
const POLL_INTERVAL: Duration = Duration::from_millis(100);
const SHUTDOWN_COMMAND: &str = "OFFSPACE_SHUTDOWN";

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum BackendState {
    Starting,
    Ready,
    Failed,
    External,
}

#[derive(Deserialize)]
struct HealthResponse {
    status: String,
    database: String,
    version: String,
}

struct ManagedProcess {
    child: Child,
    shutdown_input: Option<ChildStdin>,
    data_dir: PathBuf,
}

impl ManagedProcess {
    fn new(mut child: Child, data_dir: PathBuf) -> Self {
        Self {
            shutdown_input: child.stdin.take(),
            child,
            data_dir,
        }
    }
}

pub struct BackendManager {
    state: Mutex<BackendState>,
    process: Mutex<Option<ManagedProcess>>,
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

        append_backend_log(&data_dir, "Starting OFFSPACE backend");
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

        *self.process.lock().unwrap() = Some(ManagedProcess::new(child, data_dir.clone()));

        let readiness = {
            let mut process = self.process.lock().unwrap();
            match process.as_mut() {
                Some(process) => wait_for_readiness(process, STARTUP_TIMEOUT, Self::is_ready),
                None => Err(StartupFailure::ProcessCheck(io::Error::new(
                    io::ErrorKind::Other,
                    "backend process tracking was lost during startup",
                ))),
            }
        };

        match readiness {
            Ok(()) => {
                *self.state.lock().unwrap() = BackendState::Ready;
                append_backend_log(&data_dir, "OFFSPACE backend readiness check succeeded");
            }
            Err(StartupFailure::Exited(status)) => {
                *self.state.lock().unwrap() = BackendState::Failed;
                let _ = self.process.lock().unwrap().take();
                append_backend_log(
                    &data_dir,
                    &format!("OFFSPACE backend exited before becoming ready: {status}"),
                );
                eprintln!("OFFSPACE backend exited before becoming ready: {status}");
            }
            Err(StartupFailure::Timeout) => {
                *self.state.lock().unwrap() = BackendState::Failed;
                append_backend_log(
                    &data_dir,
                    "Backend did not return a healthy response within 30 seconds",
                );
                if let Some(mut process) = self.process.lock().unwrap().take() {
                    stop_owned_process(&mut process, SHUTDOWN_GRACE_PERIOD);
                }
            }
            Err(StartupFailure::ProcessCheck(error)) => {
                *self.state.lock().unwrap() = BackendState::Failed;
                append_backend_log(
                    &data_dir,
                    &format!("Unable to check OFFSPACE backend startup: {error}"),
                );
                eprintln!("Unable to check OFFSPACE backend startup: {error}");
                if let Some(mut process) = self.process.lock().unwrap().take() {
                    stop_owned_process(&mut process, SHUTDOWN_GRACE_PERIOD);
                }
            }
        }
    }

    fn spawn_backend(data_dir: &Path, sidecar: Option<&Path>) -> io::Result<Child> {
        if let Some(sidecar) = sidecar.filter(|path| path.is_file()) {
            return Self::spawn_packaged_backend(data_dir, sidecar);
        }

        #[cfg(not(debug_assertions))]
        {
            return Self::spawn_packaged_backend(data_dir, require_packaged_backend(sidecar)?);
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
                .env("OFFSPACE_DATABASE_URL", database_url_for_data_dir(data_dir))
                .stdin(Stdio::piped())
                .stdout(Stdio::inherit())
                .stderr(Stdio::inherit())
                .spawn()
        }
    }

    fn spawn_packaged_backend(data_dir: &Path, sidecar: &Path) -> io::Result<Child> {
        let log = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(data_dir.join("backend.log"))?;
        let error_log = log.try_clone()?;
        Command::new(sidecar)
            .current_dir(data_dir)
            .env("OFFSPACE_DATABASE_URL", database_url_for_data_dir(data_dir))
            .stdin(Stdio::piped())
            .stdout(Stdio::from(log))
            .stderr(Stdio::from(error_log))
            .spawn()
    }

    fn is_ready() -> bool {
        Self::is_health_ready(HEALTH_ADDRESS)
    }

    fn is_health_ready(address: &str) -> bool {
        let Ok(address) = address.parse() else {
            return false;
        };
        let Ok(mut stream) = TcpStream::connect_timeout(&address, Duration::from_millis(200))
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
        let Some((headers, body)) = response.split_once("\r\n\r\n") else {
            return false;
        };
        let status_is_ok = headers
            .lines()
            .next()
            .and_then(|line| line.split_whitespace().nth(1))
            == Some("200");
        if !status_is_ok {
            return false;
        }

        serde_json::from_str::<HealthResponse>(body)
            .map(|health| {
                health.status == "online"
                    && health.database == "connected"
                    && !health.version.trim().is_empty()
            })
            .unwrap_or(false)
    }

    pub fn stop(&self) {
        if let Some(mut process) = self.process.lock().unwrap().take() {
            stop_owned_process(&mut process, SHUTDOWN_GRACE_PERIOD);
        }
    }
}

fn database_url_for_data_dir(data_dir: &Path) -> String {
    let database_path = data_dir
        .join("offspace.db")
        .to_string_lossy()
        .replace('\\', "/");
    format!("sqlite:///{database_path}")
}

#[allow(dead_code)]
fn require_packaged_backend(sidecar: Option<&Path>) -> io::Result<&Path> {
    sidecar.filter(|path| path.is_file()).ok_or_else(|| {
        io::Error::new(
            io::ErrorKind::NotFound,
            "The packaged OFFSPACE backend resource is missing; rebuild the installer",
        )
    })
}

fn append_backend_log(data_dir: &Path, message: &str) {
    let result = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(data_dir.join("backend.log"))
        .and_then(|mut log| writeln!(log, "{message}"));
    if let Err(error) = result {
        eprintln!("Unable to write OFFSPACE backend log: {error}");
    }
}

enum StartupFailure {
    Exited(ExitStatus),
    Timeout,
    ProcessCheck(io::Error),
}

fn wait_for_readiness(
    process: &mut ManagedProcess,
    timeout: Duration,
    mut health_check: impl FnMut() -> bool,
) -> Result<(), StartupFailure> {
    let deadline = Instant::now() + timeout;
    loop {
        match process.child.try_wait() {
            Ok(Some(status)) => return Err(StartupFailure::Exited(status)),
            Ok(None) => {}
            Err(error) => return Err(StartupFailure::ProcessCheck(error)),
        }

        if health_check() {
            return Ok(());
        }
        let now = Instant::now();
        if now >= deadline {
            return Err(StartupFailure::Timeout);
        }
        thread::sleep(POLL_INTERVAL.min(deadline - now));
    }
}

fn wait_for_child_exit(child: &mut Child, timeout: Duration) -> io::Result<Option<ExitStatus>> {
    let deadline = Instant::now() + timeout;
    loop {
        if let Some(status) = child.try_wait()? {
            return Ok(Some(status));
        }
        let now = Instant::now();
        if now >= deadline {
            return Ok(None);
        }
        thread::sleep(POLL_INTERVAL.min(deadline - now));
    }
}

fn stop_owned_process(process: &mut ManagedProcess, grace_period: Duration) {
    match process.child.try_wait() {
        Ok(Some(status)) => {
            append_backend_log(
                &process.data_dir,
                &format!("OFFSPACE backend had already exited: {status}"),
            );
            return;
        }
        Ok(None) => {}
        Err(error) => append_backend_log(
            &process.data_dir,
            &format!("Unable to inspect OFFSPACE backend before shutdown: {error}"),
        ),
    }

    append_backend_log(
        &process.data_dir,
        "Requesting graceful OFFSPACE backend shutdown",
    );
    if let Some(mut input) = process.shutdown_input.take() {
        if let Err(error) = writeln!(input, "{SHUTDOWN_COMMAND}").and_then(|_| input.flush()) {
            append_backend_log(
                &process.data_dir,
                &format!("Unable to send backend shutdown request: {error}"),
            );
        }
    } else {
        append_backend_log(
            &process.data_dir,
            "Backend shutdown control pipe is unavailable",
        );
    }

    match wait_for_child_exit(&mut process.child, grace_period) {
        Ok(Some(status)) => {
            append_backend_log(
                &process.data_dir,
                &format!("OFFSPACE backend shut down gracefully: {status}"),
            );
            return;
        }
        Ok(None) => append_backend_log(
            &process.data_dir,
            "Graceful backend shutdown timed out; terminating the OFFSPACE-owned process tree",
        ),
        Err(error) => append_backend_log(
            &process.data_dir,
            &format!("Unable to wait for graceful backend shutdown: {error}"),
        ),
    }

    if let Err(error) = force_terminate_owned_tree(&mut process.child) {
        append_backend_log(
            &process.data_dir,
            &format!("Unable to terminate OFFSPACE-owned backend process tree: {error}"),
        );
    }

    match wait_for_child_exit(&mut process.child, SHUTDOWN_FORCE_WAIT) {
        Ok(Some(status)) => append_backend_log(
            &process.data_dir,
            &format!("OFFSPACE backend process tree terminated: {status}"),
        ),
        Ok(None) => append_backend_log(
            &process.data_dir,
            "OFFSPACE backend process exit was not confirmed after forced cleanup",
        ),
        Err(error) => append_backend_log(
            &process.data_dir,
            &format!("Unable to confirm OFFSPACE backend process exit: {error}"),
        ),
    }
}

#[cfg(target_os = "windows")]
fn force_terminate_owned_tree(child: &mut Child) -> io::Result<()> {
    let status = Command::new("taskkill")
        .args(["/PID", &child.id().to_string(), "/T", "/F"])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()?;
    if status.success() {
        Ok(())
    } else {
        Err(io::Error::new(
            io::ErrorKind::Other,
            format!("taskkill exited with {status}"),
        ))
    }
}

#[cfg(not(target_os = "windows"))]
fn force_terminate_owned_tree(child: &mut Child) -> io::Result<()> {
    child.kill()
}

impl Drop for BackendManager {
    fn drop(&mut self) {
        if let Some(mut process) = self.process.get_mut().unwrap().take() {
            stop_owned_process(&mut process, SHUTDOWN_GRACE_PERIOD);
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
    use super::{
        database_url_for_data_dir, require_packaged_backend, stop_owned_process,
        wait_for_readiness, BackendManager, ManagedProcess, StartupFailure, SHUTDOWN_COMMAND,
    };
    use std::fs;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::path::{Path, PathBuf};
    use std::process::{Command, Stdio};
    use std::thread;
    use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

    fn health_response(body: &str) -> (String, thread::JoinHandle<()>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let address = listener.local_addr().unwrap().to_string();
        let body = body.to_owned();
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            let mut request = [0; 128];
            let _ = stream.read(&mut request);
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            )
            .unwrap();
        });
        (address, server)
    }

    fn temporary_data_dir() -> PathBuf {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let directory = std::env::temp_dir().join(format!(
            "offspace-backend-lifecycle-{}-{unique}",
            std::process::id()
        ));
        fs::create_dir_all(&directory).unwrap();
        directory
    }

    fn spawn_fixture(mode: &str, data_dir: &Path) -> ManagedProcess {
        let child = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "backend_manager::tests::managed_child_fixture",
                "--nocapture",
            ])
            .env("OFFSPACE_TEST_CHILD_MODE", mode)
            .env("OFFSPACE_TEST_PID_FILE", data_dir.join("descendant.pid"))
            .stdin(Stdio::piped())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .unwrap();
        ManagedProcess::new(child, data_dir.to_path_buf())
    }

    #[test]
    fn readiness_requires_database_and_version_health_fields() {
        let (address, server) =
            health_response(r#"{"status":"online","database":"connected","version":"1.0.0"}"#);
        assert!(BackendManager::is_health_ready(&address));
        server.join().unwrap();
    }

    #[test]
    fn readiness_rejects_generic_online_response() {
        let (address, server) = health_response(r#"{"status":"online"}"#);
        assert!(!BackendManager::is_health_ready(&address));
        server.join().unwrap();
    }

    #[test]
    fn readiness_rejects_non_health_listeners() {
        let (address, server) = health_response("not offspace");
        assert!(!BackendManager::is_health_ready(&address));
        server.join().unwrap();
    }

    #[test]
    fn packaged_database_url_uses_windows_absolute_path() {
        let data_dir = Path::new(r"C:\Users\Tester\AppData\Local\Offspace");
        assert_eq!(
            database_url_for_data_dir(data_dir),
            "sqlite:///C:/Users/Tester/AppData/Local/Offspace/offspace.db"
        );
    }

    #[test]
    fn missing_packaged_sidecar_returns_not_found() {
        let directory = temporary_data_dir();
        let missing = directory.join("missing-backend.exe");
        let error = require_packaged_backend(Some(&missing)).unwrap_err();
        assert_eq!(error.kind(), std::io::ErrorKind::NotFound);
        fs::remove_dir_all(directory).unwrap();
    }

    #[test]
    fn readiness_timeout_retains_process_for_graceful_cleanup() {
        let directory = temporary_data_dir();
        let mut process = spawn_fixture("graceful", &directory);
        let result = wait_for_readiness(&mut process, Duration::from_millis(150), || false);
        assert!(matches!(result, Err(StartupFailure::Timeout)));

        stop_owned_process(&mut process, Duration::from_secs(3));
        assert!(process.child.try_wait().unwrap().is_some());
        fs::remove_dir_all(directory).unwrap();
    }

    #[test]
    fn tracked_child_receives_graceful_shutdown_request() {
        let directory = temporary_data_dir();
        let mut process = spawn_fixture("graceful", &directory);
        stop_owned_process(&mut process, Duration::from_secs(3));
        assert!(process.child.try_wait().unwrap().is_some());
        fs::remove_dir_all(directory).unwrap();
    }

    #[cfg(target_os = "windows")]
    #[test]
    fn shutdown_fallback_terminates_only_the_owned_process_tree() {
        let directory = temporary_data_dir();
        let mut process = spawn_fixture("tree", &directory);
        let pid_file = directory.join("descendant.pid");
        let deadline = Instant::now() + Duration::from_secs(5);
        while !pid_file.is_file() && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(25));
        }
        assert!(pid_file.is_file(), "fixture did not start its descendant");
        let descendant_pid = fs::read_to_string(&pid_file)
            .unwrap()
            .parse::<u32>()
            .unwrap();

        stop_owned_process(&mut process, Duration::from_millis(100));
        assert!(process.child.try_wait().unwrap().is_some());
        let descendant_running = windows_process_exists(descendant_pid);
        if descendant_running {
            let _ = Command::new("taskkill")
                .args(["/PID", &descendant_pid.to_string(), "/T", "/F"])
                .stdin(Stdio::null())
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .status();
        }
        fs::remove_dir_all(&directory).unwrap();
        assert!(!descendant_running, "owned descendant remained running");
    }

    #[cfg(target_os = "windows")]
    fn windows_process_exists(pid: u32) -> bool {
        let output = Command::new("tasklist")
            .args(["/FI", &format!("PID eq {pid}"), "/FO", "CSV", "/NH"])
            .output()
            .unwrap();
        String::from_utf8_lossy(&output.stdout).contains(&format!(",\"{pid}\","))
    }

    #[test]
    fn managed_child_fixture() {
        match std::env::var("OFFSPACE_TEST_CHILD_MODE").as_deref() {
            Ok("graceful") => {
                let mut command = String::new();
                std::io::stdin().read_line(&mut command).unwrap();
                assert_eq!(command.trim(), SHUTDOWN_COMMAND);
            }
            Ok("tree") => {
                let pid_file = std::env::var_os("OFFSPACE_TEST_PID_FILE").unwrap();
                let child = Command::new(std::env::current_exe().unwrap())
                    .args([
                        "--exact",
                        "backend_manager::tests::managed_grandchild_fixture",
                        "--nocapture",
                    ])
                    .env("OFFSPACE_TEST_GRANDCHILD", "1")
                    .stdin(Stdio::null())
                    .stdout(Stdio::null())
                    .stderr(Stdio::null())
                    .spawn()
                    .unwrap();
                fs::write(pid_file, child.id().to_string()).unwrap();
                loop {
                    thread::sleep(Duration::from_secs(1));
                }
            }
            _ => {}
        }
    }

    #[test]
    fn managed_grandchild_fixture() {
        if std::env::var_os("OFFSPACE_TEST_GRANDCHILD").is_some() {
            loop {
                thread::sleep(Duration::from_secs(1));
            }
        }
    }
}
