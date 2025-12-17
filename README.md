# Pocket Casts Downloader

Download all your favorited podcasts from Pocket Casts for a specific year.

## Features

- 🎯 Download episodes favorited in a specific year
- 📁 Organizes downloads by podcast name
- ⚡ Skips already downloaded files
- 📊 Progress tracking for each download
- 💾 Optional metadata export to JSON
- 🔒 Works with Google Sign-In accounts

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Getting Your Access Token

Since you sign in with Google, you'll need to get your access token from the browser:

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

Alternative method using browser console:
1. Open [https://play.pocketcasts.com](https://play.pocketcasts.com) and sign in
2. Open Developer Tools Console (F12 → Console tab)
3. Type: `localStorage.getItem('token')` or `document.cookie`
4. Look for any token values and try them with the script

## Usage

Basic usage (downloads current year's favorites):

```bash
python pocketcast_downloader.py --token YOUR_ACCESS_TOKEN
```

### Options

- `--token`: Your Pocket Casts access token from browser (required)
- `--year`: Year to filter favorites (default: current year)
- `--output-dir`: Download directory (default: ./downloads)
- `--save-metadata`: Save episode metadata as JSON file

### Examples

Download favorites from 2024:

```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --year 2024
```

Save to a specific directory and include metadata:

```bash
python pocketcast_downloader.py \
  --token YOUR_ACCESS_TOKEN \
  --year 2025 \
  --output-dir ~/Podcasts/Favorites \
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

## Output Structure

Downloads are organized as follows:

```
downloads/
├── Podcast Name 1/
│   ├── Episode 1.mp3
│   └── Episode 2.mp3
├── Podcast Name 2/
│   ├── Episode 3.mp3
│   └── Episode 4.mp3
└── metadata_2025.json (if --save-metadata is used)
```

## Requirements

- Python 3.7+
- `requests` library

## License

MIT License - Feel free to use and modify as needed.
