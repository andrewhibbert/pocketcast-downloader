# Pocket Casts Downloader

Download all your favorited podcasts from Pocket Casts, filtered by the year they were published.

## Features

- 🎯 Download episodes published in a specific year (or all starred episodes)
- 📁 Saves files with podcast name in filename by default
- 📂 Optional: Organize downloads into separate podcast directories
- ⚡ Skips already downloaded files
- 📊 Progress tracking for each download
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
- `--no-verify-ssl`: Disable SSL verification (needed on macOS)

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

**Save to a specific directory with metadata:**
```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --year 2025 \
  --output-dir ~/Podcasts \
  --save-metadata
```

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
