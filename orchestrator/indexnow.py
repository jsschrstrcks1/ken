#!/usr/bin/env python3
"""
indexnow.py — Submit URLs to IndexNow for instant search engine indexing.

Notifies Bing, Yandex, Naver, Seznam, and Yep when pages are created or updated.
Uses the shared IndexNow endpoint (api.indexnow.org) — one POST reaches all
participating search engines.

No external dependencies — uses urllib (stdlib) like perplexity.py and youdotcom.py.

Usage:
    python3 indexnow.py submit <domain> <path1> [path2 ...]
    python3 indexnow.py bulk <sitemap.xml> <domain>
    python3 indexnow.py auto <file_path>

Examples:
    python3 indexnow.py submit cruisinginthewake.com ships/wonder-of-the-seas.html
    python3 indexnow.py bulk /home/user/InTheWake/sitemap.xml cruisinginthewake.com
    python3 indexnow.py auto /home/user/InTheWake/ships/wonder-of-the-seas.html
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

# ── Configuration ───────────────────────────────────────────────────

API_KEY = "68e691d21e304db593e4aaac3b92e9e4"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH_SIZE = 500  # URLs per request (conservative; max is 10,000)

# Map repo directory names to domains
DOMAIN_MAP = {
    "InTheWake": "cruisinginthewake.com",
    "ken": "ken-baker.com",
}

# Paths to skip (not content pages)
SKIP_PATHS = {
    "offline.html",
    "search.html",
}


# ── Core Submission ─────────────────────────────────────────────────

def submit_urls(domain, urls):
    """Submit a list of URLs to IndexNow in batches.

    Returns:
        dict with counts: submitted, accepted, failed, errors
    """
    if not urls:
        print("No URLs to submit.", file=sys.stderr)
        return {"submitted": 0, "accepted": 0, "failed": 0, "errors": []}

    key_location = f"https://{domain}/{API_KEY}.txt"
    total = len(urls)
    results = {"submitted": 0, "accepted": 0, "failed": 0, "errors": []}

    # Batch into chunks
    batches = [urls[i:i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]

    print(f"Submitting {total} URLs in {len(batches)} batch(es) to IndexNow...",
          file=sys.stderr)

    for batch_num, batch in enumerate(batches, 1):
        payload = {
            "host": domain,
            "key": API_KEY,
            "keyLocation": key_location,
            "urlList": batch,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            ENDPOINT,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.getcode()
                results["submitted"] += len(batch)

                if status == 200:
                    results["accepted"] += len(batch)
                    print(f"  Batch {batch_num}/{len(batches)}: "
                          f"{len(batch)} URLs — 200 OK", file=sys.stderr)
                elif status == 202:
                    results["accepted"] += len(batch)
                    print(f"  Batch {batch_num}/{len(batches)}: "
                          f"{len(batch)} URLs — 202 Accepted (pending verification)",
                          file=sys.stderr)

        except urllib.error.HTTPError as e:
            status = e.code
            results["failed"] += len(batch)

            if status == 422:
                msg = f"Batch {batch_num}: 422 Unprocessable Entity (invalid URLs or payload)"
            elif status == 429:
                msg = f"Batch {batch_num}: 429 Rate Limited — wait and retry"
            elif status == 403:
                msg = f"Batch {batch_num}: 403 Forbidden — check API key and key file"
            else:
                msg = f"Batch {batch_num}: HTTP {status}"

            results["errors"].append(msg)
            print(f"  {msg}", file=sys.stderr)

            # On rate limit, wait before next batch
            if status == 429 and batch_num < len(batches):
                wait = min(60 * (2 ** (batch_num - 1)), 300)
                print(f"  Waiting {wait}s before next batch...", file=sys.stderr)
                time.sleep(wait)

        except Exception as e:
            results["failed"] += len(batch)
            msg = f"Batch {batch_num}: {e}"
            results["errors"].append(msg)
            print(f"  {msg}", file=sys.stderr)

        # Brief pause between batches to be respectful
        if batch_num < len(batches):
            time.sleep(1)

    # Summary
    print(f"\nIndexNow: {results['accepted']}/{total} accepted, "
          f"{results['failed']} failed", file=sys.stderr)

    return results


# ── Commands ────────────────────────────────────────────────────────

def cmd_submit(domain, paths):
    """Submit specific URL paths for a domain."""
    urls = []
    for path in paths:
        path = path.lstrip("/")
        if os.path.basename(path) in SKIP_PATHS:
            continue
        url = f"https://{domain}/{path}"
        urls.append(url)

    return submit_urls(domain, urls)


def cmd_bulk(sitemap_path, domain):
    """Parse a sitemap.xml and submit all URLs."""
    if not os.path.exists(sitemap_path):
        print(f"Error: Sitemap not found: {sitemap_path}", file=sys.stderr)
        sys.exit(1)

    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Handle XML namespace
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []

    for url_elem in root.findall("sm:url", ns):
        loc = url_elem.find("sm:loc", ns)
        if loc is not None and loc.text:
            url = loc.text.strip()
            # Skip non-content pages
            basename = os.path.basename(url)
            if basename in SKIP_PATHS:
                continue
            urls.append(url)

    if not urls:
        # Try without namespace (some sitemaps don't use it)
        for url_elem in root.findall("url"):
            loc = url_elem.find("loc")
            if loc is not None and loc.text:
                url = loc.text.strip()
                basename = os.path.basename(url)
                if basename in SKIP_PATHS:
                    continue
                urls.append(url)

    print(f"Found {len(urls)} URLs in sitemap", file=sys.stderr)
    return submit_urls(domain, urls)


def cmd_auto(file_path):
    """Auto-detect domain from file path and submit a single URL."""
    abs_path = os.path.abspath(file_path)

    # Detect which repo this file belongs to
    domain = None
    rel_path = None

    for repo_name, repo_domain in DOMAIN_MAP.items():
        # Check if the file path contains the repo name
        repo_marker = f"/{repo_name}/"
        if repo_marker in abs_path:
            domain = repo_domain
            # Extract relative path after repo directory
            idx = abs_path.index(repo_marker) + len(repo_marker)
            rel_path = abs_path[idx:]
            break

    if not domain:
        print(f"Could not detect domain for: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not rel_path or not rel_path.endswith(".html"):
        print(f"Not an HTML file: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Skip non-content files
    if os.path.basename(rel_path) in SKIP_PATHS:
        print(f"Skipped (non-content): {rel_path}", file=sys.stderr)
        return {"submitted": 0, "accepted": 0, "failed": 0, "errors": []}

    url = f"https://{domain}/{rel_path}"
    print(f"Auto-detected: {domain} → {url}", file=sys.stderr)
    return submit_urls(domain, [url])


# ── Main ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "submit":
        if len(sys.argv) < 4:
            print("Usage: python3 indexnow.py submit <domain> <path1> [path2 ...]")
            sys.exit(1)
        domain = sys.argv[2]
        paths = sys.argv[3:]
        result = cmd_submit(domain, paths)

    elif command == "bulk":
        if len(sys.argv) < 4:
            print("Usage: python3 indexnow.py bulk <sitemap.xml> <domain>")
            sys.exit(1)
        sitemap_path = sys.argv[2]
        domain = sys.argv[3]
        result = cmd_bulk(sitemap_path, domain)

    elif command == "auto":
        if len(sys.argv) < 3:
            print("Usage: python3 indexnow.py auto <file_path>")
            sys.exit(1)
        file_path = sys.argv[2]
        result = cmd_auto(file_path)

    else:
        print(f"Unknown command: {command}")
        print("Commands: submit, bulk, auto")
        sys.exit(1)

    # Output result as JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
