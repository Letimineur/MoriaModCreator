"""Reformat prebuilt INI files so Description HTML uses indented continuation lines.

This makes them compatible with Python's configparser multi-line value format.
Run once to fix all files in the prebuilt modfiles directory.
"""

import os
from pathlib import Path


def reformat_ini(ini_path: Path) -> str:
    """Reformat an INI file so Description value uses indented continuation lines."""
    lines = ini_path.read_text(encoding='utf-8').splitlines()
    result = []
    in_description = False

    for line in lines:
        stripped = line.strip()

        # Detect start of Description key
        if stripped.startswith('Description') and '=' in stripped:
            key, _, value = line.partition('=')
            value = value.strip()
            if value:
                # Description has content on same line as key
                result.append(f'{key.strip()} = {value}')
            else:
                # Description value starts on next line
                result.append(f'{key.strip()} =')
            in_description = True
            continue

        if in_description:
            # End of description: next section header or next key=value
            if stripped.startswith('[') and stripped.endswith(']'):
                in_description = False
                result.append(line)
                continue

            # A non-HTML key=value line (not starting with <) signals end of description
            if '=' in stripped and not stripped.startswith('<') and stripped[0].isalpha():
                in_description = False
                result.append(line)
                continue

            # Empty lines within description become single indented space
            if not stripped:
                result.append('    ')
            else:
                # Indent continuation lines with 4 spaces
                result.append(f'    {stripped}')
            continue

        result.append(line)

    return '\n'.join(result) + '\n'


def main():
    appdata = Path(os.environ['APPDATA']) / 'MoriaMODCreator' / 'prebuilt modfiles'
    if not appdata.exists():
        print(f'Directory not found: {appdata}')
        return

    ini_files = sorted(appdata.glob('*.ini'))
    print(f'Found {len(ini_files)} INI files')

    for ini_path in ini_files:
        original = ini_path.read_text(encoding='utf-8')
        reformatted = reformat_ini(ini_path)
        if original != reformatted:
            ini_path.write_text(reformatted, encoding='utf-8')
            print(f'  Reformatted: {ini_path.name}')
        else:
            print(f'  No change:   {ini_path.name}')


if __name__ == '__main__':
    main()
