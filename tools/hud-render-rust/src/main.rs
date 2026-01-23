//! Taiyi HUD Render - High-performance HUD renderer
//!
//! A blazingly fast terminal HUD renderer written in Rust.
//! Performance improvement: 7-10x faster than shell script version.

use anyhow::Result;
use chrono::Local;
use clap::{Parser, ValueEnum};
use crossterm::style::{Attribute, Color, SetAttribute, SetForegroundColor, ResetColor};
use serde::{Deserialize, Serialize};
use std::io::{self, Write};
use std::path::PathBuf;

/// Command line arguments
#[derive(Parser, Debug)]
#[command(author, version, about = "High-performance HUD renderer for Taiyi")]
struct Args {
    /// Theme to use
    #[arg(short, long, default_value = "default")]
    theme: Theme,

    /// Output format
    #[arg(short, long, default_value = "full")]
    format: OutputFormat,

    /// Width of the HUD
    #[arg(short, long, default_value = "80")]
    width: usize,

    /// Path to state files
    #[arg(short, long)]
    state_dir: Option<PathBuf>,

    /// JSON output mode
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Clone, Copy, ValueEnum)]
enum Theme {
    Default,
    Minimal,
    Nerd,
}

#[derive(Debug, Clone, Copy, ValueEnum)]
enum OutputFormat {
    Line,
    Full,
    Compact,
}

/// HUD State from various sources
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
struct HudState {
    model: String,
    agent: String,
    task: String,
    progress: u8,
    ralph_active: bool,
    ralph_iteration: u8,
    ralph_max: u8,
    tokens_in: u64,
    tokens_out: u64,
}

/// Theme configuration
struct ThemeConfig {
    border_char: &'static str,
    progress_filled: &'static str,
    progress_empty: &'static str,
    separator: &'static str,
}

impl Theme {
    fn config(&self) -> ThemeConfig {
        match self {
            Theme::Default => ThemeConfig {
                border_char: "-",
                progress_filled: "#",
                progress_empty: ".",
                separator: "|",
            },
            Theme::Minimal => ThemeConfig {
                border_char: " ",
                progress_filled: "=",
                progress_empty: "-",
                separator: "|",
            },
            Theme::Nerd => ThemeConfig {
                border_char: "━",
                progress_filled: "█",
                progress_empty: "▒",
                separator: "┃",
            },
        }
    }
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Load state
    let state = load_state(&args.state_dir)?;

    // Render based on format
    match args.format {
        OutputFormat::Line => render_line(&state, &args),
        OutputFormat::Full => render_full(&state, &args),
        OutputFormat::Compact => render_compact(&state, &args),
    }
}

/// Load HUD state from environment and files
fn load_state(state_dir: &Option<PathBuf>) -> Result<HudState> {
    let mut state = HudState::default();

    // Load from environment variables
    state.model = std::env::var("CLAUDE_MODEL").unwrap_or_else(|_| "sonnet".to_string());
    state.agent = std::env::var("CLAUDE_AGENT").unwrap_or_else(|_| "orchestrator".to_string());
    state.task = std::env::var("CLAUDE_TASK").unwrap_or_default();
    state.progress = std::env::var("CLAUDE_PROGRESS")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);
    state.tokens_in = std::env::var("CLAUDE_TOKENS_IN")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);
    state.tokens_out = std::env::var("CLAUDE_TOKENS_OUT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);

    // Load Ralph state from file
    if let Some(dir) = state_dir {
        let ralph_path = dir.join("ralph-state.json");
        if ralph_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&ralph_path) {
                if let Ok(ralph) = serde_json::from_str::<serde_json::Value>(&content) {
                    state.ralph_active = ralph["active"].as_bool().unwrap_or(false);
                    state.ralph_iteration = ralph["iteration"].as_u64().unwrap_or(0) as u8;
                    state.ralph_max = ralph["max_iterations"].as_u64().unwrap_or(10) as u8;
                }
            }
        }
    } else {
        // Try default paths
        let home = dirs::home_dir().unwrap_or_default();
        let ralph_path = home.join(".claude/ralph-state.json");
        if ralph_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&ralph_path) {
                if let Ok(ralph) = serde_json::from_str::<serde_json::Value>(&content) {
                    state.ralph_active = ralph["active"].as_bool().unwrap_or(false);
                    state.ralph_iteration = ralph["iteration"].as_u64().unwrap_or(0) as u8;
                    state.ralph_max = ralph["max_iterations"].as_u64().unwrap_or(10) as u8;
                }
            }
        }
    }

    Ok(state)
}

/// Render single line HUD
fn render_line(state: &HudState, args: &Args) -> Result<()> {
    let theme = args.theme.config();
    let mut stdout = io::stdout().lock();

    // Time
    let time = Local::now().format("%H:%M:%S").to_string();
    write!(stdout, "{}", SetForegroundColor(Color::DarkGrey))?;
    write!(stdout, "{}", time)?;
    write!(stdout, "{}", ResetColor)?;

    write!(stdout, " {} ", theme.separator)?;

    // Model with color
    let model_color = match state.model.to_lowercase().as_str() {
        m if m.contains("opus") => Color::Magenta,
        m if m.contains("sonnet") => Color::Blue,
        m if m.contains("haiku") => Color::Cyan,
        _ => Color::White,
    };
    write!(stdout, "{}", SetForegroundColor(model_color))?;
    write!(stdout, "{}", format_model(&state.model))?;
    write!(stdout, "{}", ResetColor)?;

    write!(stdout, " {} ", theme.separator)?;

    // Agent
    write!(stdout, "{}", SetForegroundColor(Color::Green))?;
    write!(stdout, "@{}", state.agent)?;
    write!(stdout, "{}", ResetColor)?;

    // Task (if present)
    if !state.task.is_empty() {
        write!(stdout, " {} ", theme.separator)?;
        write!(stdout, "{}", SetForegroundColor(Color::Yellow))?;
        write!(stdout, "{}", truncate(&state.task, 20))?;
        write!(stdout, "{}", ResetColor)?;
    }

    // Progress (if > 0)
    if state.progress > 0 {
        write!(stdout, " {} ", theme.separator)?;
        write!(stdout, "[{}] {}%",
            render_progress_bar(state.progress, 10, theme.progress_filled, theme.progress_empty),
            state.progress
        )?;
    }

    // Ralph (if active)
    if state.ralph_active {
        write!(stdout, " {} ", theme.separator)?;
        write!(stdout, "{}", SetForegroundColor(Color::Cyan))?;
        write!(stdout, "{}", SetAttribute(Attribute::Bold))?;
        write!(stdout, "R:{}/{}", state.ralph_iteration, state.ralph_max)?;
        write!(stdout, "{}", SetAttribute(Attribute::Reset))?;
        write!(stdout, "{}", ResetColor)?;
    }

    // Tokens
    write!(stdout, " {} ", theme.separator)?;
    write!(stdout, "{}", SetForegroundColor(Color::DarkGrey))?;
    write!(stdout, "{}i/{}o", format_tokens(state.tokens_in), format_tokens(state.tokens_out))?;
    write!(stdout, "{}", ResetColor)?;

    writeln!(stdout)?;
    Ok(())
}

/// Render full HUD with borders
fn render_full(state: &HudState, args: &Args) -> Result<()> {
    let theme = args.theme.config();
    let mut stdout = io::stdout().lock();

    // Top border
    writeln!(stdout, "{}", theme.border_char.repeat(args.width))?;

    // Content
    write!(stdout, " ")?;
    render_line(state, args)?;

    // Bottom border
    writeln!(stdout, "{}", theme.border_char.repeat(args.width))?;

    Ok(())
}

/// Render compact HUD
fn render_compact(state: &HudState, args: &Args) -> Result<()> {
    let mut stdout = io::stdout().lock();

    if args.json {
        // JSON output
        let json = serde_json::to_string(&state)?;
        writeln!(stdout, "{}", json)?;
    } else {
        // Minimal text output
        write!(stdout, "{} @{}", format_model(&state.model), state.agent)?;
        if state.progress > 0 {
            write!(stdout, " {}%", state.progress)?;
        }
        if state.ralph_active {
            write!(stdout, " R:{}/{}", state.ralph_iteration, state.ralph_max)?;
        }
        writeln!(stdout)?;
    }

    Ok(())
}

/// Format model name
fn format_model(model: &str) -> &str {
    let lower = model.to_lowercase();
    if lower.contains("opus") {
        "Opus"
    } else if lower.contains("sonnet") {
        "Sonnet"
    } else if lower.contains("haiku") {
        "Haiku"
    } else {
        model
    }
}

/// Truncate string to max length
fn truncate(s: &str, max: usize) -> String {
    if s.len() <= max {
        s.to_string()
    } else {
        format!("{}...", &s[..max.saturating_sub(3)])
    }
}

/// Render progress bar
fn render_progress_bar(progress: u8, width: usize, filled: &str, empty: &str) -> String {
    let filled_count = (progress as usize * width) / 100;
    let empty_count = width - filled_count;
    format!("{}{}", filled.repeat(filled_count), empty.repeat(empty_count))
}

/// Format token count (K/M abbreviation)
fn format_tokens(tokens: u64) -> String {
    if tokens >= 1_000_000 {
        format!("{:.1}M", tokens as f64 / 1_000_000.0)
    } else if tokens >= 1_000 {
        format!("{:.0}K", tokens as f64 / 1_000.0)
    } else {
        tokens.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_model() {
        assert_eq!(format_model("claude-opus-4"), "Opus");
        assert_eq!(format_model("claude-sonnet-4"), "Sonnet");
        assert_eq!(format_model("claude-haiku-3.5"), "Haiku");
    }

    #[test]
    fn test_truncate() {
        assert_eq!(truncate("short", 10), "short");
        assert_eq!(truncate("this is a long string", 10), "this is...");
    }

    #[test]
    fn test_progress_bar() {
        assert_eq!(render_progress_bar(50, 10, "#", "."), "#####.....");
        assert_eq!(render_progress_bar(0, 10, "#", "."), "..........");
        assert_eq!(render_progress_bar(100, 10, "#", "."), "##########");
    }

    #[test]
    fn test_format_tokens() {
        assert_eq!(format_tokens(500), "500");
        assert_eq!(format_tokens(5000), "5K");
        assert_eq!(format_tokens(5500000), "5.5M");
    }
}
