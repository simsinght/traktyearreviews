#!/usr/bin/env python3
"""
Download poster and profile images for year review

Usage:
    python download_images_template.py <year>

Example:
    python download_images_template.py 2026
"""

import json
import os
import sys
import requests

if len(sys.argv) != 2:
    print("Usage: python download_images_template.py <year>")
    print("Example: python download_images_template.py 2026")
    sys.exit(1)

YEAR = sys.argv[1]
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def download_image(path, filename):
    """Download an image from TMDB"""
    if not path:
        print(f"  ✗ No path for {filename}")
        return False

    url = f"{TMDB_IMAGE_BASE}{path}"
    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs('assets', exist_ok=True)
        filepath = os.path.join('assets', filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"  ✓ Downloaded {filename}")
        return True
    else:
        print(f"  ✗ Failed to download {filename}")
        return False

def sanitize_filename(name):
    """Create a safe filename from a movie/person name"""
    # Remove special characters and spaces
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
    safe = safe.replace(' ', '')
    return safe[:50]  # Limit length

def main():
    """Download all necessary images"""
    print(f"Downloading images for {YEAR} review...")

    with open(f'{YEAR}_stats.json', 'r') as f:
        data = json.load(f)

    stats = data['stats']

    # Top Actor
    if 'top_actor' in stats:
        actor = stats['top_actor']
        filename = f"{sanitize_filename(actor['name'])}.jpg"
        print(f"\nTop Actor: {actor['name']}")
        download_image(actor.get('profile_path'), filename)

    # Top Director
    if 'top_director' in stats:
        director = stats['top_director']
        filename = f"{sanitize_filename(director['name'])}.jpg"
        print(f"\nTop Director: {director['name']}")
        download_image(director.get('profile_path'), filename)

    # Highest Rated Movies
    print("\nHighest Rated Movies:")
    for i, movie in enumerate(stats['highest_rated']):
        rating = int(movie['rating'])
        filename = f"{sanitize_filename(movie['title'])}{rating}.jpg"
        download_image(movie.get('poster_path'), filename)

    # Lowest Rated Movies
    print("\nLowest Rated Movies:")
    for movie in stats['lowest_rated']:
        rating = int(movie['rating'])
        filename = f"{sanitize_filename(movie['title'])}{rating}.jpg"
        download_image(movie.get('poster_path'), filename)

    # First Watch
    print("\nFirst Watch:")
    first = stats['first_watch']
    filename = f"{sanitize_filename(first['title'])}.jpg"
    download_image(first.get('poster_path'), filename)

    # Last Watch
    print("\nLast Watch:")
    last = stats['last_watch']
    filename = f"{sanitize_filename(last['title'])}.jpg"
    download_image(last.get('poster_path'), filename)

    # Divergent Ratings - Lower
    print("\nLower Than Average:")
    for movie in stats['most_lower_than_avg']:
        filename = f"{sanitize_filename(movie['title'])}.jpg"
        download_image(movie.get('poster_path'), filename)

    # Divergent Ratings - Higher
    print("\nHigher Than Average:")
    for movie in stats['most_higher_than_avg']:
        filename = f"{sanitize_filename(movie['title'])}.jpg"
        download_image(movie.get('poster_path'), filename)

    # Most Popular
    print("\nMost Popular:")
    most_pop = stats['most_popular']
    filename = f"{sanitize_filename(most_pop['title'])}.jpg"
    download_image(most_pop.get('poster_path'), filename)

    # Least Popular
    print("\nLeast Popular:")
    least_pop = stats['least_popular']
    filename = f"{sanitize_filename(least_pop['title'])}.jpg"
    download_image(least_pop.get('poster_path'), filename)

    # Smallest Budgets
    if 'smallest_budgets' in stats:
        print("\nSmallest Budgets:")
        for movie in stats['smallest_budgets']:
            filename = f"{sanitize_filename(movie['title'])}.jpg"
            download_image(movie.get('poster_path'), filename)

    # Biggest Budgets
    if 'biggest_budgets' in stats:
        print("\nBiggest Budgets:")
        for movie in stats['biggest_budgets']:
            filename = f"{sanitize_filename(movie['title'])}.jpg"
            download_image(movie.get('poster_path'), filename)

    # Oldest Film
    if 'oldest_film' in stats:
        print("\nOldest Film:")
        oldest = stats['oldest_film']
        filename = f"{sanitize_filename(oldest.get('name', oldest.get('title', '')))}.jpg"
        download_image(oldest.get('poster_path'), filename)

    # Newest Film
    if 'newest_film' in stats:
        print("\nNewest Film:")
        newest = stats['newest_film']
        filename = f"{sanitize_filename(newest.get('name', newest.get('title', '')))}.jpg"
        download_image(newest.get('poster_path'), filename)

    # Longest Film
    if 'longest_film' in stats:
        print("\nLongest Film:")
        longest = stats['longest_film']
        filename = f"{sanitize_filename(longest.get('name', longest.get('title', '')))}.jpg"
        download_image(longest.get('poster_path'), filename)

    # Shortest Film
    if 'shortest_film' in stats:
        print("\nShortest Film:")
        shortest = stats['shortest_film']
        filename = f"{sanitize_filename(shortest.get('name', shortest.get('title', '')))}.jpg"
        download_image(shortest.get('poster_path'), filename)

    # Top 10 Cast profile photos
    print("\nTop 10 Cast:")
    for i, actor in enumerate(stats.get('top_10_actors', []), 1):
        filename = f"cast_{sanitize_filename(actor['name'])}.jpg"
        download_image(actor.get('profile_path'), filename)

    # Top 10 Directors profile photos
    print("\nTop 10 Directors:")
    for i, director in enumerate(stats.get('top_10_directors', []), 1):
        filename = f"director_{sanitize_filename(director['name'])}.jpg"
        download_image(director.get('profile_path'), filename)

    # All movie posters for the complete list
    print("\nAll Movie Posters:")
    downloaded_count = 0
    for movie in data['movies']:
        if movie.get('poster_path'):
            # Use tmdb_id to ensure unique filenames
            filename = f"poster_{movie['tmdb_id']}.jpg"
            if download_image(movie.get('poster_path'), filename):
                downloaded_count += 1
    print(f"  Downloaded {downloaded_count} movie posters")

    print("\n✓ Image download complete!")

if __name__ == "__main__":
    main()
