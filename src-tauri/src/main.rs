#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend_manager;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let backend = backend_manager::BackendManager::default();
            backend.start(app.handle());
            app.manage(backend);
            Ok(())
        })
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::CloseRequested { .. }) {
                window.state::<backend_manager::BackendManager>().stop();
            }
        })
        .build(tauri::generate_context!())
        .expect("error while building OFFSPACE")
        .run(|app_handle, event| {
            if matches!(event, tauri::RunEvent::ExitRequested { .. } | tauri::RunEvent::Exit) {
                app_handle.state::<backend_manager::BackendManager>().stop();
            }
        });
}
