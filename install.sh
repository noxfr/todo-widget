#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"
SKILLS="$HOME/.claude/skills"

mkdir -p "$APPS" "$ICONS" "$SKILLS"
sed "s|@INSTALL_DIR@|$DIR|" "$DIR/local.TodoWidget.desktop" > "$APPS/local.TodoWidget.desktop"
ln -sfn "$DIR/local.TodoWidget.svg" "$ICONS/local.TodoWidget.svg"
ln -sfn "$DIR/skill/todo-widget" "$SKILLS/todo-widget"
touch "$HOME/todo.md"

gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
update-desktop-database "$APPS" >/dev/null 2>&1 || true
echo "Installé. Lancer : gtk-launch local.TodoWidget"
