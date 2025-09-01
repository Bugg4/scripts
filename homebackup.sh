#!/usr/bin/env bash
set -euo pipefail

# === Config ===
SOURCE="$HOME/"
MOUNTPOINT="/mnt/WIN_D"
BASE_DEST="$MOUNTPOINT/arch-backup"
IGNORE_FILE="$HOME/.config/homebackup/ignore.list"

# Check if mountpoint is available
if ! mountpoint -q "$MOUNTPOINT"; then
    echo "Error: $MOUNTPOINT is not mounted."
    exit 1
fi

# Ensure ignore file exists
if [[ ! -f "$IGNORE_FILE" ]]; then
    echo "Ignore list not found at: $IGNORE_FILE"
    exit 1
fi

# Create dated destination dir (e.g. 2025-09-01_22-43-21/home)
DATE="$(date +'%Y-%m-%d_%H-%M-%S')"
DEST="$BASE_DEST/$DATE/home"

mkdir -p "$DEST"

# --- Run rsync with filters from the ignore file ---
rsync -av --ignore-case \
    --exclude-from="$IGNORE_FILE" \
    "$SOURCE" "$DEST"