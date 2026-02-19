"""Clean up temporary and orphan files from %APPDATA%/MoriaMODCreator.

Moves all identified temp/orphan items to a backup folder on the Desktop
before deleting them from the AppData directory.

Temp items cleaned:
  - mymodfiles/*/jsonfiles/   (build intermediate JSON files)
  - mymodfiles/*/uasset/      (build intermediate uasset files)
  - mymodfiles/*/finalmod/    (build output, already zipped to Downloads)
  - cache/                    (all cached JSON files, regenerated on scan)
  - output/retoc/             (retoc output, intermediate pak files)
  - output/**                 (all content under output/)
  - changeconstructions/*/buildings/*.json  (build intermediates, .def kept)
  - changesecrets/*/buildings/*.json        (build intermediates, .def kept)
  - New Objects/Build/        (build intermediates)
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


# ---------------------------------------------------------------------------
#  Path helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
#  Finders — each returns a list of paths to clean
# ---------------------------------------------------------------------------

def find_build_temp_dirs(root: Path) -> list[Path]:
    """Find build temp directories (jsonfiles, uasset, finalmod)
    under mymodfiles/<mod>/.
    """
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


def find_cache_dirs(root: Path) -> list[Path]:
    """Find all cache subdirectories (constructions, game, secrets).

    These contain cached copies of game JSON files, regenerated
    automatically when a tab is opened or the app scans game data.
    """
    items = []
    cache_dir = root / 'cache'
    if cache_dir.exists():
        for sub in cache_dir.iterdir():
            if sub.is_dir() and any(sub.rglob('*')):
                items.append(sub)
    return items


def find_output_content(root: Path) -> list[Path]:
    """Find all files and directories under output/ to remove.

    Includes output/jsondata (extracted game JSON) and output/retoc
    (intermediate .pak/.ucas/.utoc files).
    """
    output_dir = root / 'output'
    items = []
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir() and any(item.rglob('*')):
                items.append(item)
            elif item.is_file():
                items.append(item)
    return items


def find_changeset_build_json(root: Path) -> list[Path]:
    """Find build-intermediate JSON files in change set directories.

    Both changesecrets/<prefix>/buildings/ and
    changeconstructions/<prefix>/buildings/ contain copies of game JSON
    files used during the build process. The .def files in the
    definitions/ subdirectory are user content and are NOT cleaned.
    """
    items = []
    for changedir_name in ('changesecrets', 'changeconstructions'):
        changedir = root / changedir_name
        if not changedir.exists():
            continue
        for prefix_dir in changedir.iterdir():
            if not prefix_dir.is_dir():
                continue
            # Clean JSON files in category subdirs (buildings, items, etc.)
            # but NOT the definitions/ subdirectory
            for sub in prefix_dir.iterdir():
                if sub.is_dir() and sub.name != 'definitions':
                    json_files = list(sub.glob('*.json'))
                    items.extend(json_files)
    return items


def find_new_objects_build(root: Path) -> list[Path]:
    """Find build intermediates under New Objects/Build/.

    These are generated during the new-object build process and can
    be safely removed.
    """
    items = []
    build_dir = root / 'New Objects' / 'Build'
    if build_dir.exists():
        for sub in build_dir.iterdir():
            if sub.is_dir() and any(sub.rglob('*')):
                items.append(sub)
            elif sub.is_file():
                items.append(sub)
    return items


def find_secrets_source_non_def(root: Path) -> list[Path]:
    """Find non-.def files under Secrets Source/.

    The .def manifest file is kept; everything else (zip files,
    extracted pak/ucas/utoc files, jsondata) is cleaned.
    """
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


def find_build_log(root: Path) -> Path | None:
    """Find the build log file (regenerated each build)."""
    log = root / 'build_log.txt'
    return log if log.exists() else None


def find_empty_dirs(root: Path) -> list[Path]:
    """Find all empty directories recursively (deepest first)."""
    empty = []
    for dirpath in sorted(root.rglob('*'), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            empty.append(dirpath)
    return empty


# ---------------------------------------------------------------------------
#  Size/count helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
#  Backup and cleanup
# ---------------------------------------------------------------------------

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


def _item_size_count(item: Path) -> tuple[int, int]:
    """Return (size_bytes, file_count) for a file or directory."""
    if item.is_dir():
        return dir_size(item), file_count(item)
    return item.stat().st_size, 1


def _collect_items(label: str, paths: list[Path],
                   result: list[tuple[str, Path, int, int]]):
    """Measure and append each path to the result list with its label."""
    for item in paths:
        size, count = _item_size_count(item)
        result.append((label, item, size, count))


def scan_cleanable_items(root: Path) -> list[tuple[str, Path, int, int]]:
    """Scan the AppData tree and return all items that should be cleaned.

    Each entry is (label, path, size_bytes, file_count).
    """
    items: list[tuple[str, Path, int, int]] = []

    # 1. Build temp directories (mymodfiles/*/jsonfiles, uasset, finalmod)
    _collect_items('BUILD TEMP', find_build_temp_dirs(root), items)

    # 2. Cache directories (constructions, game, secrets)
    _collect_items('CACHE', find_cache_dirs(root), items)

    # 3. All output/ content (jsondata, retoc)
    _collect_items('OUTPUT', find_output_content(root), items)

    # 4. Change set build intermediates (JSON files only, not .def)
    _collect_items('CHANGESET', find_changeset_build_json(root), items)

    # 5. New Objects/Build intermediates
    _collect_items('NEW OBJ', find_new_objects_build(root), items)

    # 6. Secrets Source non-.def files
    _collect_items('SECRETS', find_secrets_source_non_def(root), items)

    # 7. Build log
    log = find_build_log(root)
    if log:
        items.append(('BUILD LOG', log, log.stat().st_size, 1))

    return items


def print_summary(root: Path, items: list[tuple[str, Path, int, int]],
                  empty_dirs: list[Path]):
    """Print the cleanup summary report."""
    total_size = sum(s for _, _, s, _ in items)
    total_files = sum(c for _, _, _, c in items)

    print('=== ITEMS TO CLEAN ===')
    for label, path, size, count in items:
        rel = path.relative_to(root)
        print(f'  [{label:10}]  {rel}  ({format_size(size)}, {count} files)')

    if empty_dirs:
        print(f'\n=== EMPTY DIRECTORIES ({len(empty_dirs)}) ===')
        for d in empty_dirs:
            print(f'  {d.relative_to(root)}/')

    print('\n=== TOTAL ===')
    print(f'  Files to move:       {total_files}')
    print(f'  Space to reclaim:    {format_size(total_size)}')
    print(f'  Empty dirs to remove: {len(empty_dirs)}')


def execute_cleanup(root: Path, items: list[tuple[str, Path, int, int]]):
    """Move all items to a backup directory and remove empty dirs.

    Returns the backup directory path.
    """
    total_files = sum(c for _, _, _, c in items)
    backup_dir = get_backup_dir()
    print(f'\nBackup directory: {backup_dir}')

    # Move files and directories to backup
    for _label, path, _size, _count in items:
        rel = path.relative_to(root)
        print(f'  Moving {rel}...')
        backup_and_remove(path, backup_dir, root, dry_run=False)

    # Re-scan and remove empty directories (moving files creates new ones)
    for d in find_empty_dirs(root):
        print(f'  Removing empty dir: {d.relative_to(root)}/')
        d.rmdir()

    print(f'\nCleanup complete. {total_files} files moved to:')
    print(f'  {backup_dir}')


def run_cleanup(dry_run: bool = True):
    """Main cleanup routine.

    Scans for all cleanable items, prints a summary, and (if not dry-run)
    moves them to a timestamped backup on the Desktop before removing.
    """
    root = get_appdata_root()
    if not root.exists():
        print(f'AppData directory not found: {root}')
        return

    mode = 'DRY RUN (preview only)' if dry_run else 'LIVE — will move files'
    print(f'AppData root: {root}')
    print(f'Mode: {mode}')
    print()

    items = scan_cleanable_items(root)
    empty_dirs = find_empty_dirs(root)
    print_summary(root, items, empty_dirs)

    if dry_run:
        print('\nRun with --run to execute cleanup.')
    else:
        execute_cleanup(root, items)


if __name__ == '__main__':
    is_live = '--run' in sys.argv
    run_cleanup(dry_run=not is_live)
