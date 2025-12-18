# Pocket Casts Downloader

Download all your favorited podcasts from Pocket Casts, filtered by the year they were published.

## Features

- 🎯 Download episodes published in a specific year (or all starred episodes)
- 📁 Saves files with episode title as filename
- 📂 Optional: Organize downloads into separate podcast directories
- ⚡ Skips already downloaded files
- 📊 Progress tracking for each download
- 🏷️ Automatically adds metadata tags (Title, Artist, Album, Year, Genre, Album Art)
- 🧠 Smart title enhancement - prefixes short/generic titles with podcast name
- 🔄 Updates metadata on existing files (enhances titles, adds missing tags)
- 💾 Optional metadata export to JSON
- 🔒 Works with Google Sign-In accounts
- 🔍 Dry-run mode to preview downloads

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Getting Your Access Token

Since Pocket Casts uses Google Sign-In, you'll need to get your access token from the browser:

1. Open [https://play.pocketcasts.com](https://play.pocketcasts.com) and sign in with Google
2. Open Developer Tools (press `F12` or right-click and select "Inspect")
3. Go to the **Network** tab
4. In the filter box, type "starred" or "user"
5. Click on "Starred" or navigate around in Pocket Casts to trigger some API calls
6. Click on one of the API requests to `api.pocketcasts.com`
7. Look at the **Request Headers** section
8. Find the `Authorization` header - it will look like `Bearer eyJhbGc...`
9. Copy everything after `Bearer ` (the token part)
10. Use this token with the `--token` parameter

## Usage

Basic usage (downloads current year's favorites):

```bash
python pocketcast_downloader.py --token YOUR_ACCESS_TOKEN
```

### Options

- `--token`: Your Pocket Casts access token from browser (required)
- `--year`: Year to filter by publish date (default: current year)
- `--output-dir`: Download directory (default: ./downloads)
- `--show-all`: Download all starred episodes (ignore year filter)
- `--organize-by-podcast`: Create separate directories for each podcast
- `--dry-run`: Show what would be downloaded without downloading
- `--save-metadata`: Save episode metadata as JSON
- `--no-verify-ssl`: Disable SSL verification

### Examples

**Download episodes published in 2024:**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --year 2024
```

**Download all starred episodes:**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --show-all
```

**Organize into podcast directories:**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --organize-by-podcast
```

**Preview what would be downloaded (dry run):**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --dry-run
```

This will show the file paths where episodes will be saved, without actually downloading anything or checking existing metadata.

**Save to a specific directory with metadata:**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
=  --year 2025 \
  --output-dir ~/Podcasts \
  --save-metadata
```

## Metadata Tags

The script automatically adds/updates the following metadata tags on downloaded files:

- **Title**: Episode title (enhanced with podcast name if too short or generic)
- **Artist**: Podcast name
- **Album**: Podcast name
- **Year**: Year the episode was published
- **Genre**: "Podcast"
- **Album Art**: Podcast cover artwork (downloaded and embedded)

This works for both MP3 (ID3 tags) and M4A (iTunes tags) files.

### Smart Title Enhancement

If an episode title is short (< 15 characters) or doesn't reference the podcast name, the script will enhance it by prefixing with the podcast name

This makes episodes easier to identify in your music player.

### Metadata Updates

- **New files**: All metadata tags are added during download
- **Existing files**: The script checks and updates metadata without re-downloading
  - Enhances short/generic titles
  - Adds missing tags (Artist, Album, Year, Genre, Album Art)
  - Preserves any other existing metadata

## Security Notes

⚠️ **Important**: Keep your access token secure - it provides access to your Pocket Casts account.

For better security:

- Don't share your token
- Use environment variables instead of command-line arguments
- The token may expire and need to be refreshed periodically

Example with environment variable:

```bash
export POCKETCASTS_TOKEN="your_token_here"

python pocketcast_downloader.py --token "$POCKETCASTS_TOKEN"
```

Or create a `.env` file (don't commit it to git):

```bash
# .env file
POCKETCASTS_TOKEN=your_token_here
```

Then use it in a wrapper script:

```bash
#!/bin/bash
source .env
python pocketcast_downloader.py --token "$POCKETCASTS_TOKEN" "$@"
```

## Requirements

- Python 3.7+
- `requests` library

## License

MIT License - Feel free to use and modify as needed.
