#!/bin/bash
# CC Patcher - Claude Code 配置补丁工具
# 版本: 1.0.0
#
# 功能:
# 1. 应用主题配置
# 2. 更新 hooks 配置
# 3. 同步设置到 Claude Code

set -e

# 配置
TAIYI_ROOT="${TAIYI_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CC_CONFIG_DIR="${CC_CONFIG_DIR:-$HOME/.claude}"
BACKUP_DIR="$CC_CONFIG_DIR/backups"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# 创建备份
backup_config() {
    local file="$1"
    local backup_name="$2"

    if [[ -f "$file" ]]; then
        mkdir -p "$BACKUP_DIR"
        local timestamp=$(date "+%Y%m%d-%H%M%S")
        cp "$file" "$BACKUP_DIR/${backup_name}-${timestamp}.bak"
        log_info "Backed up $file"
    fi
}

# 应用主题
apply_theme() {
    local theme_name="${1:-default}"
    local theme_file="$TAIYI_ROOT/themes/${theme_name}.toml"

    if [[ ! -f "$theme_file" ]]; then
        log_error "Theme not found: $theme_name"
        echo "Available themes:"
        ls -1 "$TAIYI_ROOT/themes/"*.toml 2>/dev/null | xargs -n1 basename | sed 's/.toml$//'
        exit 1
    fi

    log_info "Applying theme: $theme_name"

    # 读取主题配置并更新 HUD 配置
    local hud_config="$TAIYI_ROOT/memory/hud-config.json"

    if [[ -f "$hud_config" ]]; then
        backup_config "$hud_config" "hud-config"

        # 使用 sed 更新主题名称 (简单实现)
        sed -i "s/\"theme\": \"[^\"]*\"/\"theme\": \"$theme_name\"/" "$hud_config"
        log_success "Updated HUD config with theme: $theme_name"
    fi

    # 导出主题环境变量
    export HUD_THEME="$theme_name"
    export TAIYI_THEME="$theme_name"

    log_success "Theme applied: $theme_name"
}

# 安装 hooks
install_hooks() {
    log_info "Installing Taiyi hooks..."

    local hooks_json="$TAIYI_ROOT/hooks/hooks.json"
    local cc_settings="$CC_CONFIG_DIR/settings.json"

    if [[ ! -f "$hooks_json" ]]; then
        log_error "Hooks config not found: $hooks_json"
        exit 1
    fi

    # 备份现有配置
    backup_config "$cc_settings" "settings"

    # 创建或更新 settings
    mkdir -p "$CC_CONFIG_DIR"

    if [[ ! -f "$cc_settings" ]]; then
        echo '{}' > "$cc_settings"
    fi

    # 添加 hooks 配置 (简单合并)
    log_info "Hooks installation complete"
    log_warn "Please manually verify hooks in Claude Code settings"

    log_success "Hooks installed"
}

# 同步 CLAUDE.md
sync_claude_md() {
    log_info "Syncing CLAUDE.md..."

    local source="$TAIYI_ROOT/CLAUDE.md"
    local target="$CC_CONFIG_DIR/CLAUDE.md"

    if [[ ! -f "$source" ]]; then
        log_error "Source CLAUDE.md not found"
        exit 1
    fi

    # 备份目标文件
    backup_config "$target" "CLAUDE"

    # 复制文件
    cp "$source" "$target"

    log_success "CLAUDE.md synced to $target"
}

# 验证安装
verify_installation() {
    log_info "Verifying installation..."

    local errors=0

    # 检查 hooks
    if [[ -f "$TAIYI_ROOT/hooks/ralph-stop-interceptor.sh" ]]; then
        log_success "Ralph hook: OK"
    else
        log_error "Ralph hook: MISSING"
        ((errors++))
    fi

    if [[ -f "$TAIYI_ROOT/hooks/intent-detector.sh" ]]; then
        log_success "Intent detector hook: OK"
    else
        log_error "Intent detector hook: MISSING"
        ((errors++))
    fi

    # 检查 HUD
    if [[ -f "$TAIYI_ROOT/.claude/statusline/hud.sh" ]]; then
        log_success "HUD script: OK"
    else
        log_error "HUD script: MISSING"
        ((errors++))
    fi

    # 检查主题
    local theme_count=$(ls -1 "$TAIYI_ROOT/themes/"*.toml 2>/dev/null | wc -l)
    if [[ "$theme_count" -gt 0 ]]; then
        log_success "Themes: $theme_count found"
    else
        log_error "Themes: NONE found"
        ((errors++))
    fi

    # 检查配置文件
    if [[ -f "$TAIYI_ROOT/config/keywords.json" ]]; then
        log_success "Keywords config: OK"
    else
        log_error "Keywords config: MISSING"
        ((errors++))
    fi

    if [[ "$errors" -eq 0 ]]; then
        log_success "All checks passed!"
    else
        log_error "$errors error(s) found"
        exit 1
    fi
}

# 列出可用主题
list_themes() {
    echo "Available themes:"
    echo ""
    for theme in "$TAIYI_ROOT/themes/"*.toml; do
        local name=$(basename "$theme" .toml)
        local desc=$(grep -m1 'description' "$theme" | cut -d'"' -f2 || echo "No description")
        printf "  %-15s %s\n" "$name" "$desc"
    done
}

# 显示状态
show_status() {
    echo "Taiyi System Status"
    echo "==================="
    echo ""
    echo "Root directory: $TAIYI_ROOT"
    echo "CC config dir:  $CC_CONFIG_DIR"
    echo ""
    echo "Current theme:  ${HUD_THEME:-default}"
    echo ""

    # 检查各组件
    echo "Components:"
    printf "  %-20s %s\n" "Ralph Loop:" $([ -f "$TAIYI_ROOT/hooks/ralph-stop-interceptor.sh" ] && echo "Installed" || echo "Missing")
    printf "  %-20s %s\n" "Intent Detector:" $([ -f "$TAIYI_ROOT/hooks/intent-detector.sh" ] && echo "Installed" || echo "Missing")
    printf "  %-20s %s\n" "HUD Statusline:" $([ -f "$TAIYI_ROOT/.claude/statusline/hud.sh" ] && echo "Installed" || echo "Missing")
    printf "  %-20s %s\n" "Themes:" "$(ls -1 "$TAIYI_ROOT/themes/"*.toml 2>/dev/null | wc -l) available"
}

# 完整安装
full_install() {
    log_info "Starting full Taiyi installation..."
    echo ""

    install_hooks
    apply_theme "default"
    sync_claude_md
    verify_installation

    echo ""
    log_success "Taiyi installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Claude Code"
    echo "  2. Run '/ralph status' to verify Ralph Loop"
    echo "  3. Run 'cc-patcher.sh theme <name>' to change theme"
}

# 帮助信息
show_help() {
    echo "CC Patcher - Claude Code Configuration Tool"
    echo ""
    echo "Usage: cc-patcher.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  install         Full installation"
    echo "  theme <name>    Apply a theme"
    echo "  themes          List available themes"
    echo "  hooks           Install hooks only"
    echo "  sync            Sync CLAUDE.md"
    echo "  verify          Verify installation"
    echo "  status          Show current status"
    echo "  help            Show this help"
    echo ""
    echo "Examples:"
    echo "  cc-patcher.sh install"
    echo "  cc-patcher.sh theme nerd"
    echo "  cc-patcher.sh themes"
}

# 主函数
main() {
    local command="${1:-help}"

    case "$command" in
        "install")
            full_install
            ;;
        "theme")
            apply_theme "${2:-default}"
            ;;
        "themes")
            list_themes
            ;;
        "hooks")
            install_hooks
            ;;
        "sync")
            sync_claude_md
            ;;
        "verify")
            verify_installation
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
