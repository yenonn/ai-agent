#!/bin/bash

# Script to remove model frontmatter from markdown files
# This will remove the "model: claude-sonnet-4-0" line from YAML frontmatter

set -e

COMMANDS_DIR="/Users/i537817/.claude/commands"
BACKUP_DIR="/Users/i537817/.claude/backups/model-removal-$(date +%Y%m%d-%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "🔍 Finding markdown files with model frontmatter..."
echo ""

# Counter
count=0

# Find all .md files with model frontmatter
while IFS= read -r file; do
    # Skip the template and defaults files
    if [[ "$file" == *"_template.md" ]] || [[ "$file" == *"_defaults.md" ]]; then
        echo "⏭️  Skipping: $file"
        continue
    fi

    # Check if file has model frontmatter
    if grep -q "^model: claude-sonnet-4-0" "$file" 2>/dev/null; then
        # Create backup
        relative_path="${file#$COMMANDS_DIR/}"
        backup_file="$BACKUP_DIR/$relative_path"
        mkdir -p "$(dirname "$backup_file")"
        cp "$file" "$backup_file"

        # Remove the model line using sed
        # This removes lines that start with "model: " (with optional spaces)
        sed -i '' '/^model: /d' "$file"

        echo "✅ Processed: $relative_path"
        ((count++))
    fi
done < <(find "$COMMANDS_DIR" -name "*.md" -type f)

echo ""
echo "📊 Summary:"
echo "  - Files processed: $count"
echo "  - Backup location: $BACKUP_DIR"
echo ""
echo "✨ Done! All model frontmatter lines have been removed."
echo ""
echo "⚠️  Note: Files now rely on Claude Code's default model settings."
echo "   If you need to restore, backups are available at: $BACKUP_DIR"
