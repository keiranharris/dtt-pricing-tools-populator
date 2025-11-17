# Version Control System

This document describes the version control system implemented for the PriceUp project.

## Version Format

The project uses a date-based versioning system with the format:

```
YYYY.MM.DD_N
```

Where:
- `YYYY.MM.DD` is the ISO date format (e.g., 2025.11.18)
- `N` is an incrementing integer starting from 1

## Examples

- `2025.11.18_1` - First release on November 18, 2025
- `2025.11.18_2` - Second release on the same day
- `2025.11.19_1` - First release on November 19, 2025

## Features

### Version Display

The application automatically displays the current version at startup:

```
🚀 PriceUp v2025.11.18_1
```

### Command Line Version Check

Use the `--version` or `-v` flags to display only the version number:

```bash
python3 pricing_tool_accelerator.py --version
# Output: 2025.11.18_1
```

### Update Checking

The system can check for newer versions from GitHub releases:
- Checks are cached for 24 hours to avoid API rate limits
- Users are prompted when newer versions are available
- Users can choose to continue with their current version

### Interactive Update Prompts

When a newer version is available, users see an interactive prompt:

```
🔄 A new version of this code is available!
Current version: 2025.11.18_1
Latest version: 2025.11.18_2

To update, run: git pull && git checkout v2025.11.18_2
Or visit: https://github.com/keiranharris/priceup/releases

There is a new version available. Are you sure you want to run with your old version? (y/n):
```

## Release Management

### Creating Releases

Use the release manager script to create new releases:

```bash
# Show version information
python3 scripts/release_manager.py --info

# Create new release
python3 scripts/release_manager.py --release

# Create release with notes
python3 scripts/release_manager.py --release --notes "Bug fixes and improvements"

# Check for updates
python3 scripts/release_manager.py --check-updates
```

### Release Process

1. The script automatically generates the next version number
2. Updates the `VERSION` file
3. Creates a git commit with the version bump
4. Creates a git tag for the release
5. Provides instructions for pushing to remote

### VERSION File

The current version is stored in a simple text file at the project root:

```
VERSION
```

This file contains only the version string (e.g., `2025.11.18_1`).

## Implementation Details

### Core Components

- `src/version_manager.py` - Main version management logic
- `src/version_cli_integration.py` - CLI integration for version display and update checking
- `scripts/release_manager.py` - Release management utilities
- `VERSION` - Current version storage

### Update Checking

The system uses GitHub's releases API to check for updates:
- Endpoint: `https://api.github.com/repos/keiranharris/priceup/releases/latest`
- Uses standard library `urllib` for HTTP requests (no external dependencies)
- Implements proper error handling for network failures
- Caches results locally to respect API rate limits

### Integration Points

Version checking is integrated into the main application startup sequence:

1. Handle `--version` flag (exit early if present)
2. Display version on startup
3. Check for updates (if cache is expired)
4. Prompt user if newer version available
5. Continue with application logic

## Configuration

### Cache Location

Version check cache is stored at: `~/.priceup_version_cache.json`

### Cache Settings

- Maximum age: 24 hours
- Contains update status, latest version info, and check timestamp
- Non-critical failures are handled gracefully

### GitHub Repository

Configured to check: `keiranharris/priceup`

This can be changed in the VersionManager constructor if needed.

## Error Handling

The version system is designed to fail gracefully:

- Network failures don't prevent application startup
- Missing VERSION file defaults to current date with `_1`
- API rate limits are handled with local caching
- Malformed version strings fall back to safe defaults

## Development Workflow

1. Develop features on feature branches
2. Merge to main branch
3. Use `scripts/release_manager.py --release` to create releases
4. Push commits and tags to GitHub
5. Create GitHub release from the tag (manual step)

The system supports multiple releases per day with automatic increment handling.