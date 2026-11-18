#!/usr/bin/env python3
"""Check a knowledge bundle: frontmatter, vocabulary, and every link.

    okf_lint.py [--root <project>] [--bundle <dir>]
"""

from __future__ import annotations

import pathlib
import re
import sys

import okfconf

ROOT = okfconf.root(sys.argv)
DEFAULT_BUNDLE = ROOT / "okf"
CONF = okfconf.read(ROOT)
CODE_URL = okfconf.one(CONF, "code_url")
VOCAB = "decisions/why-this-bundle-exists.md"
RESERVED = {"index.md", "log.md"}
SOURCE_SUFFIX = set(okfconf.many(CONF, "source_suffix",
                                 (".swift", ".metal", ".py", ".sh")))
# Copied in byte-identical from another repo, whose own bundle they point
# at. Editing them would turn the next re-import from a copy into a merge.
VENDORED = set(okfconf.many(CONF, "vendored"))
COVERED = okfconf.many(CONF, "covered")
POINTER = re.compile(r"okf/[a-z0-9-]+/[a-z0-9.-]+\.md")
# The wikilink shape this bundle used before v0.2. OKF has no such link and the
# engine that reads the bundle cannot see one, so any survivor is a fault.
WIKI = re.compile(r"\[\[([a-z][a-z0-9.]*(?:-[a-z0-9.]+)+)\]\]")
LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
NAME = re.compile(r"^[a-z0-9]+([-.][a-z0-9]+)*\.md$")
SPEC = ["type"]                                    # OKF v0.2 requires this
POLICY = ["title", "generated"]                    # ours, stricter
CLAIM = 40    # a title this long may stand in for `description:`

def frontmatter(text):
    """The leading --- block: flat strings, one-line lists, and the
    spec's nested `sources: [- resource: ...]`."""
    found = {}
    last = ""
    lines = text.splitlines()
    inside = bool(lines) and lines[0].strip() == "---"
    for line in lines[1:] if inside else []:
        if line.strip() == "---":
            inside = False
        elif not inside:
            pass
        elif ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            last = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                found[last] = [one.strip() for one
                               in value[1:-1].split(",") if one.strip()]
            else:
                found[last] = value
        elif line.strip().startswith("- resource:"):
            # `sources:` opens with an empty value, so the key is a bare
            # string until its first entry arrives.
            _, _, one = line.partition("- resource:")
            if not isinstance(found.get("sources"), list):
                found["sources"] = []
            found["sources"].append(one.strip())
        elif last and isinstance(found.get(last), str):
            found[last] = found[last] + " " + line.strip()
    return found

def resolved(bundle, one):
    """Where a `sources:` entry lands on disk, or None for an external URL
    this lint does not follow."""
    out = None
    if one.startswith(CODE_URL):
        out = ROOT / one[len(CODE_URL):]
    elif "://" not in one:
        out = bundle / one
    return out

def vocabulary(bundle):
    """The types the bundle declares, from the table in its own concept."""
    path = bundle / VOCAB
    text = path.read_text() if path.exists() else ""
    return set(re.findall(r"^\|\s*`(\w+)`\s*\|", text, re.M))

def concepts(bundle):
    return sorted(one for one in bundle.rglob("*.md")
                  if one.name not in RESERVED
                  and not any(part.startswith(".")
                              for part in one.relative_to(bundle).parts))

def shaped(bundle, path, front, types):
    """Frontmatter faults on one concept."""
    faults = []
    for key in SPEC:
        if not front.get(key):
            faults.append(f"missing `{key}:` (OKF v0.2 requires it)")
    for key in POLICY:
        if not front.get(key):
            faults.append(f"missing `{key}:` (local policy, not spec)")
    if not front.get("description") and len(front.get("title", "")) < CLAIM:
        faults.append(f"missing `description:` and the title is under {CLAIM} "
                      f"characters, so nothing states the claim a search "
                      f"matches on (local policy, not spec)")
    kind = front.get("type", "")
    if kind and kind not in types:
        faults.append(f"type `{kind}` is not in the bundle vocabulary "
                      f"({', '.join(sorted(types))})")
    if not NAME.match(path.name):
        faults.append("filename is not kebab-case")
    # A colon followed by a space inside an unquoted value makes real YAML read
    # a nested mapping and reject the block.
    for key, value in front.items():
        if isinstance(value, str) and ": " in value \
           and not value.startswith(('"', "'", ">", "|", "{")):
            faults.append(f"`{key}:` is a plain scalar holding ': ', which "
                          "a YAML reader takes as a nested mapping")
    if "timestamp" in front:
        faults.append("`timestamp:` was retired by OKF v0.2; the content's "
                      "last change is `generated: {by, at}`")
    if "verified_at" in front:
        faults.append("`verified_at:` is not an OKF field - a verification "
                      "is `verified: {by, at}`")
    named = front.get("sources") or []
    for one in named:
        target = resolved(bundle, one)
        if target is not None and not target.exists():
            faults.append(f"sources names `{one}`, which does not exist")
    if kind == "File":
        if not named:
            faults.append("a File concept names at least one source")
        for one in named:
            if not one.startswith(CODE_URL):
                faults.append("a File concept's source is a URL into the "
                              f"code repo, `{CODE_URL}<path>`, not `{one}`")
    return faults

def bound(bundle, path, text):
    """References out of one concept that land nowhere."""
    faults = []
    for target in WIKI.findall(text):
        faults.append(f"`[[{target}]]` is not an OKF link; write "
                      "[title](/dir/name.md)")
    for target in LINK.findall(text):
        if not target.startswith(("http://", "https://")):
            where = bundle / target[1:] if target.startswith("/") \
                else path.parent / target
            if not where.resolve().exists():
                faults.append(f"link `{target}` does not resolve")
    return faults

def scratch(rel):
    """./tmp is the scratch convention and a dot directory is tooling;
    neither holds a source this bundle covers."""
    parts = rel.split("/")
    return parts[0] == "tmp" or any(p.startswith(".") for p in parts[:-1])

def pointers():
    """A reference into the bundle from a source file, in either spelling."""
    faults = []
    for area in COVERED:
        for one in sorted((ROOT / area).rglob("*")):
            rel = one.relative_to(ROOT).as_posix()
            skip = one.name == "okf_lint.py" or rel in VENDORED or scratch(rel)
            if one.suffix in SOURCE_SUFFIX and not skip:
                text = one.read_text()
                found = set(POINTER.findall(text))
                found |= {f"[[{n}]]" for n in set(WIKI.findall(text))}
                for target in sorted(found):
                    faults.append(f"{rel} points at `{target}` - source "
                                  "files carry no bundle references")
    return faults

def covered(found):
    """Source files in the covered areas with no File entry; an entry
    elsewhere (scripts, config, project.yml) only has to name a real file.
    A covered entry that is a file covers itself, for a fork that owns a
    few files of a large directory."""
    entries = {}
    for path in found:
        front = frontmatter(path.read_text())
        if front.get("type") == "File":
            for one in front.get("sources") or []:
                if one.startswith(CODE_URL):
                    entries[one[len(CODE_URL):]] = path
    have = {one.relative_to(ROOT).as_posix() for area in COVERED
            for one in ([ROOT / area] if (ROOT / area).is_file()
                        else (ROOT / area).rglob("*"))
            if one.suffix in SOURCE_SUFFIX
            and not scratch(one.relative_to(ROOT).as_posix())}
    return [f"{one} has no File entry" for one in sorted(have - set(entries))]

def listed(bundle):
    """The root index: only okf_version in its frontmatter (OKF v0.2
    section 8), and every directory of the bundle listed in its body."""
    index = bundle / "index.md"
    text = index.read_text() if index.exists() else ""
    faults = []
    front = frontmatter(text)
    for key in front:
        if key != "okf_version":
            faults.append(f"index.md carries `{key}:`; a bundle-root index "
                          "may carry only okf_version (OKF v0.2 section 8)")
    if front.get("okf_version", "").strip('"') != "0.2":
        faults.append("index.md does not declare okf_version \"0.2\"")
    for one in sorted(p for p in bundle.iterdir()
                      if p.is_dir() and not p.name.startswith(".")):
        if f"]({one.name}/)" not in text:
            faults.append(f"index.md does not list `{one.name}/`")
    return faults

def main(argv):
    bundle = DEFAULT_BUNDLE
    if "--bundle" in argv:
        bundle = pathlib.Path(argv[argv.index("--bundle") + 1])
    bundle = bundle.resolve()
    reported = 0
    if not (bundle / "index.md").exists():
        print(f"okf: no bundle at {bundle}")
        reported += 1
    elif not CODE_URL:
        print("okf: okf.conf names no code_url")
        reported += 1
    else:
        types = vocabulary(bundle)
        found = concepts(bundle)
        if not types:
            print(f"  {VOCAB} declares no type vocabulary")
            reported += 1
        for path in found:
            text = path.read_text()
            faults = (shaped(bundle, path, frontmatter(text), types)
                      + bound(bundle, path, text))
            for fault in faults:
                print(f"  {path.relative_to(bundle)}: {fault}")
            reported += len(faults)
        for fault in pointers() + listed(bundle) + covered(found):
            print(f"  {fault}")
            reported += 1
        print(f"okf: {reported} fault(s) over {len(found)} concepts")
    return 1 if reported else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
