#!/usr/bin/env python3
"""Fetch latest HN trends and update the dataset."""

import json
import csv
import io
import urllib.request
from datetime import datetime


def fetch_hn_top_stories(limit=30):
    """Get top stories from HN API."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = json.loads(urllib.request.urlopen(url, timeout=10).read())[:limit]

    stories = []
    for sid in ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        item = json.loads(urllib.request.urlopen(item_url, timeout=10).read())
        if item and item.get("type") == "story":
            stories.append({
                "id": item["id"],
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "by": item.get("by", ""),
                "time": datetime.fromtimestamp(item.get("time", 0)).isoformat(),
                "fetched": datetime.utcnow().isoformat()
            })

    return stories


def update_json(filepath, new_stories):
    """Append new stories to JSON file."""
    try:
        with open(filepath) as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    existing_ids = {s["id"] for s in existing}
    added = [s for s in new_stories if s["id"] not in existing_ids]
    existing.extend(added)

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return len(added)


def update_csv(filepath, new_stories):
    """Append new stories to CSV file."""
    fields = ["id", "title", "url", "score", "comments", "by", "time", "fetched"]
    try:
        with open(filepath) as f:
            reader = csv.DictReader(f)
            existing = list(reader)
            existing_ids = {int(r["id"]) for r in existing}
    except FileNotFoundError:
        existing = []
        existing_ids = set()

    added = [s for s in new_stories if s["id"] not in existing_ids]

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in existing + added:
            writer.writerow(row)

    return len(added)


if __name__ == "__main__":
    print(f"Fetching HN top stories at {datetime.utcnow().isoformat()}...")
    stories = fetch_hn_top_stories(30)
    print(f"Fetched {len(stories)} stories")

    added_json = update_json("hn-tech-trends-2026.json", stories)
    added_csv = update_csv("hn-tech-trends-2026.csv", stories)
    print(f"Added {added_json} new stories to JSON, {added_csv} to CSV")
