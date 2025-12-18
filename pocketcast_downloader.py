#!/usr/bin/env python3
"""
Pocket Casts Favorited Podcasts Downloader

This script downloads all podcasts that you have favorited in the PocketCasts app.
By default it will download all podcasts that were published in the current year.
You can also either pick a particular year or download all years.
To use this you need to get the Pocket Casts app session token from your browser.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import argparse
import certifi
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, COMM, APIC
from mutagen.mp4 import MP4, MP4Cover
from mutagen import File as MutagenFile


class PocketCastsAPI:
    """Client for interacting with the Pocket Casts API"""

    BASE_URL = "https://api.pocketcasts.com"
    WEB_URL = "https://play.pocketcasts.com"

    def __init__(self, token=None, verify_ssl=True):
        self.session = requests.Session()
        self.token = token
        self.verify_ssl = verify_ssl

        if verify_ssl:
            try:
                self.session.verify = certifi.where()
            except Exception:
                self.session.verify = True
        else:
            self.session.verify = False
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.session.cookies.set("accessToken", self.token)

    def set_token(self, token: str):
        """Set the authentication token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.session.cookies.set("accessToken", self.token)

    def verify_auth(self):
        """Verify that the authentication token works"""
        url = f"{self.BASE_URL}/user/starred"

        try:
            response = self.session.post(url)
            response.raise_for_status()
            print("✓ Successfully authenticated with Pocket Casts")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            print("\nPlease check your token is correct and not expired.")
            return False

    def get_starred_episodes(self):
        """Get all starred/favorited episodes"""
        url = f"{self.BASE_URL}/user/starred"

        try:
            response = self.session.post(url)
            response.raise_for_status()
            data = response.json()
            episodes = data.get("episodes", [])
            print(f"✓ Found {len(episodes)} starred episodes")
            return episodes
        except Exception as e:
            print(f"✗ Failed to get starred episodes: {e}")
            return []

    def get_episode_info(self, episode_uuid):
        """Get detailed information about an episode"""
        url = f"{self.BASE_URL}/user/episode"
        payload = {"uuid": episode_uuid}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Failed to get episode info: {e}")
            return None


class PodcastDownloader:
    """Downloads podcast episodes"""

    def __init__(self, download_dir="./downloads", verify_ssl=True, debug=False):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.verify_ssl = verify_ssl
        self.debug = debug

        if verify_ssl:
            try:
                self.verify = certifi.where()
            except Exception:
                self.verify = True
        else:
            self.verify = False

    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        filename = filename.replace("|", "-")
        filename = filename.replace(":", " -")

        invalid_chars = '<>"/\\?*'
        for char in invalid_chars:
            filename = filename.replace(char, "")

        filename = " ".join(filename.split())

        return filename

    def set_metadata(self, filepath, episode):
        """
        Set metadata tags (ID3 for MP3, iTunes tags for M4A) on the downloaded file.
        Only adds tags if they don't already exist - preserves any existing metadata.

        Tags set:
        - Title: Episode title
        - Artist: Podcast name
        - Album: Podcast name
        - Year: Published year
        - Genre: "Podcast"
        """
        try:
            audio = MutagenFile(filepath, easy=False)

            if audio is None:
                return

            title = episode.get("title", "")
            podcast_title = episode.get("podcastTitle", "")
            published = episode.get("published", "")

            original_title = title
            if title and podcast_title:
                title_lower = title.lower()
                podcast_lower = podcast_title.lower()
                
                if self.debug:
                    print(f"  🔍 DEBUG: Checking title enhancement")
                    print(f"      Original title: '{title}' (length: {len(title)})")
                    print(f"      Podcast name: '{podcast_title}'")
                    print(f"      Title too short (<15 chars): {len(title) < 15}")
                    print(f"      Podcast name in title: {podcast_lower in title_lower}")

                needs_enhancement = len(title) < 15 and podcast_lower not in title_lower
                
                if self.debug:
                    print(f"      Needs enhancement (short AND no podcast name): {needs_enhancement}")
                
                if needs_enhancement:
                    title = f"{podcast_title} - {title}"
                    if self.debug:
                        print(f"      ✏️  Enhanced to: '{title}'")

            year = ""
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    year = str(pub_date.year)
                except Exception:
                    pass

            tags_added = []

            if isinstance(audio, MP3):
                if audio.tags is None:
                    audio.add_tags()

                existing_title = None
                existing_title_frames = audio.tags.getall("TIT2")
                if existing_title_frames:
                    existing_title = str(existing_title_frames[0])

                should_update_title = False
                if existing_title:
                    existing_lower = existing_title.lower()
                    podcast_lower = podcast_title.lower()
                    
                    if self.debug:
                        print(f"  🔍 DEBUG: Checking existing MP3 title for enhancement")
                        print(f"      Existing title: '{existing_title}' (length: {len(existing_title)})")
                        print(f"      Title too short (<15 chars): {len(existing_title) < 15}")
                        print(f"      Podcast name in existing title: {podcast_lower in existing_lower}")
                    
                    should_update = len(existing_title) < 15 and podcast_lower not in existing_lower
                    
                    if self.debug:
                        print(f"      Should update (short AND no podcast name): {should_update}")
                    
                    if should_update:
                        should_update_title = True
                        if self.debug:
                            print(f"      ✏️  Will update to: '{title}'")

                if not existing_title_frames:
                    audio.tags.add(TIT2(encoding=3, text=title))
                    tags_added.append("Title")
                elif should_update_title:
                    audio.tags.delall("TIT2")
                    audio.tags.add(TIT2(encoding=3, text=title))
                    tags_added.append("Title (enhanced)")

                if not audio.tags.getall("TPE1"):
                    audio.tags.add(TPE1(encoding=3, text=podcast_title))
                    tags_added.append("Artist")
                if not audio.tags.getall("TALB"):
                    audio.tags.add(TALB(encoding=3, text=podcast_title))
                    tags_added.append("Album")
                if year and not audio.tags.getall("TDRC"):
                    audio.tags.add(TDRC(encoding=3, text=year))
                    tags_added.append("Year")
                if not audio.tags.getall("TCON"):
                    audio.tags.add(TCON(encoding=3, text="Podcast"))
                    tags_added.append("Genre")

            elif isinstance(audio, MP4):
                existing_title = None
                if "\xa9nam" in audio:
                    existing_title = str(audio["\xa9nam"][0])

                should_update_title = False
                if existing_title:
                    existing_lower = existing_title.lower()
                    podcast_lower = podcast_title.lower()
                    
                    if self.debug:
                        print(f"  🔍 DEBUG: Checking existing M4A title for enhancement")
                        print(f"      Existing title: '{existing_title}' (length: {len(existing_title)})")
                        print(f"      Title too short (<15 chars): {len(existing_title) < 15}")
                        print(f"      Podcast name in existing title: {podcast_lower in existing_lower}")
                    
                    should_update = len(existing_title) < 15 and podcast_lower not in existing_lower
                    
                    if self.debug:
                        print(f"      Should update (short AND no podcast name): {should_update}")
                    
                    if should_update:
                        should_update_title = True
                        if self.debug:
                            print(f"      ✏️  Will update to: '{title}'")

                if "\xa9nam" not in audio:
                    audio["\xa9nam"] = title
                    tags_added.append("Title")
                elif should_update_title:
                    # Update existing short/generic title
                    audio["\xa9nam"] = title
                    tags_added.append("Title (enhanced)")

                if "\xa9ART" not in audio:
                    audio["\xa9ART"] = podcast_title
                    tags_added.append("Artist")
                if "\xa9alb" not in audio:
                    audio["\xa9alb"] = podcast_title
                    tags_added.append("Album")
                if year and "\xa9day" not in audio:
                    audio["\xa9day"] = year
                    tags_added.append("Year")
                if "\xa9gen" not in audio:
                    audio["\xa9gen"] = "Podcast"
                    tags_added.append("Genre")

            if tags_added:
                audio.save()
                print(f"  ℹ️  Added metadata: {', '.join(tags_added)}")
            else:
                print(f"  ℹ️  All metadata tags already exist")

        except Exception as e:
            print(f"  ⚠️  Could not set metadata: {e}")

    def download_episode(self, episode, organize_by_podcast=False):
        """Download a single episode"""
        try:
            title = episode.get("title", "Unknown")
            podcast_title = episode.get("podcastTitle", "Unknown Podcast")
            url = episode.get("url")

            if not url:
                print(f"✗ No download URL for: {title}")
                return False

            ext = ".mp3"
            if "." in url.split("/")[-1]:
                ext = "." + url.split(".")[-1].split("?")[0]

            if organize_by_podcast:
                podcast_dir = self.download_dir / self.sanitize_filename(podcast_title)
                podcast_dir.mkdir(parents=True, exist_ok=True)
                filename = self.sanitize_filename(title) + ext
                filepath = podcast_dir / filename
            else:
                filename = self.sanitize_filename(title) + ext
                filepath = self.download_dir / filename

            if filepath.exists():
                print(f"⊘ Already exists: {filename}")
                self.set_metadata(filepath, episode)
                return True

            print(f"↓ Downloading: {title}")
            response = requests.get(url, stream=True, timeout=30, verify=self.verify)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"  Progress: {percent:.1f}%", end="\r")

            print(f"\n✓ Downloaded: {filename}")

            self.set_metadata(filepath, episode)

            return True

        except Exception as e:
            print(f"✗ Failed to download {episode.get('title', 'Unknown')}: {e}")
            return False


def filter_episodes_by_year(episodes, year):
    """Filter episodes by publish date"""
    filtered = []

    for episode in episodes:
        published = episode.get("published")

        if not published:
            continue

        try:
            episode_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if episode_date.year == year:
                filtered.append(episode)
        except Exception:
            continue

    return filtered


def main():
    parser = argparse.ArgumentParser(
        description="Download favorited podcasts from Pocket Casts",
    )
    parser.add_argument(
        "--token", required=True, help="Pocket Casts access token from browser"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="Year to filter favorited episodes (default: current year)",
    )
    parser.add_argument(
        "--output-dir",
        default="./downloads",
        help="Directory to save downloaded episodes (default: ./downloads)",
    )
    parser.add_argument(
        "--save-metadata", action="store_true", help="Save episode metadata as JSON"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification (use if you get SSL errors)",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all starred episodes (ignore year filter)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )
    parser.add_argument(
        "--organize-by-podcast",
        action="store_true",
        help="Create separate directories for each podcast (default: include podcast name in filename)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information for title enhancement logic",
    )

    args = parser.parse_args()

    print(f"Pocket Casts Favorited Podcasts Downloader")
    print(f"{'=' * 50}")
    print(f"Year: {args.year}")
    print(f"Output directory: {args.output_dir}")
    if args.no_verify_ssl:
        print(f"SSL verification: DISABLED")
    if args.dry_run:
        print(f"Mode: DRY RUN (no files will be downloaded)")
    print()

    api = PocketCastsAPI(token=args.token, verify_ssl=not args.no_verify_ssl)

    if not api.verify_auth():
        sys.exit(1)

    all_episodes = api.get_starred_episodes()

    if not all_episodes:
        print("No starred episodes found")
        sys.exit(0)

    year_counts_published = {}

    for episode in all_episodes:
        published = episode.get("published")
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                year = pub_date.year
                year_counts_published[year] = year_counts_published.get(year, 0) + 1
            except Exception:
                pass

    if year_counts_published:
        print("\nStarred episodes by published date:")
        for year in sorted(year_counts_published.keys(), reverse=True):
            print(f"  {year}: {year_counts_published[year]} episodes")
        print()

    if args.show_all:
        episodes = all_episodes
        print(f"✓ Downloading all {len(episodes)} starred episodes\n")
    else:
        episodes = filter_episodes_by_year(all_episodes, args.year)
        print(f"✓ Found {len(episodes)} episodes published in {args.year}\n")

    if not episodes:
        if not args.show_all:
            print(f"No episodes found for {args.year}.")
            print("Try using --show-all to download all starred episodes.")
        sys.exit(0)

    if args.save_metadata:
        metadata_file = Path(args.output_dir) / f"metadata_{args.year}.json"
        with open(metadata_file, "w") as f:
            json.dump(episodes, f, indent=2)
        print(f"✓ Saved metadata to {metadata_file}\n")

    downloader = PodcastDownloader(args.output_dir, verify_ssl=not args.no_verify_ssl, debug=args.debug)

    successful = 0
    failed = 0

    if args.dry_run:
        print("DRY RUN - Files that would be downloaded:\n")
        for i, episode in enumerate(episodes, 1):
            title = episode.get("title", "Unknown")
            podcast_title = episode.get("podcastTitle", "Unknown Podcast")
            url = episode.get("url")
            published = episode.get("published", "")

            year = ""
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    year = str(pub_date.year)
                except Exception:
                    pass

            ext = ".mp3"
            if url and "." in url.split("/")[-1]:
                ext = "." + url.split(".")[-1].split("?")[0]

            if args.organize_by_podcast:
                podcast_dir = downloader.sanitize_filename(podcast_title)
                filename = downloader.sanitize_filename(title) + ext
                filepath = f"{args.output_dir}/{podcast_dir}/{filename}"
            else:
                filename = downloader.sanitize_filename(title) + ext
                filepath = f"{args.output_dir}/{filename}"

            print(f"[{i}/{len(episodes)}] {filepath}")
            if url:
                successful += 1
            else:
                print(f"    ⚠️  No download URL available")
                failed += 1
            print()
    else:
        for i, episode in enumerate(episodes, 1):
            print(f"\n[{i}/{len(episodes)}]")
            if downloader.download_episode(
                episode, organize_by_podcast=args.organize_by_podcast
            ):
                successful += 1
            else:
                failed += 1

    print(f"\n{'=' * 50}")
    if args.dry_run:
        print(f"Dry run complete!")
    else:
        print(f"Download complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(episodes)}")


if __name__ == "__main__":
    main()
