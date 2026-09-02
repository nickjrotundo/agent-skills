#!/usr/bin/env python3
"""Build one ZIP per skill for manual installation.

Each archive has the skill folder as its root, which is what claude.ai's
custom-skill upload expects and what the Agent Skills spec describes:

    xcheck.zip
      xcheck/
        SKILL.md

Run from anywhere:

    python3 scripts/package.py            # build dist/*.zip
    python3 scripts/package.py --check    # verify dist/ matches skills/

Archives land in dist/, which is gitignored. They are release assets, not
source: build them, then attach them to a GitHub release with

    gh release create v0.1.0 dist/*.zip

Builds are byte-reproducible, so --check can tell you whether what is
sitting in dist/ is stale (exit 1) or current (exit 0) without writing
anything.
"""

import filecmp
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
OUT_DIR = REPO_ROOT / "dist"

# Junk that some filesystems scatter around and that should never ship.
EXCLUDE_NAMES = {".DS_Store", "__MACOSX", "Thumbs.db"}


def skill_files(skill_dir):
    """Every file in the skill, sorted, so builds are reproducible."""
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_NAMES for part in path.parts):
            continue
        yield path


def build(skill_dir, out_dir=None):
    archive = (out_dir or OUT_DIR) / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in skill_files(skill_dir):
            # Root the entry at the skill folder itself, not the repo.
            arcname = Path(skill_dir.name) / path.relative_to(skill_dir)
            # Fixed timestamp so rebuilding an unchanged skill is byte-identical.
            info = zipfile.ZipInfo(str(arcname), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    return archive


def skill_dirs():
    return sorted(p for p in SKILLS_DIR.iterdir()
                  if p.is_dir() and (p / "SKILL.md").is_file())


def check():
    """Exit non-zero if dist/ does not match what skills/ would produce."""
    stale = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for skill_dir in skill_dirs():
            fresh = build(skill_dir, tmp_dir)
            committed = OUT_DIR / fresh.name
            if not committed.is_file():
                stale.append(f"{fresh.name} is missing from dist/")
            elif not filecmp.cmp(fresh, committed, shallow=False):
                stale.append(f"{fresh.name} is out of date")

    for name in sorted(p.name for p in OUT_DIR.glob("*.zip")) if OUT_DIR.is_dir() else []:
        if name not in {f"{d.name}.zip" for d in skill_dirs()}:
            stale.append(f"{name} in dist/ has no matching skill")

    if stale:
        for line in stale:
            print(f"  {line}")
        sys.exit("\ndist/ is stale - run: python3 scripts/package.py")
    print("dist/ is up to date with skills/")


def main():
    if not SKILLS_DIR.is_dir():
        sys.exit(f"no skills/ directory at {SKILLS_DIR}")

    if "--check" in sys.argv[1:]:
        check()
        return

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()

    built = 0
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        if not (skill_dir / "SKILL.md").is_file():
            print(f"  skipping {skill_dir.name}/ - no SKILL.md")
            continue
        archive = build(skill_dir)
        print(f"  {skill_dir.name:<14} -> dist/{archive.name} "
              f"({archive.stat().st_size:,} bytes)")
        with zipfile.ZipFile(archive) as zf:
            for entry in zf.namelist():
                print(f"       {entry}")
        built += 1

    if not built:
        sys.exit("no skills found to package")
    print(f"\nBuilt {built} archive(s) in {OUT_DIR}")


if __name__ == "__main__":
    main()
