#!/usr/bin/env python3
"""
Claude Code documentation fetcher for cc-docs skill.

Fetches official Claude Code documentation and updates the skill's references.
Run from anywhere - automatically detects skill directory structure.

Usage:
    python fetch.py              # Fetch docs and validate SKILL.md
    python fetch.py --validate   # Only validate SKILL.md against fetched files
    python fetch.py --update-skill  # Also update SKILL.md with new files
"""

import requests
import time
from pathlib import Path
from typing import List, Tuple, Set, Optional, Dict
import logging
from datetime import datetime
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import json
import hashlib
import re
import random
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Sitemap URLs to try (in order of preference)
SITEMAP_URLS = [
    "https://code.claude.com/docs/sitemap.xml",
    "https://docs.anthropic.com/sitemap.xml",
]

MANIFEST_FILE = "docs_manifest.json"
SKILL_FILE = "SKILL.md"

# Headers for requests
HEADERS = {
    'User-Agent': 'Claude-Code-Docs-Fetcher/3.0 (cc-docs-skill)',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_RETRY_DELAY = 30
RATE_LIMIT_DELAY = 0.5


def get_skill_dir() -> Path:
    """Get the skill directory (parent of scripts/)."""
    return Path(__file__).parent.parent


def get_references_dir() -> Path:
    """Get the references directory."""
    return get_skill_dir() / "references"


def load_manifest() -> dict:
    """Load the manifest of previously fetched files."""
    manifest_path = get_references_dir() / MANIFEST_FILE
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if "files" not in manifest:
                manifest["files"] = {}
            return manifest
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
    return {"files": {}, "last_updated": None}


def save_manifest(manifest: dict) -> None:
    """Save the manifest of fetched files."""
    manifest_path = get_references_dir() / MANIFEST_FILE
    manifest["last_updated"] = datetime.now().isoformat()
    manifest["description"] = "Claude Code documentation manifest for cc-docs skill."
    manifest_path.write_text(json.dumps(manifest, indent=2))


def url_to_safe_filename(url_path: str) -> str:
    """Convert a URL path to a safe filename."""
    for prefix in ['/docs/en/', '/en/docs/claude-code/', '/docs/claude-code/', '/claude-code/']:
        if prefix in url_path:
            path = url_path.split(prefix)[-1]
            break
    else:
        if 'claude-code/' in url_path:
            path = url_path.split('claude-code/')[-1]
        else:
            path = url_path

    if '/' not in path:
        return path + '.md' if not path.endswith('.md') else path

    safe_name = path.replace('/', '__')
    if not safe_name.endswith('.md'):
        safe_name += '.md'
    return safe_name


def discover_sitemap_and_base_url(session: requests.Session) -> Tuple[str, str]:
    """Discover the sitemap URL and extract the base URL from it."""
    for sitemap_url in SITEMAP_URLS:
        try:
            logger.info(f"Trying sitemap: {sitemap_url}")
            response = session.get(sitemap_url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                try:
                    parser = ET.XMLParser(forbid_dtd=True, forbid_entities=True, forbid_external=True)
                    root = ET.fromstring(response.content, parser=parser)
                except TypeError:
                    root = ET.fromstring(response.content)

                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                first_url = None
                for url_elem in root.findall('.//ns:url', namespace):
                    loc_elem = url_elem.find('ns:loc', namespace)
                    if loc_elem is not None and loc_elem.text:
                        first_url = loc_elem.text
                        break

                if not first_url:
                    for loc_elem in root.findall('.//loc'):
                        if loc_elem.text:
                            first_url = loc_elem.text
                            break

                if first_url:
                    parsed = urlparse(first_url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    logger.info(f"Found sitemap at {sitemap_url}, base URL: {base_url}")
                    return sitemap_url, base_url
        except Exception as e:
            logger.warning(f"Failed to fetch {sitemap_url}: {e}")
            continue

    raise Exception("Could not find a valid sitemap")


def discover_claude_code_pages(session: requests.Session, sitemap_url: str) -> List[str]:
    """Discover all Claude Code documentation pages from the sitemap."""
    logger.info("Discovering documentation pages from sitemap...")

    try:
        response = session.get(sitemap_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        try:
            parser = ET.XMLParser(forbid_dtd=True, forbid_entities=True, forbid_external=True)
            root = ET.fromstring(response.content, parser=parser)
        except TypeError:
            root = ET.fromstring(response.content)

        urls = []
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url_elem in root.findall('.//ns:url', namespace):
            loc_elem = url_elem.find('ns:loc', namespace)
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text)

        if not urls:
            for loc_elem in root.findall('.//loc'):
                if loc_elem.text:
                    urls.append(loc_elem.text)

        logger.info(f"Found {len(urls)} total URLs in sitemap")

        claude_code_pages = []
        english_patterns = ['/docs/en/', '/en/docs/claude-code/']

        for url in urls:
            if any(pattern in url for pattern in english_patterns):
                parsed = urlparse(url)
                path = parsed.path

                if path.endswith('.html'):
                    path = path[:-5]
                elif path.endswith('/'):
                    path = path[:-1]

                skip_patterns = ['/tool-use/', '/examples/', '/legacy/', '/api/', '/reference/']
                if not any(skip in path for skip in skip_patterns):
                    claude_code_pages.append(path)

        claude_code_pages = sorted(list(set(claude_code_pages)))
        logger.info(f"Discovered {len(claude_code_pages)} Claude Code documentation pages")
        return claude_code_pages

    except Exception as e:
        logger.error(f"Failed to discover pages from sitemap: {e}")
        return get_fallback_pages()


def get_fallback_pages() -> List[str]:
    """Fallback list of essential pages."""
    return [
        "/docs/en/overview",
        "/docs/en/setup",
        "/docs/en/quickstart",
        "/docs/en/memory",
        "/docs/en/common-workflows",
        "/docs/en/mcp",
        "/docs/en/github-actions",
        "/docs/en/troubleshooting",
        "/docs/en/security",
        "/docs/en/settings",
        "/docs/en/hooks",
        "/docs/en/costs",
        "/docs/en/monitoring-usage",
    ]


def validate_markdown_content(content: str, filename: str) -> None:
    """Validate that content is proper markdown."""
    if not content or content.startswith('<!DOCTYPE') or '<html' in content[:100]:
        raise ValueError("Received HTML instead of markdown")

    if len(content.strip()) < 50:
        raise ValueError(f"Content too short ({len(content)} bytes)")

    lines = content.split('\n')
    markdown_indicators = ['# ', '## ', '### ', '```', '- ', '* ', '1. ', '[', '**', '_', '> ']

    indicator_count = 0
    for line in lines[:50]:
        for indicator in markdown_indicators:
            if line.strip().startswith(indicator) or indicator in line:
                indicator_count += 1
                break

    if indicator_count < 3:
        raise ValueError(f"Content doesn't appear to be markdown (only {indicator_count} indicators)")


def fetch_markdown_content(path: str, session: requests.Session, base_url: str) -> Tuple[str, str]:
    """Fetch markdown content with retry logic."""
    markdown_url = f"{base_url}{path}.md"
    filename = url_to_safe_filename(path)

    logger.info(f"Fetching: {markdown_url} -> {filename}")

    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(markdown_url, headers=HEADERS, timeout=30, allow_redirects=True)

            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            content = response.text
            validate_markdown_content(content, filename)

            logger.info(f"Successfully fetched {filename} ({len(content)} bytes)")
            return filename, content

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {filename}: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = min(RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
                jittered_delay = delay * random.uniform(0.5, 1.0)
                time.sleep(jittered_delay)
            else:
                raise Exception(f"Failed to fetch {filename} after {MAX_RETRIES} attempts: {e}")

        except ValueError as e:
            logger.error(f"Content validation failed for {filename}: {e}")
            raise


def fetch_changelog(session: requests.Session) -> Tuple[str, str]:
    """Fetch Claude Code changelog from GitHub."""
    changelog_url = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
    filename = "changelog.md"

    logger.info(f"Fetching changelog: {changelog_url}")

    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(changelog_url, headers=HEADERS, timeout=30)

            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            content = response.text

            header = """# Claude Code Changelog

> **Source**: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

---

"""
            content = header + content

            if len(content.strip()) < 100:
                raise ValueError(f"Changelog too short ({len(content)} bytes)")

            logger.info(f"Successfully fetched changelog ({len(content)} bytes)")
            return filename, content

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for changelog: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = min(RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY)
                time.sleep(delay * random.uniform(0.5, 1.0))
            else:
                raise Exception(f"Failed to fetch changelog: {e}")


def content_has_changed(content: str, old_hash: str) -> bool:
    """Check if content has changed based on hash."""
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return new_hash != old_hash


def save_markdown_file(filename: str, content: str) -> str:
    """Save markdown content and return its hash."""
    file_path = get_references_dir() / filename
    file_path.write_text(content, encoding='utf-8')
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    logger.info(f"Saved: {filename}")
    return content_hash


def cleanup_old_files(current_files: Set[str], manifest: dict) -> None:
    """Remove files that were previously fetched but no longer exist."""
    previous_files = set(manifest.get("files", {}).keys())
    files_to_remove = previous_files - current_files

    protected_files = {MANIFEST_FILE, "README.md"}

    for filename in files_to_remove:
        if filename in protected_files:
            continue
        file_path = get_references_dir() / filename
        if file_path.exists():
            logger.info(f"Removing obsolete file: {filename}")
            file_path.unlink()


def get_skill_md_references() -> Set[str]:
    """Parse SKILL.md and extract all referenced files."""
    skill_path = get_skill_dir() / SKILL_FILE
    if not skill_path.exists():
        return set()

    content = skill_path.read_text()
    # Match patterns like `references/filename.md` or references/filename.md
    pattern = r'`?references/([^`\s]+\.(?:md|json))`?'
    matches = re.findall(pattern, content)
    return set(matches)


def validate_skill_md(fetched_files: Set[str]) -> Dict[str, List[str]]:
    """Validate SKILL.md references against fetched files."""
    referenced = get_skill_md_references()

    # Files in SKILL.md but not fetched
    orphaned = referenced - fetched_files - {"README.md", "docs_manifest.json"}

    # Files fetched but not in SKILL.md
    unreferenced = fetched_files - referenced - {"README.md", "docs_manifest.json"}

    return {
        "orphaned": sorted(list(orphaned)),
        "unreferenced": sorted(list(unreferenced))
    }


def update_skill_md_uncategorized(new_files: List[str]) -> None:
    """Append new files to an Uncategorized section in SKILL.md."""
    if not new_files:
        return

    skill_path = get_skill_dir() / SKILL_FILE
    content = skill_path.read_text()

    # Check if Uncategorized section exists
    if "### Uncategorized (New)" not in content:
        uncategorized_section = "\n\n### Uncategorized (New)\n\n"
        uncategorized_section += "<!-- Review and move these to appropriate sections -->\n\n"
    else:
        uncategorized_section = ""

    for filename in new_files:
        uncategorized_section += f"- `references/{filename}` - (new, needs categorization)\n"

    # Append to end of file
    content = content.rstrip() + uncategorized_section
    skill_path.write_text(content)
    logger.info(f"Added {len(new_files)} new files to Uncategorized section in SKILL.md")


def fetch_docs() -> Tuple[int, int, Set[str]]:
    """Fetch all documentation. Returns (successful, failed, fetched_files)."""
    start_time = datetime.now()
    logger.info("Starting Claude Code documentation fetch")

    refs_dir = get_references_dir()
    refs_dir.mkdir(exist_ok=True)

    manifest = load_manifest()

    successful = 0
    failed = 0
    failed_pages = []
    fetched_files = set()
    new_manifest = {"files": {}}

    with requests.Session() as session:
        try:
            sitemap_url, base_url = discover_sitemap_and_base_url(session)
        except Exception as e:
            logger.error(f"Failed to discover sitemap: {e}")
            base_url = "https://code.claude.com"
            sitemap_url = None

        if sitemap_url:
            documentation_pages = discover_claude_code_pages(session, sitemap_url)
        else:
            documentation_pages = get_fallback_pages()

        if not documentation_pages:
            logger.error("No documentation pages discovered!")
            sys.exit(1)

        # Fetch each page
        for i, page_path in enumerate(documentation_pages, 1):
            logger.info(f"Processing {i}/{len(documentation_pages)}: {page_path}")

            try:
                filename, content = fetch_markdown_content(page_path, session, base_url)

                old_hash = manifest.get("files", {}).get(filename, {}).get("hash", "")
                old_entry = manifest.get("files", {}).get(filename, {})

                if content_has_changed(content, old_hash):
                    content_hash = save_markdown_file(filename, content)
                    last_updated = datetime.now().isoformat()
                else:
                    content_hash = old_hash
                    last_updated = old_entry.get("last_updated", datetime.now().isoformat())

                new_manifest["files"][filename] = {
                    "original_url": f"{base_url}{page_path}",
                    "hash": content_hash,
                    "last_updated": last_updated
                }

                fetched_files.add(filename)
                successful += 1

                if i < len(documentation_pages):
                    time.sleep(RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error(f"Failed to process {page_path}: {e}")
                failed += 1
                failed_pages.append(page_path)

        # Fetch changelog
        try:
            filename, content = fetch_changelog(session)
            old_hash = manifest.get("files", {}).get(filename, {}).get("hash", "")
            old_entry = manifest.get("files", {}).get(filename, {})

            if content_has_changed(content, old_hash):
                content_hash = save_markdown_file(filename, content)
                last_updated = datetime.now().isoformat()
            else:
                content_hash = old_hash
                last_updated = old_entry.get("last_updated", datetime.now().isoformat())

            new_manifest["files"][filename] = {
                "original_url": "https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md",
                "hash": content_hash,
                "last_updated": last_updated,
                "source": "github"
            }

            fetched_files.add(filename)
            successful += 1

        except Exception as e:
            logger.error(f"Failed to fetch changelog: {e}")
            failed += 1

    # Cleanup old files
    cleanup_old_files(fetched_files, manifest)

    # Save manifest
    new_manifest["fetch_metadata"] = {
        "last_fetch": datetime.now().isoformat(),
        "duration_seconds": (datetime.now() - start_time).total_seconds(),
        "successful": successful,
        "failed": failed,
        "failed_pages": failed_pages,
        "sitemap_url": sitemap_url,
        "base_url": base_url
    }
    save_manifest(new_manifest)

    logger.info(f"\nFetch completed: {successful} successful, {failed} failed")

    return successful, failed, fetched_files


def main():
    parser = argparse.ArgumentParser(description="Fetch Claude Code documentation for cc-docs skill")
    parser.add_argument("--validate", action="store_true", help="Only validate SKILL.md against existing files")
    parser.add_argument("--update-skill", action="store_true", help="Update SKILL.md with new unreferenced files")
    args = parser.parse_args()

    if args.validate:
        # Just validate against existing files
        refs_dir = get_references_dir()
        existing_files = {f.name for f in refs_dir.glob("*.md")} | {f.name for f in refs_dir.glob("*.json")}
        validation = validate_skill_md(existing_files)
    else:
        # Fetch docs
        successful, failed, fetched_files = fetch_docs()

        if successful == 0:
            logger.error("No pages fetched successfully!")
            sys.exit(1)

        # Validate SKILL.md
        validation = validate_skill_md(fetched_files)

    # Report validation results
    if validation["orphaned"]:
        logger.warning(f"\nOrphaned references in SKILL.md (files don't exist):")
        for f in validation["orphaned"]:
            logger.warning(f"  - {f}")

    if validation["unreferenced"]:
        logger.info(f"\nUnreferenced files (not in SKILL.md):")
        for f in validation["unreferenced"]:
            logger.info(f"  - {f}")

        if args.update_skill:
            update_skill_md_uncategorized(validation["unreferenced"])

    if not validation["orphaned"] and not validation["unreferenced"]:
        logger.info("\nSKILL.md is in sync with fetched files!")


if __name__ == "__main__":
    main()
