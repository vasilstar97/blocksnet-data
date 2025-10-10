# BlocksNet Data

BlocksNet Data is a collection of urban datasets processed for analysis and modeling with [BlocksNet](https://github.com/aimclub/blocksnet)

## Features

- Automated data processing per city using Python scripts (`main.py` in each city folder).
- Generates ZIP archives for each city containing processed datasets.
- Supports draft GitHub releases with versioned datasets.
- Release notes are automatically generated, listing:
  - BlocksNet version
  - Cities included
  - Files per city

## Usage

1. **Add or update city data** under `cities/<city_name>/`.
2. Each city folder should contain a `main.py` to process its data.
3. Push changes and create a **draft GitHub release**; the workflow will:
   - Run scripts for changes cities
   - Package outputs into ZIPs
   - Generate release notes
   - Publish the release if successful

## Versioning

- Dataset releases are tagged using **date-based versions**: `vYYYY.MM.DD`
- Pre-release drafts can use suffixes: `vYYYY.MM.DD-alpha`

## Requirements

- Python 3.10
- Dependencies listed in `requirements.txt`
