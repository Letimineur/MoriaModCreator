"""Clean up temporary and orphan files from %APPDATA%/MoriaMODCreator.

Moves all identified temp/orphan items to a backup folder on the Desktop
before deleting them from the AppData directory.

Temp items cleaned:
  - mymodfiles/*/jsonfiles/   (build intermediate JSON files)
  - mymodfiles/*/uasset/      (build intermediate uasset files)
  - mymodfiles/*/finalmod/    (build output, already zipped to Downloads)
  - output/retoc/             (retoc output, intermediate pak files)
  - output/**                 (all content under output/)
  - Secrets Source/*           (non-.def files removed, *.def files kept)
  - build_log.txt             (regenerated each build)
  - Empty directories anywhere in the tree

Usage:
  python scripts/cleanup_appdata.py           # Dry-run (preview only)
  python scripts/cleanup_appdata.py --run     # Actually move and clean
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_appdata_root() -> Path:
    """Get the MoriaMODCreator AppData directory."""
    return Path(os.environ['APPDATA']) / 'MoriaMODCreator'


def get_backup_dir() -> Path:
    """Create and return a timestamped backup directory on the Desktop."""
    desktop = Path.home() / 'Desktop'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = desktop / f'MoriaMODCreator_cleanup_{timestamp}'
    backup.mkdir(parents=True, exist_ok=True)
    return backup


def find_build_temp_dirs(root: Path) -> list[Path]:
    """Find all build temp directories under mymodfiles/."""
    temp_dirs = []
    mymod = root / 'mymodfiles'
    if mymod.exists():
        for mod_dir in mymod.iterdir():
            if mod_dir.is_dir():
                for temp_name in ('jsonfiles', 'uasset', 'finalmod'):
                    temp_dir = mod_dir / temp_name
                    if temp_dir.exists() and any(temp_dir.iterdir()):
                        temp_dirs.append(temp_dir)
    return temp_dirs


def find_retoc_output(root: Path) -> Path | None:
    """Find the retoc output directory."""
    retoc = root / 'output' / 'retoc'
    if retoc.exists() and any(retoc.iterdir()):
        return retoc
    return None


def find_output_content(root: Path) -> list[Path]:
    """Find all files and directories under output/ to remove."""
    output_dir = root / 'output'
    items = []
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir() and any(item.rglob('*')):
                items.append(item)
            elif item.is_file():
                items.append(item)
    return items


def find_secrets_source_non_def(root: Path) -> list[Path]:
    """Find non-.def files and subdirectories under Secrets Source/."""
    secrets_dir = root / 'Secrets Source'
    items = []
    if secrets_dir.exists():
        for item in secrets_dir.iterdir():
            if item.is_file() and item.suffix.lower() == '.def':
                continue  # Keep .def files
            if item.is_dir() and any(item.rglob('*')):
                items.append(item)
            elif item.is_file():
                items.append(item)
    return items


def find_empty_dirs(root: Path) -> list[Path]:
    """Find all empty directories recursively."""
    empty = []
    for dirpath in sorted(root.rglob('*'), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            empty.append(dirpath)
    return empty


def find_build_log(root: Path) -> Path | None:
    """Find the build log file."""
    log = root / 'build_log.txt'
    return log if log.exists() else None


def dir_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())


def file_count(path: Path) -> int:
    """Count files in a directory."""
    return sum(1 for f in path.rglob('*') if f.is_file())


def format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    if size_bytes > 1024 * 1024:
        return f'{size_bytes / 1024 / 1024:.1f} MB'
    if size_bytes > 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes} B'


def backup_and_remove(src: Path, backup_dir: Path, root: Path, dry_run: bool):
    """Move item to backup directory, preserving relative path structure."""
    rel = src.relative_to(root)
    dest = backup_dir / rel
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dest))
    except PermissionError:
        print(f'    SKIPPED (file locked): {rel}')


def run_cleanup(dry_run: bool = True):
    """Main cleanup routine."""
    root = get_appdata_root()
    if not root.exists():
        print(f'AppData directory not found: {root}')
        return

    print(f'AppData root: {root}')
    print(f'Mode: {"DRY RUN (preview only)" if dry_run else "LIVE — will move files"}')
    print()

    total_size = 0
    total_files = 0
    items_to_clean: list[tuple[str, Path, int, int]] = []

    # 1. Build temp directories
    temp_dirs = find_build_temp_dirs(root)
    for d in temp_dirs:
        size = dir_size(d)
        count = file_count(d)
        total_size += size
        total_files += count
        items_to_clean.append(('BUILD TEMP', d, size, count))

    # 2. Retoc output
    retoc = find_retoc_output(root)
    if retoc:
        size = dir_size(retoc)
        count = file_count(retoc)
        total_size += size
        total_files += count
        items_to_clean.append(('RETOC OUT', retoc, size, count))

    # 3. All output/ content
    output_items = find_output_content(root)
    for item in output_items:
        if item.is_dir():
            size = dir_size(item)
            count = file_count(item)
        else:
            size = item.stat().st_size
            count = 1
        total_size += size
        total_files += count
        items_to_clean.append(('OUTPUT', item, size, count))

    # 4. Secrets Source non-.def files
    secrets_items = find_secrets_source_non_def(root)
    for item in secrets_items:
        if item.is_dir():
            size = dir_size(item)
            count = file_count(item)
        else:
            size = item.stat().st_size
            count = 1
        total_size += size
        total_files += count
        items_to_clean.append(('SECRETS', item, size, count))

    # 5. Build log
    log = find_build_log(root)
    if log:
        size = log.stat().st_size
        total_size += size
        total_files += 1
        items_to_clean.append(('BUILD LOG', log, size, 1))

    # Print summary of items to clean
    print('=== ITEMS TO CLEAN ===')
    for label, path, size, count in items_to_clean:
        rel = path.relative_to(root)
        print(f'  [{label:10}]  {rel}  ({format_size(size)}, {count} files)')

    # 6. Empty directories (listed separately, just removed not backed up)
    empty_dirs = find_empty_dirs(root)
    if empty_dirs:
        print(f'\n=== EMPTY DIRECTORIES ({len(empty_dirs)}) ===')
        for d in empty_dirs:
            print(f'  {d.relative_to(root)}/')

    print(f'\n=== TOTAL ===')
    print(f'  Files to move:       {total_files}')
    print(f'  Space to reclaim:    {format_size(total_size)}')
    print(f'  Empty dirs to remove: {len(empty_dirs)}')

    if dry_run:
        print('\nRun with --run to execute cleanup.')
        return

    # Execute cleanup
    backup_dir = get_backup_dir()
    print(f'\nBackup directory: {backup_dir}')

    # Move files and directories
    for label, path, size, count in items_to_clean:
        rel = path.relative_to(root)
        print(f'  Moving {rel}...')
        backup_and_remove(path, backup_dir, root, dry_run=False)

    # Remove empty directories
    # Re-scan since moving files may have created new empty dirs
    empty_dirs = find_empty_dirs(root)
    for d in empty_dirs:
        print(f'  Removing empty dir: {d.relative_to(root)}/')
        d.rmdir()

    print(f'\nCleanup complete. {total_files} files moved to:')
    print(f'  {backup_dir}')


if __name__ == '__main__':
    is_live = '--run' in sys.argv
    run_cleanup(dry_run=not is_live)
