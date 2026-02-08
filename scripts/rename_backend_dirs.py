#!/usr/bin/env python3
"""
Rename directories named `backend` to `_backend` recursively, skipping common build
and VCS folders. Also append a local git exclude entry so these folders remain
private (adds patterns to .git/info/exclude, not to tracked .gitignore).

This script does NOT stage or commit changes.
"""
from pathlib import Path
import os
import sys

ROOT = Path.cwd()
EXCLUDE_DIRS = {".git", "_site", "builds", "dist", "node_modules", "env", ".venv", "venv"}
RENAMED = []
SKIPPED = []

def should_skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS or name.startswith('.')

for dirpath, dirnames, filenames in os.walk(ROOT, topdown=True):
    # Normalize dirnames in-place to avoid walking excluded directories
    dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
    # We only care about immediate child dirs named 'backend'
    for d in list(dirnames):
        if d == 'backend':
            src = Path(dirpath) / d
            dst = Path(dirpath) / '_backend'
            if dst.exists():
                SKIPPED.append((str(src), str(dst), 'dst_exists'))
                # remove 'backend' so os.walk won't recurse into it now
                dirnames.remove(d)
                continue
            try:
                src.rename(dst)
                RENAMED.append((str(src), str(dst)))
                # update dirnames so os.walk will continue into renamed directory
                dirnames.remove(d)
                dirnames.append('_backend')
            except Exception as e:
                SKIPPED.append((str(src), str(dst), f'error:{e}'))
                dirnames.remove(d)

# Update local git exclude if repo exists
git_exclude = ROOT / '.git' / 'info' / 'exclude'
exclude_added = False
if (ROOT / '.git').exists() and git_exclude.exists():
    entry_lines = ["# Local exclude for private backend dirs (added by script)", "**/_backend/", "_backend/"]
    try:
        existing = git_exclude.read_text(encoding='utf-8')
    except Exception:
        existing = ''
    to_add = [l for l in entry_lines if l and l not in existing]
    if to_add:
        with git_exclude.open('a', encoding='utf-8') as f:
            f.write('\n')
            f.write('\n'.join(to_add))
            f.write('\n')
        exclude_added = True
else:
    # No .git or no info/exclude — just inform the user
    pass

# Summary output
print('Rename script completed.')
print(f'Renamed {len(RENAMED)} directories:')
for s, t in RENAMED:
    print('  ', s, '->', t)
if SKIPPED:
    print(f'Skipped {len(SKIPPED)} entries:')
    for s, t, reason in SKIPPED:
        print('  ', s, '->', t, '(', reason, ')')
if exclude_added:
    print(f'Appended local exclude patterns to {git_exclude}')
else:
    if (ROOT / '.git').exists():
        print(f'No changes made to {git_exclude} (patterns already present or file missing write perms).')
    else:
        print('No .git directory found; to keep these folders private, add the pattern "**/_backend/" to your git exclude or .gitignore manually.')

print('\nNOTICE: No files were staged or committed by this script.')

# Exit code: 0 success, non-zero if nothing renamed
sys.exit(0 if RENAMED else 2)
