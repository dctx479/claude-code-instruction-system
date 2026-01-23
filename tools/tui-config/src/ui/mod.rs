//! UI Module - Rendering components for Taiyi TUI Config

mod tabs;
mod widgets;
mod themes;

pub use tabs::*;
pub use widgets::*;
pub use themes::*;

use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Tabs, Clear},
    Frame,
};

use crate::state::AppState;

/// Main UI rendering function
pub fn render_ui(f: &mut Frame, app: &AppState) {
    // Create main layout
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(1)
        .constraints([
            Constraint::Length(3),  // Header with tabs
            Constraint::Min(10),    // Main content
            Constraint::Length(3),  // Status bar
        ])
        .split(f.area());

    // Render header with tabs
    render_header(f, app, chunks[0]);

    // Render main content based on selected tab
    render_main_content(f, app, chunks[1]);

    // Render status bar
    render_status_bar(f, app, chunks[2]);

    // Render help overlay if active
    if app.show_help {
        render_help_overlay(f, app);
    }

    // Render search overlay if active
    if app.search_active {
        render_search_overlay(f, app);
    }
}

/// Render header with tabs
fn render_header(f: &mut Frame, app: &AppState, area: Rect) {
    let titles: Vec<Line> = app
        .tabs
        .iter()
        .map(|t| {
            let (first, rest) = t.split_at(1);
            Line::from(vec![
                Span::styled(
                    first,
                    Style::default()
                        .fg(Color::Yellow)
                        .add_modifier(Modifier::UNDERLINED),
                ),
                Span::styled(rest, Style::default().fg(Color::White)),
            ])
        })
        .collect();

    let tabs = Tabs::new(titles)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Taiyi Config ")
                .title_style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
        )
        .select(app.selected_tab)
        .style(Style::default().fg(Color::White))
        .highlight_style(
            Style::default()
                .fg(Color::Yellow)
                .add_modifier(Modifier::BOLD),
        );

    f.render_widget(tabs, area);
}

/// Render main content based on selected tab
fn render_main_content(f: &mut Frame, app: &AppState, area: Rect) {
    match app.selected_tab {
        0 => render_overview_tab(f, app, area),
        1 => render_agents_tab(f, app, area),
        2 => render_themes_tab(f, app, area),
        3 => render_hooks_tab(f, app, area),
        4 => render_memory_tab(f, app, area),
        _ => render_overview_tab(f, app, area),
    }
}

/// Render overview tab
fn render_overview_tab(f: &mut Frame, app: &AppState, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(area);

    // Left: System status
    let status_block = Block::default()
        .borders(Borders::ALL)
        .title(" System Status ")
        .title_style(Style::default().fg(Color::Green));

    let status_text = vec![
        Line::from(vec![
            Span::styled("Version: ", Style::default().fg(Color::Gray)),
            Span::styled("3.1", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("Agents: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} loaded", app.agents.len()),
                Style::default().fg(Color::Green),
            ),
        ]),
        Line::from(vec![
            Span::styled("Themes: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} available", app.themes.len()),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::styled("Active Theme: ", Style::default().fg(Color::Gray)),
            Span::styled(&app.current_theme, Style::default().fg(Color::Magenta)),
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("Ralph: ", Style::default().fg(Color::Gray)),
            Span::styled(
                if app.ralph_active { "Active" } else { "Inactive" },
                Style::default().fg(if app.ralph_active { Color::Green } else { Color::Gray }),
            ),
        ]),
        Line::from(vec![
            Span::styled("HUD: ", Style::default().fg(Color::Gray)),
            Span::styled("Enabled", Style::default().fg(Color::Green)),
        ]),
    ];

    let status = Paragraph::new(status_text).block(status_block);
    f.render_widget(status, chunks[0]);

    // Right: Quick actions
    let actions_block = Block::default()
        .borders(Borders::ALL)
        .title(" Quick Actions ")
        .title_style(Style::default().fg(Color::Yellow));

    let actions_text = vec![
        Line::from(vec![
            Span::styled("[t] ", Style::default().fg(Color::Yellow)),
            Span::raw("Cycle theme"),
        ]),
        Line::from(vec![
            Span::styled("[r] ", Style::default().fg(Color::Yellow)),
            Span::raw("Refresh config"),
        ]),
        Line::from(vec![
            Span::styled("[Ctrl+s] ", Style::default().fg(Color::Yellow)),
            Span::raw("Save changes"),
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("[?] ", Style::default().fg(Color::Yellow)),
            Span::raw("Show help"),
        ]),
        Line::from(vec![
            Span::styled("[/] ", Style::default().fg(Color::Yellow)),
            Span::raw("Search"),
        ]),
        Line::from(vec![
            Span::styled("[q] ", Style::default().fg(Color::Yellow)),
            Span::raw("Quit"),
        ]),
    ];

    let actions = Paragraph::new(actions_text).block(actions_block);
    f.render_widget(actions, chunks[1]);
}

/// Render agents tab
fn render_agents_tab(f: &mut Frame, app: &AppState, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(area);

    // Left: Agent list
    let agent_items: Vec<Line> = app
        .agents
        .iter()
        .enumerate()
        .map(|(i, agent)| {
            let style = if i == app.selected_agent {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };
            Line::styled(format!(" {} ", agent.name), style)
        })
        .collect();

    let agents_list = Paragraph::new(agent_items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Agents ")
            .title_style(Style::default().fg(Color::Cyan)),
    );
    f.render_widget(agents_list, chunks[0]);

    // Right: Agent details
    if let Some(agent) = app.agents.get(app.selected_agent) {
        let detail_text = vec![
            Line::from(vec![
                Span::styled("Name: ", Style::default().fg(Color::Gray)),
                Span::styled(&agent.name, Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
            ]),
            Line::from(vec![
                Span::styled("Model: ", Style::default().fg(Color::Gray)),
                Span::styled(&agent.model, Style::default().fg(Color::Magenta)),
            ]),
            Line::from(""),
            Line::from(Span::styled("Description:", Style::default().fg(Color::Gray))),
            Line::from(Span::raw(&agent.description)),
            Line::from(""),
            Line::from(Span::styled("Tools:", Style::default().fg(Color::Gray))),
            Line::from(Span::styled(
                agent.tools.join(", "),
                Style::default().fg(Color::Green),
            )),
            Line::from(""),
            Line::from(Span::styled("Trigger:", Style::default().fg(Color::Gray))),
            Line::from(Span::raw(&agent.trigger)),
        ];

        let details = Paragraph::new(detail_text).block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Agent Details ")
                .title_style(Style::default().fg(Color::Green)),
        );
        f.render_widget(details, chunks[1]);
    }
}

/// Render themes tab with live preview
fn render_themes_tab(f: &mut Frame, app: &AppState, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(area);

    // Left: Theme list
    let theme_items: Vec<Line> = app
        .themes
        .iter()
        .enumerate()
        .map(|(i, theme)| {
            let marker = if theme == &app.current_theme { "* " } else { "  " };
            let style = if i == app.selected_theme_idx {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };
            Line::styled(format!("{}{}", marker, theme), style)
        })
        .collect();

    let themes_list = Paragraph::new(theme_items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Themes ")
            .title_style(Style::default().fg(Color::Magenta)),
    );
    f.render_widget(themes_list, chunks[0]);

    // Right: Theme preview
    let preview_text = generate_theme_preview(app);
    let preview = Paragraph::new(preview_text).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Preview ")
            .title_style(Style::default().fg(Color::Yellow)),
    );
    f.render_widget(preview, chunks[1]);
}

/// Generate theme preview content
fn generate_theme_preview(app: &AppState) -> Vec<Line<'static>> {
    vec![
        Line::from(Span::styled(
            "HUD Preview:",
            Style::default().add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        Line::from(vec![
            Span::styled("[10:30:15]", Style::default().fg(Color::Gray)),
            Span::raw(" "),
            Span::styled("Sonnet", Style::default().fg(Color::Blue)),
            Span::raw(" | "),
            Span::styled("@architect", Style::default().fg(Color::Green)),
            Span::raw(" | "),
            Span::styled("designing", Style::default().fg(Color::Yellow)),
            Span::raw(" | "),
            Span::styled("[###.....]", Style::default().fg(Color::Cyan)),
            Span::raw(" 30%"),
        ]),
        Line::from(""),
        Line::from(Span::styled(
            "Code Block Preview:",
            Style::default().add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        Line::from(Span::styled(
            "fn main() {",
            Style::default().fg(Color::Blue),
        )),
        Line::from(Span::styled(
            "    println!(\"Hello, Taiyi!\");",
            Style::default().fg(Color::Green),
        )),
        Line::from(Span::styled("}", Style::default().fg(Color::Blue))),
        Line::from(""),
        Line::from(Span::styled(
            "Status Indicators:",
            Style::default().add_modifier(Modifier::BOLD),
        )),
        Line::from(vec![
            Span::styled(" [OK] ", Style::default().fg(Color::Green)),
            Span::styled(" [WARN] ", Style::default().fg(Color::Yellow)),
            Span::styled(" [ERR] ", Style::default().fg(Color::Red)),
        ]),
    ]
}

/// Render hooks tab
fn render_hooks_tab(f: &mut Frame, app: &AppState, area: Rect) {
    let hooks_text: Vec<Line> = app
        .hooks
        .iter()
        .flat_map(|(hook_type, hooks)| {
            let mut lines = vec![
                Line::from(Span::styled(
                    hook_type.clone(),
                    Style::default()
                        .fg(Color::Cyan)
                        .add_modifier(Modifier::BOLD),
                )),
            ];
            for hook in hooks {
                lines.push(Line::from(vec![
                    Span::raw("  - "),
                    Span::styled(&hook.description, Style::default().fg(Color::White)),
                ]));
            }
            lines.push(Line::from(""));
            lines
        })
        .collect();

    let hooks_widget = Paragraph::new(hooks_text).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Hooks Configuration ")
            .title_style(Style::default().fg(Color::Yellow)),
    );
    f.render_widget(hooks_widget, area);
}

/// Render memory tab
fn render_memory_tab(f: &mut Frame, app: &AppState, area: Rect) {
    let memory_text = vec![
        Line::from(Span::styled(
            "Memory System Status",
            Style::default().add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        Line::from(vec![
            Span::styled("Lessons Learned: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} entries", app.memory_stats.lessons_count),
                Style::default().fg(Color::Green),
            ),
        ]),
        Line::from(vec![
            Span::styled("Error Patterns: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} patterns", app.memory_stats.error_patterns_count),
                Style::default().fg(Color::Yellow),
            ),
        ]),
        Line::from(vec![
            Span::styled("Active Plans: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} plans", app.memory_stats.active_plans),
                Style::default().fg(Color::Cyan),
            ),
        ]),
        Line::from(""),
        Line::from(Span::styled(
            "Context Archives",
            Style::default().add_modifier(Modifier::BOLD),
        )),
        Line::from(vec![
            Span::styled("Resolutions: ", Style::default().fg(Color::Gray)),
            Span::styled(
                format!("{} saved", app.memory_stats.resolutions_count),
                Style::default().fg(Color::Green),
            ),
        ]),
        Line::from(vec![
            Span::styled("Last Archive: ", Style::default().fg(Color::Gray)),
            Span::styled(&app.memory_stats.last_archive, Style::default().fg(Color::Gray)),
        ]),
    ];

    let memory_widget = Paragraph::new(memory_text).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Memory System ")
            .title_style(Style::default().fg(Color::Green)),
    );
    f.render_widget(memory_widget, area);
}

/// Render status bar
fn render_status_bar(f: &mut Frame, app: &AppState, area: Rect) {
    let status = Paragraph::new(Line::from(vec![
        Span::styled(" Taiyi ", Style::default().bg(Color::Blue).fg(Color::White)),
        Span::raw(" "),
        Span::styled(&app.status_message, Style::default().fg(Color::Gray)),
        Span::raw(" | "),
        Span::styled(
            format!("Theme: {}", app.current_theme),
            Style::default().fg(Color::Magenta),
        ),
        Span::raw(" | "),
        Span::styled(
            "Press ? for help",
            Style::default().fg(Color::Gray),
        ),
    ]))
    .block(Block::default().borders(Borders::ALL));

    f.render_widget(status, area);
}

/// Render help overlay
fn render_help_overlay(f: &mut Frame, _app: &AppState) {
    let area = centered_rect(60, 70, f.area());
    f.render_widget(Clear, area);

    let help_text = vec![
        Line::from(Span::styled(
            "Keyboard Shortcuts",
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        Line::from(vec![
            Span::styled("Tab/Shift+Tab  ", Style::default().fg(Color::Yellow)),
            Span::raw("Switch tabs"),
        ]),
        Line::from(vec![
            Span::styled("1-5            ", Style::default().fg(Color::Yellow)),
            Span::raw("Jump to tab"),
        ]),
        Line::from(vec![
            Span::styled("j/k or Up/Down ", Style::default().fg(Color::Yellow)),
            Span::raw("Navigate list"),
        ]),
        Line::from(vec![
            Span::styled("Enter          ", Style::default().fg(Color::Yellow)),
            Span::raw("Select/Edit item"),
        ]),
        Line::from(vec![
            Span::styled("Esc            ", Style::default().fg(Color::Yellow)),
            Span::raw("Go back/Cancel"),
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("t              ", Style::default().fg(Color::Yellow)),
            Span::raw("Cycle theme"),
        ]),
        Line::from(vec![
            Span::styled("r              ", Style::default().fg(Color::Yellow)),
            Span::raw("Refresh config"),
        ]),
        Line::from(vec![
            Span::styled("Ctrl+s         ", Style::default().fg(Color::Yellow)),
            Span::raw("Save changes"),
        ]),
        Line::from(vec![
            Span::styled("/              ", Style::default().fg(Color::Yellow)),
            Span::raw("Search"),
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("?              ", Style::default().fg(Color::Yellow)),
            Span::raw("Toggle this help"),
        ]),
        Line::from(vec![
            Span::styled("q/Ctrl+c       ", Style::default().fg(Color::Yellow)),
            Span::raw("Quit"),
        ]),
        Line::from(""),
        Line::from(Span::styled(
            "Press any key to close",
            Style::default().fg(Color::Gray),
        )),
    ];

    let help = Paragraph::new(help_text).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Help ")
            .title_style(Style::default().fg(Color::Green)),
    );
    f.render_widget(help, area);
}

/// Render search overlay
fn render_search_overlay(f: &mut Frame, app: &AppState) {
    let area = Rect::new(f.area().x + 2, f.area().y + 2, f.area().width - 4, 3);
    f.render_widget(Clear, area);

    let search = Paragraph::new(Line::from(vec![
        Span::styled("Search: ", Style::default().fg(Color::Yellow)),
        Span::raw(&app.search_query),
        Span::styled("_", Style::default().add_modifier(Modifier::SLOW_BLINK)),
    ]))
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Search ")
            .title_style(Style::default().fg(Color::Cyan)),
    );
    f.render_widget(search, area);
}

/// Helper function to create a centered rect
fn centered_rect(percent_x: u16, percent_y: u16, r: Rect) -> Rect {
    let popup_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Percentage((100 - percent_y) / 2),
            Constraint::Percentage(percent_y),
            Constraint::Percentage((100 - percent_y) / 2),
        ])
        .split(r);

    Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage((100 - percent_x) / 2),
            Constraint::Percentage(percent_x),
            Constraint::Percentage((100 - percent_x) / 2),
        ])
        .split(popup_layout[1])[1]
}
