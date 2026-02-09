"""Generate secrets manifest.def from all JSON files in Secrets Source/jsondata."""

import os
from pathlib import Path


def main():
    base = Path(os.environ['APPDATA']) / 'MoriaMODCreator' / 'Secrets Source' / 'jsondata'
    if not base.exists():
        print(f"Directory not found: {base}")
        return

    # Exclude StringTables directory - these files must never be included
    exclude_dirs = {'StringTables'}
    json_files = sorted(
        f for f in base.rglob('*.json')
        if f.is_file() and not any(ex in f.parts for ex in exclude_dirs)
    )

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<manifest>',
        '  <!-- Secrets manifest: lists all JSON files to overlay during build Phase B -->',
    ]
    for f in json_files:
        rel = str(f.relative_to(base)).replace('\\', '/')
        lines.append(f'  <mod file="{rel}" />')
    lines.append('</manifest>')
    lines.append('')

    manifest_path = base.parent / 'secrets manifest.def'
    manifest_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Written {len(json_files)} entries to {manifest_path}')


if __name__ == '__main__':
    main()
