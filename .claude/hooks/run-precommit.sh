#!/usr/bin/env bash
# Run pre-commit on the just-edited file. Exit 2 feeds stderr back to Claude.
set -u
file=$(jq -r '.tool_input.file_path // empty')
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

# Only run inside the current Claude project.
project="${CLAUDE_PROJECT_DIR:-}"
[ -z "$project" ] && exit 0
case "$file" in
  "$project"/*) ;;
  *) exit 0 ;;
esac

cd "$project" || exit 0

# Locate pre-commit: PATH, then a venv in the project, then the user's pip bin.
pc=""
if command -v pre-commit >/dev/null 2>&1; then
  pc=pre-commit
elif [ -x "$project/.venv/bin/pre-commit" ]; then
  pc="$project/.venv/bin/pre-commit"
elif [ -x "$project/venv/bin/pre-commit" ]; then
  pc="$project/venv/bin/pre-commit"
elif [ -x "$HOME/.local/bin/pre-commit" ]; then
  pc="$HOME/.local/bin/pre-commit"
else
  # Not installed — skip silently; contributors without pre-commit shouldn't be blocked.
  exit 0
fi

# pre-commit filters by file type itself; passing any file is safe.
# Skip the slow local pytest hook here — PostToolUse should be fast.
output=$(SKIP=pytest "$pc" run --files "$file" 2>&1)
status=$?

if [ $status -ne 0 ]; then
  {
    echo "pre-commit failed on $file:"
    echo "$output"
  } >&2
  exit 2
fi
exit 0
