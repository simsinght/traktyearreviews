#!/usr/bin/env python3
"""
Generate Year in Review from Letterboxd data

Usage:
    python generate_review_template.py <year> <letterboxd_dir>

Environment variables:
    TMDB_API_KEY - Your TMDB API key (required)

Example:
    export TMDB_API_KEY=your_key_here
    python generate_review_template.py 2026 letterboxd-simsinght-2026-01-01-00-00-utc
"""

import csv
import os
import sys
import requests
from collections import defaultdict, Counter
from datetime import datetime
from urllib.parse import urlencode
import json

# Get parameters
if len(sys.argv) != 3:
    print("Usage: python generate_review_template.py <year> <letterboxd_dir>")
    print("Example: python generate_review_template.py 2026 letterboxd-simsinght-2026-01-01-00-00-utc")
    sys.exit(1)

YEAR = int(sys.argv[1])
LETTERBOXD_DIR = sys.argv[2]

# TMDB API Configuration from environment
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
if not TMDB_API_KEY:
    print("Error: TMDB_API_KEY environment variable not set")
    print("Set it with: export TMDB_API_KEY=your_key_here")
    sys.exit(1)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


class MovieData:
    def __init__(self):
        self.movies = []
        self.tmdb_cache = {}

    def load_letterboxd_data(self):
        """Load movies from Letterboxd diary.csv for {YEAR}"""
        diary_path = os.path.join(LETTERBOXD_DIR, "diary.csv")

        with open(diary_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                watched_date = row.get('Watched Date', '')
                if watched_date.startswith(f'{YEAR}-'):
                    self.movies.append({
                        'name': row['Name'],
                        'year': row['Year'],
                        'rating': float(row['Rating']) * 2 if row['Rating'] else 0,  # Letterboxd uses 0.5-5, convert to 0-10
                        'watched_date': watched_date,
                        'letterboxd_uri': row['Letterboxd URI'],
                        'tags': row.get('Tags', '').split(', ') if row.get('Tags') else []
                    })

        print(f"Loaded {len(self.movies)} movies from {YEAR}")
        return self.movies

    def search_tmdb(self, title, year):
        """Search TMDB for a movie"""
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year
        }

        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                return results[0]['id']
        return None

    def get_tmdb_details(self, tmdb_id):
        """Get detailed movie info from TMDB"""
        if tmdb_id in self.tmdb_cache:
            return self.tmdb_cache[tmdb_id]

        params = {'api_key': TMDB_API_KEY}

        # Get basic details
        details_response = requests.get(f"{TMDB_BASE_URL}/movie/{tmdb_id}", params=params)
        if details_response.status_code != 200:
            return None

        details = details_response.json()

        # Get credits (cast and crew)
        credits_response = requests.get(f"{TMDB_BASE_URL}/movie/{tmdb_id}/credits", params=params)
        credits = credits_response.json() if credits_response.status_code == 200 else {}

        movie_info = {
            'tmdb_id': tmdb_id,
            'title': details.get('title'),
            'poster_path': details.get('poster_path'),
            'backdrop_path': details.get('backdrop_path'),
            'runtime': details.get('runtime', 0),
            'budget': details.get('budget', 0),
            'vote_average': details.get('vote_average', 0),
            'vote_count': details.get('vote_count', 0),
            'release_date': details.get('release_date', ''),
            'genres': [g['name'] for g in details.get('genres', [])],
            'cast': credits.get('cast', [])[:10],  # Top 10 cast
            'crew': credits.get('crew', []),
            'production_countries': [c['name'] for c in details.get('production_countries', [])],
            'spoken_languages': [l['english_name'] for l in details.get('spoken_languages', [])]
        }

        self.tmdb_cache[tmdb_id] = movie_info
        return movie_info

    def enrich_with_tmdb(self):
        """Enrich Letterboxd data with TMDB details"""
        print("Enriching with TMDB data...")

        for movie in self.movies:
            tmdb_id = self.search_tmdb(movie['name'], movie['year'])
            if tmdb_id:
                details = self.get_tmdb_details(tmdb_id)
                if details:
                    movie.update(details)
                    print(f"✓ {movie['name']} ({movie['year']})")
            else:
                print(f"✗ Could not find: {movie['name']} ({movie['year']})")

        # Filter out movies without TMDB data (keep short films now)
        self.movies = [m for m in self.movies if 'tmdb_id' in m]
        print(f"\nEnriched {len(self.movies)} movies")

    def download_poster(self, poster_path, filename):
        """Download a poster image"""
        if not poster_path:
            return False

        url = f"{TMDB_IMAGE_BASE}{poster_path}"
        response = requests.get(url)

        if response.status_code == 200:
            os.makedirs('assets', exist_ok=True)
            filepath = os.path.join('assets', filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        return False

    def calculate_stats(self):
        """Calculate all statistics for the year"""
        stats = {}

        # Basic counts
        stats['total_films'] = len(self.movies)
        stats['total_hours'] = sum(m.get('runtime', 0) for m in self.movies) / 60

        # Average rating
        rated_movies = [m for m in self.movies if m['rating'] > 0]
        if rated_movies:
            stats['average_rating'] = sum(m['rating'] for m in rated_movies) / len(rated_movies)

        # Highest rated (rating >= 8)
        highest_rated = sorted(rated_movies, key=lambda x: x['rating'], reverse=True)
        stats['highest_rated'] = [m for m in highest_rated if m['rating'] >= 8][:9]

        # Lowest rated
        lowest_rated = sorted(rated_movies, key=lambda x: x['rating'])
        stats['lowest_rated'] = lowest_rated[:3]

        # First and last watch
        sorted_by_date = sorted(self.movies, key=lambda x: x['watched_date'])
        stats['first_watch'] = sorted_by_date[0]
        stats['last_watch'] = sorted_by_date[-1]

        # Most watched actor (exclude short films < 30 min)
        feature_films = [m for m in self.movies if m.get('runtime', 0) >= 30]

        actor_counts = defaultdict(list)
        actor_details = {}
        for movie in feature_films:
            for actor in movie.get('cast', []):
                actor_counts[actor['name']].append(movie['name'])
                if actor['name'] not in actor_details:
                    actor_details[actor['name']] = actor

        if actor_counts:
            top_actor_name, top_actor_movies = max(actor_counts.items(), key=lambda x: len(x[1]))
            actor = actor_details[top_actor_name]
            stats['top_actor'] = {
                'name': top_actor_name,
                'movies': top_actor_movies,
                'profile_path': actor.get('profile_path'),
                'count': len(top_actor_movies)
            }

        # Top 10 actors (include ALL films including shorts)
        all_actor_counts = defaultdict(list)
        all_actor_details = {}
        for movie in self.movies:  # Use all movies
            for actor in movie.get('cast', []):
                all_actor_counts[actor['name']].append(movie['name'])
                if actor['name'] not in all_actor_details:
                    all_actor_details[actor['name']] = actor

        top_10_actors = []
        for name, movies in sorted(all_actor_counts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            top_10_actors.append({
                'name': name,
                'count': len(movies),
                'profile_path': all_actor_details[name].get('profile_path')
            })
        stats['top_10_actors'] = top_10_actors

        # Most watched director (exclude short films < 30 min)
        director_counts = defaultdict(list)
        director_details = {}
        for movie in feature_films:
            directors = [c for c in movie.get('crew', []) if c.get('job') == 'Director']
            for director in directors:
                director_counts[director['name']].append(movie['name'])
                if director['name'] not in director_details:
                    director_details[director['name']] = director

        if director_counts:
            top_director_name, top_director_movies = max(director_counts.items(), key=lambda x: len(x[1]))
            director = director_details[top_director_name]
            stats['top_director'] = {
                'name': top_director_name,
                'movies': top_director_movies,
                'profile_path': director.get('profile_path'),
                'count': len(top_director_movies)
            }

        # Top 10 directors (include ALL films including shorts)
        all_director_counts = defaultdict(list)
        all_director_details = {}
        for movie in self.movies:  # Use all movies
            directors = [c for c in movie.get('crew', []) if c.get('job') == 'Director']
            for director in directors:
                all_director_counts[director['name']].append(movie['name'])
                if director['name'] not in all_director_details:
                    all_director_details[director['name']] = director

        top_10_directors = []
        for name, movies in sorted(all_director_counts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            top_10_directors.append({
                'name': name,
                'count': len(movies),
                'profile_path': all_director_details[name].get('profile_path')
            })
        stats['top_10_directors'] = top_10_directors

        # Divergent ratings (your rating vs TMDB average)
        divergent = []
        for movie in rated_movies:
            if movie.get('vote_count', 0) > 100:
                diff = movie['rating'] - movie['vote_average']
                divergent.append((diff, movie))

        divergent.sort(key=lambda x: x[0])
        stats['most_lower_than_avg'] = [d[1] for d in divergent[:2]]
        stats['most_higher_than_avg'] = [d[1] for d in divergent[-2:]]

        # Most and least popular
        stats['most_popular'] = sorted(self.movies, key=lambda x: x.get('vote_count', 0), reverse=True)[0]
        stats['least_popular'] = sorted([m for m in self.movies if m.get('vote_count', 0) > 0],
                                       key=lambda x: x.get('vote_count', 0))[0]

        # Budget stats
        movies_with_budget = [m for m in self.movies if m.get('budget', 0) > 0]
        if movies_with_budget:
            stats['smallest_budgets'] = sorted(movies_with_budget, key=lambda x: x['budget'])[:2]
            stats['biggest_budgets'] = sorted(movies_with_budget, key=lambda x: x['budget'], reverse=True)[:2]

        # Movies watched within 30 days of release
        recent_watches = []
        for movie in self.movies:
            if movie.get('release_date'):
                try:
                    release_date = datetime.strptime(movie['release_date'], '%Y-%m-%d')
                    watch_date = datetime.strptime(movie['watched_date'], '%Y-%m-%d')
                    days_diff = (watch_date - release_date).days
                    if 0 <= days_diff <= 30 and release_date.year == YEAR:
                        recent_watches.append(movie)
                except:
                    pass
        stats['recent_watches_count'] = len(recent_watches)

        # Genres breakdown
        genre_counts = Counter()
        for movie in self.movies:
            for genre in movie.get('genres', []):
                genre_counts[genre] += 1
        stats['top_genres'] = genre_counts.most_common(5)

        # Countries breakdown
        country_counts = Counter()
        for movie in self.movies:
            for country in movie.get('production_countries', []):
                country_counts[country] += 1
        stats['top_countries'] = country_counts.most_common(5)

        # Languages breakdown
        language_counts = Counter()
        for movie in self.movies:
            for language in movie.get('spoken_languages', []):
                language_counts[language] += 1
        stats['top_languages'] = language_counts.most_common(5)

        # Decades breakdown
        decade_counts = Counter()
        for movie in self.movies:
            year = int(movie.get('year', 0))
            if year:
                decade = (year // 10) * 10
                decade_counts[decade] += 1
        stats['decades'] = sorted(decade_counts.items())

        # Release year stats
        release_years = [int(m.get('year', 0)) for m in self.movies if m.get('year')]
        films_2025 = sum(1 for y in release_years if y == 2025)
        films_2024 = sum(1 for y in release_years if y == 2024)
        films_older = len(release_years) - films_2025 - films_2024
        stats['release_year_breakdown'] = {
            '2025': films_2025,
            '2024': films_2024,
            'older': films_older
        }

        # Oldest and newest by release date
        movies_with_release = [m for m in self.movies if m.get('release_date')]
        if movies_with_release:
            stats['oldest_film'] = min(movies_with_release, key=lambda x: x['release_date'])
            stats['newest_film'] = max(movies_with_release, key=lambda x: x['release_date'])

        # Longest and shortest
        movies_with_runtime = [m for m in self.movies if m.get('runtime', 0) > 0]
        if movies_with_runtime:
            stats['longest_film'] = max(movies_with_runtime, key=lambda x: x['runtime'])
            stats['shortest_film'] = min(movies_with_runtime, key=lambda x: x['runtime'])

        # Weekly activity
        week_counts = defaultdict(int)
        for movie in self.movies:
            if movie.get('watched_date'):
                try:
                    dt = datetime.strptime(movie['watched_date'], '%Y-%m-%d')
                    week_num = dt.isocalendar()[1]  # ISO week number
                    week_counts[week_num] += 1
                except:
                    pass
        stats['weekly_activity'] = dict(sorted(week_counts.items()))

        # Monthly activity
        month_counts = defaultdict(int)
        for movie in self.movies:
            if movie.get('watched_date'):
                try:
                    month = movie['watched_date'][:7]  # YYYY-MM
                    month_counts[month] += 1
                except:
                    pass
        stats['monthly_activity'] = dict(sorted(month_counts.items()))

        # Day of week activity (0 = Monday, 6 = Sunday)
        day_counts = defaultdict(int)
        for movie in self.movies:
            if movie.get('watched_date'):
                try:
                    dt = datetime.strptime(movie['watched_date'], '%Y-%m-%d')
                    day_counts[dt.weekday()] += 1
                except:
                    pass
        stats['day_of_week'] = dict(sorted(day_counts.items()))

        return stats


def main():
    """Main execution"""
    print("=" * 60)
    print("Generating Sim's {YEAR} Year in Review")
    print("=" * 60)

    # Load and process data
    data = MovieData()
    data.load_letterboxd_data()
    data.enrich_with_tmdb()

    # Calculate statistics
    stats = data.calculate_stats()

    # Print summary
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)
    print(f"Total Films: {stats['total_films']}")
    print(f"Total Hours: {stats['total_hours']:.1f}")
    print(f"First Watch: {stats['first_watch']['name']}")
    print(f"Last Watch: {stats['last_watch']['name']}")

    if 'top_actor' in stats:
        print(f"Top Actor: {stats['top_actor']['name']} ({stats['top_actor']['count']} films)")
    if 'top_director' in stats:
        print(f"Top Director: {stats['top_director']['name']} ({stats['top_director']['count']} films)")

    print(f"\nHighest Rated Films: {len(stats['highest_rated'])}")
    for movie in stats['highest_rated'][:3]:
        print(f"  - {movie['name']} ({movie['rating']}/10)")

    # Save data for later use
    with open('{YEAR}_stats.json', 'w') as f:
        # Convert to JSON-serializable format
        json_stats = {
            'movies': data.movies,
            'stats': stats
        }
        json.dump(json_stats, f, indent=2, default=str)

    print("\n✓ Stats saved to {YEAR}_stats.json")
    print("\nNext: Download poster images and generate HTML")


if __name__ == "__main__":
    main()
