//! State Module - Application state management

use anyhow::Result;
use std::collections::HashMap;
use std::path::PathBuf;

use crate::config::{AgentConfig, ConfigLoader, HookEntry, TaiyiConfig};

/// Main application state
pub struct AppState {
    // Configuration
    pub config: TaiyiConfig,
    pub config_loader: ConfigLoader,
    pub root_path: PathBuf,

    // UI State
    pub tabs: Vec<String>,
    pub selected_tab: usize,
    pub show_help: bool,
    pub search_active: bool,
    pub search_query: String,
    pub status_message: String,

    // Tab-specific state
    pub agents: Vec<AgentInfo>,
    pub selected_agent: usize,
    pub themes: Vec<String>,
    pub selected_theme_idx: usize,
    pub current_theme: String,
    pub hooks: HashMap<String, Vec<HookInfo>>,
    pub memory_stats: MemoryStats,

    // System state
    pub ralph_active: bool,
    pub has_unsaved_changes: bool,
}

/// Agent information for display
#[derive(Debug, Clone)]
pub struct AgentInfo {
    pub name: String,
    pub model: String,
    pub description: String,
    pub tools: Vec<String>,
    pub trigger: String,
}

/// Hook information for display
#[derive(Debug, Clone)]
pub struct HookInfo {
    pub description: String,
    pub command: String,
}

/// Memory system statistics
#[derive(Debug, Clone, Default)]
pub struct MemoryStats {
    pub lessons_count: usize,
    pub error_patterns_count: usize,
    pub active_plans: usize,
    pub resolutions_count: usize,
    pub last_archive: String,
}

impl AppState {
    pub fn new(root_path: PathBuf, theme: String) -> Result<Self> {
        let config_loader = ConfigLoader::new(root_path.clone());
        let config = config_loader.load()?;

        // Convert agents
        let agents: Vec<AgentInfo> = config
            .agents
            .iter()
            .map(|a| AgentInfo {
                name: a.name.clone(),
                model: a.model.clone(),
                description: a.description.clone(),
                tools: a.tools.clone(),
                trigger: a.trigger.clone(),
            })
            .collect();

        // Convert hooks
        let mut hooks = HashMap::new();
        hooks.insert(
            "PreToolUse".to_string(),
            config
                .hooks
                .pre_tool_use
                .iter()
                .map(|h| HookInfo {
                    description: h.description.clone(),
                    command: h.command.clone(),
                })
                .collect(),
        );
        hooks.insert(
            "PostToolUse".to_string(),
            config
                .hooks
                .post_tool_use
                .iter()
                .map(|h| HookInfo {
                    description: h.description.clone(),
                    command: h.command.clone(),
                })
                .collect(),
        );
        hooks.insert(
            "Stop".to_string(),
            config
                .hooks
                .stop
                .iter()
                .map(|h| HookInfo {
                    description: h.description.clone(),
                    command: h.command.clone(),
                })
                .collect(),
        );
        hooks.insert(
            "PreCompact".to_string(),
            config
                .hooks
                .pre_compact
                .iter()
                .map(|h| HookInfo {
                    description: h.description.clone(),
                    command: h.command.clone(),
                })
                .collect(),
        );

        // Load memory stats
        let memory_stats = Self::load_memory_stats(&root_path)?;

        // Check Ralph status
        let ralph_active = Self::check_ralph_status(&root_path);

        Ok(Self {
            config,
            config_loader,
            root_path,
            tabs: vec![
                "Overview".to_string(),
                "Agents".to_string(),
                "Themes".to_string(),
                "Hooks".to_string(),
                "Memory".to_string(),
            ],
            selected_tab: 0,
            show_help: false,
            search_active: false,
            search_query: String::new(),
            status_message: "Ready".to_string(),
            agents,
            selected_agent: 0,
            themes: vec!["default".to_string(), "minimal".to_string(), "nerd".to_string()],
            selected_theme_idx: 0,
            current_theme: theme,
            hooks,
            memory_stats,
            ralph_active,
            has_unsaved_changes: false,
        })
    }

    /// Load memory statistics
    fn load_memory_stats(root_path: &PathBuf) -> Result<MemoryStats> {
        let mut stats = MemoryStats::default();

        // Count lessons learned
        let lessons_path = root_path.join("memory/lessons-learned.md");
        if lessons_path.exists() {
            let content = std::fs::read_to_string(&lessons_path)?;
            stats.lessons_count = content.matches("## [").count();
        }

        // Count error patterns
        let errors_path = root_path.join("memory/error-patterns.md");
        if errors_path.exists() {
            let content = std::fs::read_to_string(&errors_path)?;
            stats.error_patterns_count = content.matches("### ").count();
        }

        // Count active plans
        let plans_path = root_path.join(".claude/context/plans/index.json");
        if plans_path.exists() {
            let content = std::fs::read_to_string(&plans_path)?;
            let json: serde_json::Value = serde_json::from_str(&content)?;
            if let Some(plans) = json["plans"].as_array() {
                stats.active_plans = plans.len();
            }
        }

        // Count resolutions
        let resolutions_dir = root_path.join(".claude/context/resolutions");
        if resolutions_dir.exists() {
            stats.resolutions_count = std::fs::read_dir(&resolutions_dir)?.count();
        }

        // Get last archive time
        let archives_dir = root_path.join(".claude/memory/context-archives");
        if archives_dir.exists() {
            if let Some(latest) = std::fs::read_dir(&archives_dir)?
                .filter_map(|e| e.ok())
                .max_by_key(|e| e.metadata().ok().and_then(|m| m.modified().ok()))
            {
                stats.last_archive = latest.file_name().to_string_lossy().to_string();
            }
        }

        Ok(stats)
    }

    /// Check Ralph status
    fn check_ralph_status(root_path: &PathBuf) -> bool {
        let ralph_path = root_path.join("memory/ralph-state.json");
        if ralph_path.exists() {
            if let Ok(content) = std::fs::read_to_string(&ralph_path) {
                return content.contains("\"active\": true");
            }
        }
        false
    }

    // Navigation methods
    pub fn next_tab(&mut self) {
        self.selected_tab = (self.selected_tab + 1) % self.tabs.len();
    }

    pub fn prev_tab(&mut self) {
        self.selected_tab = if self.selected_tab == 0 {
            self.tabs.len() - 1
        } else {
            self.selected_tab - 1
        };
    }

    pub fn select_tab(&mut self, idx: usize) {
        if idx < self.tabs.len() {
            self.selected_tab = idx;
        }
    }

    pub fn move_up(&mut self) {
        match self.selected_tab {
            1 => {
                // Agents tab
                if self.selected_agent > 0 {
                    self.selected_agent -= 1;
                }
            }
            2 => {
                // Themes tab
                if self.selected_theme_idx > 0 {
                    self.selected_theme_idx -= 1;
                }
            }
            _ => {}
        }
    }

    pub fn move_down(&mut self) {
        match self.selected_tab {
            1 => {
                // Agents tab
                if self.selected_agent < self.agents.len().saturating_sub(1) {
                    self.selected_agent += 1;
                }
            }
            2 => {
                // Themes tab
                if self.selected_theme_idx < self.themes.len().saturating_sub(1) {
                    self.selected_theme_idx += 1;
                }
            }
            _ => {}
        }
    }

    pub fn move_left(&mut self) {
        // Currently no horizontal navigation
    }

    pub fn move_right(&mut self) {
        // Currently no horizontal navigation
    }

    pub fn select_item(&mut self) {
        match self.selected_tab {
            2 => {
                // Themes tab - apply selected theme
                if let Some(theme) = self.themes.get(self.selected_theme_idx) {
                    self.current_theme = theme.clone();
                    self.status_message = format!("Theme changed to: {}", theme);
                    self.has_unsaved_changes = true;
                }
            }
            _ => {}
        }
    }

    pub fn go_back(&mut self) {
        if self.search_active {
            self.search_active = false;
            self.search_query.clear();
        } else if self.show_help {
            self.show_help = false;
        }
    }

    pub fn toggle_help(&mut self) {
        self.show_help = !self.show_help;
    }

    pub fn start_search(&mut self) {
        self.search_active = true;
        self.search_query.clear();
    }

    pub fn cycle_theme(&mut self) {
        self.selected_theme_idx = (self.selected_theme_idx + 1) % self.themes.len();
        if let Some(theme) = self.themes.get(self.selected_theme_idx) {
            self.current_theme = theme.clone();
            self.status_message = format!("Theme: {}", theme);
        }
    }

    pub fn refresh(&mut self) -> Result<()> {
        self.config = self.config_loader.load()?;
        self.memory_stats = Self::load_memory_stats(&self.root_path)?;
        self.ralph_active = Self::check_ralph_status(&self.root_path);
        self.status_message = "Refreshed".to_string();
        Ok(())
    }

    pub fn save(&mut self) -> Result<()> {
        self.config_loader.save(&self.config)?;
        self.has_unsaved_changes = false;
        self.status_message = "Saved".to_string();
        Ok(())
    }

    pub fn check_file_changes(&mut self) -> Result<()> {
        // Placeholder for file watching implementation
        Ok(())
    }
}
