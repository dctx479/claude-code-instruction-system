//! Preview Module - Real-time configuration preview

use anyhow::Result;
use std::path::Path;

/// Preview renderer for configuration changes
pub struct PreviewRenderer {
    syntax_set: Option<syntect::parsing::SyntaxSet>,
    theme_set: Option<syntect::highlighting::ThemeSet>,
}

impl PreviewRenderer {
    pub fn new() -> Self {
        // Load syntax highlighting resources (optional)
        let syntax_set = syntect::parsing::SyntaxSet::load_defaults_newlines();
        let theme_set = syntect::highlighting::ThemeSet::load_defaults();

        Self {
            syntax_set: Some(syntax_set),
            theme_set: Some(theme_set),
        }
    }

    /// Preview a configuration file with syntax highlighting
    pub fn preview_file(&self, path: &Path) -> Result<Vec<HighlightedLine>> {
        let content = std::fs::read_to_string(path)?;
        self.preview_content(&content, path.extension().and_then(|s| s.to_str()))
    }

    /// Preview content with optional syntax highlighting
    pub fn preview_content(
        &self,
        content: &str,
        extension: Option<&str>,
    ) -> Result<Vec<HighlightedLine>> {
        let lines: Vec<HighlightedLine> = content
            .lines()
            .enumerate()
            .map(|(i, line)| HighlightedLine {
                number: i + 1,
                content: line.to_string(),
                highlights: vec![],
            })
            .collect();

        // If syntax highlighting is available, apply it
        if let (Some(syntax_set), Some(theme_set)) = (&self.syntax_set, &self.theme_set) {
            if let Some(ext) = extension {
                if let Some(_syntax) = syntax_set.find_syntax_by_extension(ext) {
                    // Apply syntax highlighting here if needed
                    // For now, return plain lines
                }
            }
        }

        Ok(lines)
    }

    /// Generate a preview of HUD output
    pub fn preview_hud(&self, theme: &str) -> Vec<String> {
        let (border, progress_filled, progress_empty, separator) = match theme {
            "minimal" => (" ", "=", "-", "|"),
            "nerd" => ("━", "█", "▒", "┃"),
            _ => ("-", "#", ".", "|"),
        };

        vec![
            format!("{}", border.repeat(60)),
            format!(
                " [10:30:15] {} Sonnet {} @architect {} designing {} [{}{}] 30%",
                separator,
                separator,
                separator,
                separator,
                progress_filled.repeat(3),
                progress_empty.repeat(7)
            ),
            format!("{}", border.repeat(60)),
        ]
    }

    /// Generate a preview of agent output
    pub fn preview_agent(&self, agent_name: &str, model: &str) -> Vec<String> {
        vec![
            format!("Agent: {}", agent_name),
            format!("Model: {}", model),
            String::new(),
            "Output Preview:".to_string(),
            "─".repeat(40),
            format!("[{}] Task started...", agent_name),
            format!("[{}] Analyzing context...", agent_name),
            format!("[{}] Generating response...", agent_name),
            "─".repeat(40),
        ]
    }
}

impl Default for PreviewRenderer {
    fn default() -> Self {
        Self::new()
    }
}

/// A line with syntax highlighting information
#[derive(Debug, Clone)]
pub struct HighlightedLine {
    pub number: usize,
    pub content: String,
    pub highlights: Vec<Highlight>,
}

/// A syntax highlight span
#[derive(Debug, Clone)]
pub struct Highlight {
    pub start: usize,
    pub end: usize,
    pub color: HighlightColor,
}

/// Colors for syntax highlighting
#[derive(Debug, Clone, Copy)]
pub enum HighlightColor {
    Keyword,
    String,
    Number,
    Comment,
    Function,
    Type,
    Operator,
    Default,
}

impl HighlightColor {
    pub fn to_ratatui_color(&self) -> ratatui::style::Color {
        use ratatui::style::Color;
        match self {
            HighlightColor::Keyword => Color::Blue,
            HighlightColor::String => Color::Green,
            HighlightColor::Number => Color::Yellow,
            HighlightColor::Comment => Color::Gray,
            HighlightColor::Function => Color::Cyan,
            HighlightColor::Type => Color::Magenta,
            HighlightColor::Operator => Color::Red,
            HighlightColor::Default => Color::White,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_preview_renderer_creation() {
        let renderer = PreviewRenderer::new();
        assert!(renderer.syntax_set.is_some());
    }

    #[test]
    fn test_hud_preview() {
        let renderer = PreviewRenderer::new();
        let preview = renderer.preview_hud("default");
        assert_eq!(preview.len(), 3);
    }

    #[test]
    fn test_agent_preview() {
        let renderer = PreviewRenderer::new();
        let preview = renderer.preview_agent("architect", "opus");
        assert!(!preview.is_empty());
    }
}
