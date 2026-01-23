//! Config Module - Configuration loading and parsing

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

/// Main configuration structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaiyiConfig {
    pub version: String,
    pub agents: Vec<AgentConfig>,
    pub themes: Vec<String>,
    pub hooks: HooksConfig,
    pub settings: SettingsConfig,
}

/// Agent configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentConfig {
    pub name: String,
    pub file: PathBuf,
    pub model: String,
    pub tools: Vec<String>,
    pub description: String,
    pub trigger: String,
}

/// Hooks configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HooksConfig {
    #[serde(rename = "PreToolUse")]
    pub pre_tool_use: Vec<HookEntry>,
    #[serde(rename = "PostToolUse")]
    pub post_tool_use: Vec<HookEntry>,
    #[serde(rename = "Stop")]
    pub stop: Vec<HookEntry>,
    #[serde(rename = "PreCompact")]
    pub pre_compact: Vec<HookEntry>,
}

/// Individual hook entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookEntry {
    #[serde(rename = "type")]
    pub hook_type: String,
    pub command: String,
    pub description: String,
    #[serde(default)]
    pub timeout: Option<u64>,
    #[serde(default)]
    pub matcher: Option<String>,
}

/// Settings configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SettingsConfig {
    pub model: ModelSettings,
    pub context: ContextSettings,
    pub agents: AgentSettings,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelSettings {
    pub default: String,
    pub thinking: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextSettings {
    #[serde(rename = "maxTokens")]
    pub max_tokens: u64,
    pub summarization: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentSettings {
    pub enabled: bool,
    pub parallel: u8,
}

/// Configuration loader
pub struct ConfigLoader {
    root_path: PathBuf,
}

impl ConfigLoader {
    pub fn new(root_path: PathBuf) -> Self {
        Self { root_path }
    }

    /// Load all configuration
    pub fn load(&self) -> Result<TaiyiConfig> {
        let version = self.load_version()?;
        let agents = self.load_agents()?;
        let themes = self.load_themes()?;
        let hooks = self.load_hooks()?;
        let settings = self.load_settings()?;

        Ok(TaiyiConfig {
            version,
            agents,
            themes,
            hooks,
            settings,
        })
    }

    /// Load version from CLAUDE.md
    fn load_version(&self) -> Result<String> {
        let claude_md = self.root_path.join("CLAUDE.md");
        if claude_md.exists() {
            let content = std::fs::read_to_string(&claude_md)?;
            // Extract version from "# 版本: X.X"
            for line in content.lines() {
                if line.contains("版本:") || line.contains("Version:") {
                    if let Some(version) = line.split_whitespace().last() {
                        return Ok(version.to_string());
                    }
                }
            }
        }
        Ok("3.1".to_string())
    }

    /// Load agents from INDEX.md
    fn load_agents(&self) -> Result<Vec<AgentConfig>> {
        let index_path = self.root_path.join("agents/INDEX.md");
        let mut agents = Vec::new();

        if index_path.exists() {
            let content = std::fs::read_to_string(&index_path)?;
            let mut current_agent: Option<AgentConfig> = None;

            for line in content.lines() {
                // Parse YAML-like blocks
                if line.starts_with("####") {
                    // Save previous agent
                    if let Some(agent) = current_agent.take() {
                        agents.push(agent);
                    }
                    // Start new agent
                    let name = line.trim_start_matches('#').trim().to_string();
                    current_agent = Some(AgentConfig {
                        name,
                        file: PathBuf::new(),
                        model: "sonnet".to_string(),
                        tools: vec![],
                        description: String::new(),
                        trigger: String::new(),
                    });
                } else if let Some(ref mut agent) = current_agent {
                    if line.starts_with("文件:") || line.starts_with("file:") {
                        agent.file = PathBuf::from(line.split(':').last().unwrap_or("").trim());
                    } else if line.starts_with("模型:") || line.starts_with("model:") {
                        agent.model = line.split(':').last().unwrap_or("sonnet").trim().to_string();
                    } else if line.starts_with("描述:") || line.starts_with("description:") {
                        agent.description = line.split(':').last().unwrap_or("").trim().to_string();
                    } else if line.starts_with("工具:") || line.starts_with("tools:") {
                        agent.tools = line
                            .split(':')
                            .last()
                            .unwrap_or("")
                            .split(',')
                            .map(|s| s.trim().to_string())
                            .collect();
                    } else if line.starts_with("触发:") || line.starts_with("trigger:") {
                        agent.trigger = line.split(':').last().unwrap_or("").trim().to_string();
                    }
                }
            }

            // Save last agent
            if let Some(agent) = current_agent {
                agents.push(agent);
            }
        }

        // If no agents found, add defaults
        if agents.is_empty() {
            agents = vec![
                AgentConfig {
                    name: "orchestrator".to_string(),
                    file: PathBuf::from("agents/orchestrator.md"),
                    model: "opus".to_string(),
                    tools: vec!["Read".to_string(), "Write".to_string(), "Bash".to_string()],
                    description: "Meta-orchestrator for task decomposition".to_string(),
                    trigger: "Complex tasks".to_string(),
                },
                AgentConfig {
                    name: "architect".to_string(),
                    file: PathBuf::from("agents/architect.md"),
                    model: "opus".to_string(),
                    tools: vec!["Read".to_string(), "Grep".to_string(), "Glob".to_string()],
                    description: "Software architect for system design".to_string(),
                    trigger: "Architecture decisions".to_string(),
                },
                AgentConfig {
                    name: "debugger".to_string(),
                    file: PathBuf::from("agents/debugger.md"),
                    model: "sonnet".to_string(),
                    tools: vec!["Read".to_string(), "Edit".to_string(), "Bash".to_string()],
                    description: "Debug expert for problem solving".to_string(),
                    trigger: "Bug fixes".to_string(),
                },
            ];
        }

        Ok(agents)
    }

    /// Load available themes
    fn load_themes(&self) -> Result<Vec<String>> {
        let themes_dir = self.root_path.join("themes");
        let mut themes = Vec::new();

        if themes_dir.exists() {
            for entry in std::fs::read_dir(&themes_dir)? {
                let entry = entry?;
                let path = entry.path();
                if path.extension().map(|e| e == "toml").unwrap_or(false) {
                    if let Some(stem) = path.file_stem() {
                        themes.push(stem.to_string_lossy().to_string());
                    }
                }
            }
        }

        if themes.is_empty() {
            themes = vec!["default".to_string(), "minimal".to_string(), "nerd".to_string()];
        }

        Ok(themes)
    }

    /// Load hooks configuration
    fn load_hooks(&self) -> Result<HooksConfig> {
        let hooks_path = self.root_path.join("hooks/hooks.json");

        if hooks_path.exists() {
            let content = std::fs::read_to_string(&hooks_path)?;
            let json: serde_json::Value = serde_json::from_str(&content)?;

            let parse_hooks = |key: &str| -> Vec<HookEntry> {
                json["hooks"][key]
                    .as_array()
                    .map(|arr| {
                        arr.iter()
                            .filter_map(|v| {
                                Some(HookEntry {
                                    hook_type: v["type"].as_str()?.to_string(),
                                    command: v["command"].as_str().unwrap_or("").to_string(),
                                    description: v["description"].as_str().unwrap_or("").to_string(),
                                    timeout: v["timeout"].as_u64(),
                                    matcher: v["matcher"].as_str().map(|s| s.to_string()),
                                })
                            })
                            .collect()
                    })
                    .unwrap_or_default()
            };

            Ok(HooksConfig {
                pre_tool_use: parse_hooks("PreToolUse"),
                post_tool_use: parse_hooks("PostToolUse"),
                stop: parse_hooks("Stop"),
                pre_compact: parse_hooks("PreCompact"),
            })
        } else {
            Ok(HooksConfig {
                pre_tool_use: vec![],
                post_tool_use: vec![],
                stop: vec![],
                pre_compact: vec![],
            })
        }
    }

    /// Load settings
    fn load_settings(&self) -> Result<SettingsConfig> {
        let settings_path = self.root_path.join("config/settings.json");

        if settings_path.exists() {
            let content = std::fs::read_to_string(&settings_path)?;
            let json: serde_json::Value = serde_json::from_str(&content)?;

            Ok(SettingsConfig {
                model: ModelSettings {
                    default: json["model"]["default"]
                        .as_str()
                        .unwrap_or("sonnet")
                        .to_string(),
                    thinking: json["model"]["thinking"].as_bool().unwrap_or(true),
                },
                context: ContextSettings {
                    max_tokens: json["context"]["maxTokens"].as_u64().unwrap_or(200000),
                    summarization: json["context"]["summarization"].as_bool().unwrap_or(true),
                },
                agents: AgentSettings {
                    enabled: json["agents"]["enabled"].as_bool().unwrap_or(true),
                    parallel: json["agents"]["parallel"].as_u64().unwrap_or(5) as u8,
                },
            })
        } else {
            Ok(SettingsConfig {
                model: ModelSettings {
                    default: "sonnet".to_string(),
                    thinking: true,
                },
                context: ContextSettings {
                    max_tokens: 200000,
                    summarization: true,
                },
                agents: AgentSettings {
                    enabled: true,
                    parallel: 5,
                },
            })
        }
    }

    /// Save configuration changes
    pub fn save(&self, config: &TaiyiConfig) -> Result<()> {
        // Save settings
        let settings_path = self.root_path.join("config/settings.json");
        let settings_json = serde_json::to_string_pretty(&config.settings)?;
        std::fs::write(&settings_path, settings_json)?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_config_loader_defaults() {
        let dir = tempdir().unwrap();
        let loader = ConfigLoader::new(dir.path().to_path_buf());
        let config = loader.load().unwrap();
        assert_eq!(config.version, "3.1");
    }
}
