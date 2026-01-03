# Letterboxd Year in Review Generator

Generate beautiful year-in-review pages from your Letterboxd data.

## Quick Start for a New Year

1. **Export your Letterboxd data**
   - Go to Letterboxd settings and export your data
   - Extract the zip file to this directory

2. **Set your TMDB API key**
   ```bash
   export TMDB_API_KEY=your_api_key_here
   ```

3. **Run the scripts**
   ```bash
   source venv/bin/activate

   # Replace with your year and letterboxd export folder name
   YEAR=2026
   LETTERBOXD_DIR="letterboxd-simsinght-2026-01-01-00-00-utc"

   # Generate stats and fetch TMDB data
   python generate_review_template.py $YEAR $LETTERBOXD_DIR

   # Download all poster images
   python download_images_template.py $YEAR

   # Generate HTML
   python generate_html_template.py $YEAR
   ```

4. **Publish to web**
   ```bash
   mkdir -p /Volumes/web/movies/$YEAR/assets
   cp -r assets/* /Volumes/web/movies/$YEAR/assets/
   cp sim_$YEAR.html /Volumes/web/movies/$YEAR/index.html
   ```

## Features

- **Stats**: Total films, hours watched, average rating
- **Top picks**: Highest/lowest rated films
- **People**: Most watched actors and directors
- **Activity**: Weekly and monthly viewing patterns
- **Genres & Countries**: What you watched most
- **Complete list**: All films with posters and ratings

## API Keys

Get a TMDB API key from: https://www.themoviedb.org/settings/api

## Notes

- Short films (< 30 min) are included in totals but excluded from top actor/director calculations
- Images are downloaded locally to avoid exposing API keys
- Each year gets its own assets folder on the web server
