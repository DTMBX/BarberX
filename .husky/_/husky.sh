#!/usr/bin/env sh

# Husky bootstrap script for environment consistency
# Ensures PATH includes node_modules/.bin and sources user config if present

# Skip if HUSKY=0
[ "${HUSKY-}" = "0" ] && exit 0

# Source user config if present
[ -f "$HOME/.huskyrc" ] && . "$HOME/.huskyrc"

# Ensure node_modules/.bin is in PATH
export PATH="node_modules/.bin:$PATH"
