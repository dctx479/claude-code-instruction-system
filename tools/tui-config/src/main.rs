//! Taiyi TUI Config - Interactive Configuration Tool
//!
//! A terminal user interface for configuring the Taiyi Meta-System.
//! Features:
//! - Real-time preview of configuration changes
//! - Visual editing of Agent definitions
//! - Theme selector with live preview
//! - Keyboard shortcuts help panel

mod ui;
mod preview;
mod config;
mod state;

use anyhow::Result;
use clap::Parser;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyModifiers},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    Terminal,
};
use std::io;
use std::path::PathBuf;
use std::time::Duration;

use crate::state::AppState;
use crate::ui::render_ui;

/// Taiyi TUI Configuration Tool
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to Taiyi root directory
    #[arg(short, long, default_value = ".")]
    path: PathBuf,

    /// Initial tab to display
    #[arg(short, long, default_value = "overview")]
    tab: String,

    /// Watch for file changes
    #[arg(short, long, default_value = "true")]
    watch: bool,

    /// Theme to use (default, minimal, nerd)
    #[arg(long, default_value = "default")]
    theme: String,
}

fn main() -> Result<()> {
    // Parse command line arguments
    let args = Args::parse();

    // Setup logging
    tracing_subscriber::fmt::init();

    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app state
    let mut app = AppState::new(args.path.clone(), args.theme)?;

    // Main loop
    let res = run_app(&mut terminal, &mut app);

    // Restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    // Handle errors
    if let Err(err) = res {
        eprintln!("Error: {err:?}");
        return Err(err);
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    app: &mut AppState,
) -> Result<()> {
    loop {
        // Draw UI
        terminal.draw(|f| render_ui(f, app))?;

        // Handle events with timeout for file watching
        if event::poll(Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                match (key.modifiers, key.code) {
                    // Quit
                    (KeyModifiers::CONTROL, KeyCode::Char('c')) |
                    (KeyModifiers::NONE, KeyCode::Char('q')) => {
                        return Ok(());
                    }

                    // Tab navigation
                    (KeyModifiers::NONE, KeyCode::Tab) => {
                        app.next_tab();
                    }
                    (KeyModifiers::SHIFT, KeyCode::BackTab) => {
                        app.prev_tab();
                    }

                    // Number keys for direct tab access
                    (KeyModifiers::NONE, KeyCode::Char('1')) => app.select_tab(0),
                    (KeyModifiers::NONE, KeyCode::Char('2')) => app.select_tab(1),
                    (KeyModifiers::NONE, KeyCode::Char('3')) => app.select_tab(2),
                    (KeyModifiers::NONE, KeyCode::Char('4')) => app.select_tab(3),
                    (KeyModifiers::NONE, KeyCode::Char('5')) => app.select_tab(4),

                    // Navigation
                    (KeyModifiers::NONE, KeyCode::Up) |
                    (KeyModifiers::NONE, KeyCode::Char('k')) => {
                        app.move_up();
                    }
                    (KeyModifiers::NONE, KeyCode::Down) |
                    (KeyModifiers::NONE, KeyCode::Char('j')) => {
                        app.move_down();
                    }
                    (KeyModifiers::NONE, KeyCode::Left) |
                    (KeyModifiers::NONE, KeyCode::Char('h')) => {
                        app.move_left();
                    }
                    (KeyModifiers::NONE, KeyCode::Right) |
                    (KeyModifiers::NONE, KeyCode::Char('l')) => {
                        app.move_right();
                    }

                    // Enter to select/edit
                    (KeyModifiers::NONE, KeyCode::Enter) => {
                        app.select_item();
                    }

                    // Escape to go back
                    (KeyModifiers::NONE, KeyCode::Esc) => {
                        app.go_back();
                    }

                    // Help
                    (KeyModifiers::NONE, KeyCode::Char('?')) => {
                        app.toggle_help();
                    }

                    // Search
                    (KeyModifiers::NONE, KeyCode::Char('/')) => {
                        app.start_search();
                    }

                    // Refresh
                    (KeyModifiers::NONE, KeyCode::Char('r')) => {
                        app.refresh()?;
                    }

                    // Save
                    (KeyModifiers::CONTROL, KeyCode::Char('s')) => {
                        app.save()?;
                    }

                    // Theme cycling
                    (KeyModifiers::NONE, KeyCode::Char('t')) => {
                        app.cycle_theme();
                    }

                    _ => {}
                }
            }
        }

        // Check for file changes if watching is enabled
        app.check_file_changes()?;
    }
}
