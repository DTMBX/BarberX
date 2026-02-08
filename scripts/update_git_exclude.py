from pathlib import Path

def ensure_lines(path: Path, lines):
    if not path.exists():
        print(f'{path} not found')
        return
    existing = path.read_text(encoding='utf-8')
    to_add = [l for l in lines if l and l not in existing]
    if to_add:
        with path.open('a', encoding='utf-8') as f:
            f.write('\n')
            f.write('\n'.join(to_add))
            f.write('\n')
        print(f'Appended {len(to_add)} lines to {path}')
    else:
        print(f'No changes needed to {path}')


if __name__ == '__main__':
    p = Path('.git') / 'info' / 'exclude'
    lines = [
        '# Local-only private backend entries',
        '_backend/',
        '**/_backend/',
        '.backend-local.txt',
    ]
    ensure_lines(p, lines)
