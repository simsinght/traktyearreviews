#!/usr/bin/env python3
"""
Generate the HTML page for year review - Enhanced Version

Usage:
    python generate_html_template.py <year>

Example:
    python generate_html_template.py 2026
"""

import json
import sys
from datetime import datetime

if len(sys.argv) != 2:
    print("Usage: python generate_html_template.py <year>")
    print("Example: python generate_html_template.py 2026")
    sys.exit(1)

YEAR = sys.argv[1]

def sanitize_filename(name):
    """Create a safe filename"""
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
    safe = safe.replace(' ', '')
    return safe[:50]

def format_date(date_str):
    """Format date as 'Jan 5'"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%b %-d')

def format_budget(budget):
    """Format budget with commas"""
    return f"${budget:,}"

def format_runtime(minutes):
    """Format runtime"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

def main():
    """Generate HTML"""
    with open('{YEAR}_stats.json', 'r') as f:
        data = json.load(f)

    stats = data['stats']
    movies = data['movies']

    # Calculate total hours rounded
    total_hours = int(stats['total_hours'])

    # Build movie sections HTML
    highest_rated_html = ""
    for movie in stats['highest_rated']:
        rating = int(movie['rating'])
        filename = f"assets/{sanitize_filename(movie['title'])}{rating}.jpg"
        highest_rated_html += f'''<div class="movie-item">
            <div class="movie-poster-container">
                <img src="{filename}" class="movie-poster"/>
            </div>
            <div class="rating-badge">
                <div class="rating-number">{rating}</div>
            </div>
        </div>'''

    lowest_rated_html = ""
    for movie in stats['lowest_rated']:
        rating = int(movie['rating'])
        filename = f"assets/{sanitize_filename(movie['title'])}{rating}.jpg"
        lowest_rated_html += f'''<div class="movie-item">
            <div class="movie-poster-container">
                <img src="{filename}" class="movie-poster"/>
            </div>
            <div class="rating-badge">
                <div class="rating-number">{rating}</div>
            </div>
        </div>'''

    # Divergent ratings
    divergent_lower_html = ""
    for movie in stats['most_lower_than_avg']:
        filename = f"assets/{sanitize_filename(movie['title'])}.jpg"
        diff = abs(int(movie['rating'] - movie['vote_average']))
        divergent_lower_html += f'''<div class="movie-item">
            <div class="movie-poster-container">
                <div class="divergent-label">{diff} PTS LOWER THAN AVG</div>
                <img src="{filename}" class="movie-poster"/>
            </div>
        </div>'''

    divergent_higher_html = ""
    for movie in stats['most_higher_than_avg']:
        filename = f"assets/{sanitize_filename(movie['title'])}.jpg"
        diff = int(movie['rating'] - movie['vote_average'])
        divergent_higher_html += f'''<div class="movie-item">
            <div class="movie-poster-container">
                <div class="divergent-label">{diff} PTS HIGHER THAN AVG</div>
                <img src="{filename}" class="movie-poster"/>
            </div>
        </div>'''

    # Budget sections
    smallest_budgets_html = ""
    if 'smallest_budgets' in stats:
        for movie in stats['smallest_budgets']:
            filename = f"assets/{sanitize_filename(movie['title'])}.jpg"
            budget_str = format_budget(movie['budget'])
            smallest_budgets_html += f'''<div class="movie-item">
                <div class="movie-poster-container">
                    <img src="{filename}" class="movie-poster"/>
                    <div class="budget-label">{budget_str}</div>
                </div>
            </div>'''

    biggest_budgets_html = ""
    if 'biggest_budgets' in stats:
        for movie in stats['biggest_budgets']:
            filename = f"assets/{sanitize_filename(movie['title'])}.jpg"
            budget_str = format_budget(movie['budget'])
            biggest_budgets_html += f'''<div class="movie-item">
                <div class="movie-poster-container">
                    <img src="{filename}" class="movie-poster"/>
                    <div class="budget-label">{budget_str}</div>
                </div>
            </div>'''

    # Top actor and director
    top_actor_html = ""
    if 'top_actor' in stats:
        actor = stats['top_actor']
        filename = f"assets/{sanitize_filename(actor['name'])}.jpg"
        movies_str = ', '.join(actor['movies'][:3])
        top_actor_html = f'''
        <div class="person-card">
            <div class="person-label">MOST WATCHED ACTOR</div>
            <img src="{filename}" class="person-image"/>
            <div class="person-name">{actor['name']}</div>
            <div class="person-movies">{movies_str}</div>
        </div>'''

    top_director_html = ""
    if 'top_director' in stats:
        director = stats['top_director']
        filename = f"assets/{sanitize_filename(director['name'])}.jpg"
        movies_str = ', '.join(director['movies'][:2])
        top_director_html = f'''
        <div class="person-card">
            <div class="person-label">MOST WATCHED DIRECTOR</div>
            <img src="{filename}" class="person-image"/>
            <div class="person-name">{director['name']}</div>
            <div class="person-movies">{movies_str}</div>
        </div>'''

    # First and last watch
    first_watch = stats['first_watch']
    first_filename = f"assets/{sanitize_filename(first_watch['name'])}.jpg"
    first_date = format_date(first_watch['watched_date'])

    last_watch = stats['last_watch']
    last_filename = f"assets/{sanitize_filename(last_watch['name'])}.jpg"
    last_date = format_date(last_watch['watched_date'])

    # Most/least popular
    most_pop = stats['most_popular']
    most_pop_filename = f"assets/{sanitize_filename(most_pop['name'])}.jpg"

    least_pop = stats['least_popular']
    least_pop_filename = f"assets/{sanitize_filename(least_pop['name'])}.jpg"

    # Oldest/Newest/Longest/Shortest
    oldest = stats.get('oldest_film', {})
    newest = stats.get('newest_film', {})
    longest = stats.get('longest_film', {})
    shortest = stats.get('shortest_film', {})

    oldest_filename = f"assets/{sanitize_filename(oldest.get('name', ''))}.jpg"
    newest_filename = f"assets/{sanitize_filename(newest.get('name', ''))}.jpg"
    longest_filename = f"assets/{sanitize_filename(longest.get('name', ''))}.jpg"
    shortest_filename = f"assets/{sanitize_filename(shortest.get('name', ''))}.jpg"

    # Top genres with bar chart
    genres = stats.get('top_genres', [])
    max_genre = max([count for _, count in genres], default=1)
    genres_html = ""
    for genre, count in genres[:10]:
        width = (count / max_genre * 100) if max_genre > 0 else 0
        genres_html += f'''
        <div class="bar-chart-row">
            <span class="bar-chart-label">{genre}</span>
            <div class="bar-chart-bar" style="width: {width}%; background-color: #00d573;">
                <span class="bar-chart-count">{count}</span>
            </div>
        </div>'''

    # Top countries with bar chart
    countries = stats.get('top_countries', [])
    max_country = max([count for _, count in countries], default=1)
    countries_html = ""
    for country, count in countries[:10]:
        width = (count / max_country * 100) if max_country > 0 else 0
        countries_html += f'''
        <div class="bar-chart-row">
            <span class="bar-chart-label">{country}</span>
            <div class="bar-chart-bar" style="width: {width}%; background-color: #00a8e1;">
                <span class="bar-chart-count">{count}</span>
            </div>
        </div>'''

    # Top languages with bar chart
    languages = stats.get('top_languages', [])
    max_language = max([count for _, count in languages], default=1)
    languages_html = ""
    for language, count in languages[:10]:
        width = (count / max_language * 100) if max_language > 0 else 0
        languages_html += f'''
        <div class="bar-chart-row">
            <span class="bar-chart-label">{language}</span>
            <div class="bar-chart-bar" style="width: {width}%; background-color: #ff8800;">
                <span class="bar-chart-count">{count}</span>
            </div>
        </div>'''

    # Top 10 Cast - as small profile images (local files)
    top_10_cast_html = ""
    for i, actor in enumerate(stats.get('top_10_actors', []), 1):
        filename = f"assets/cast_{sanitize_filename(actor['name'])}.jpg"
        top_10_cast_html += f'''
        <div class="person-small-card">
            <img src="{filename}" class="person-small-image" alt="{actor['name']}" onerror="this.src='assets/placeholder.jpg'"/>
            <div class="person-small-name">{actor['name']}</div>
            <div class="person-small-count">{actor['count']} films</div>
        </div>'''

    # Top 10 Directors - as small profile images (local files)
    top_10_directors_html = ""
    for i, director in enumerate(stats.get('top_10_directors', []), 1):
        filename = f"assets/director_{sanitize_filename(director['name'])}.jpg"
        top_10_directors_html += f'''
        <div class="person-small-card">
            <img src="{filename}" class="person-small-image" alt="{director['name']}" onerror="this.src='assets/placeholder.jpg'"/>
            <div class="person-small-name">{director['name']}</div>
            <div class="person-small-count">{director['count']} films</div>
        </div>'''

    # Decades breakdown with bar chart
    decades = stats.get('decades', [])
    max_decade = max([count for _, count in decades], default=1)
    decades_html = ""
    for decade, count in reversed(decades):  # Most recent first
        width = (count / max_decade * 100) if max_decade > 0 else 0
        decades_html += f'''
        <div class="bar-chart-row">
            <span class="bar-chart-label">{decade}s</span>
            <div class="bar-chart-bar" style="width: {width}%; background-color: #e74c3c;">
                <span class="bar-chart-count">{count}</span>
            </div>
        </div>'''

    # Release years - individual years from 2020s
    from collections import Counter
    year_counts = Counter([int(m.get('year', 0)) for m in movies if m.get('year')])
    years_2020s = [(year, year_counts[year]) for year in range(2020, 2026) if year in year_counts]
    years_2020s.sort(reverse=True)  # Most recent first

    max_year_count = max([count for _, count in years_2020s], default=1) if years_2020s else 1
    release_year_html = ""
    for year, count in years_2020s:
        width = (count / max_year_count * 100) if max_year_count > 0 else 0
        release_year_html += f'''
        <div class="bar-chart-row">
            <span class="bar-chart-label">{year}</span>
            <div class="bar-chart-bar" style="width: {width}%; background-color: #9b59b6;">
                <span class="bar-chart-count">{count}</span>
            </div>
        </div>'''

    # Weekly activity chart - convert string keys to ints
    weekly_data = stats.get('weekly_activity', {})
    # Convert string keys to integers
    weekly_data_int = {int(k): v for k, v in weekly_data.items()}
    max_week_count = max(weekly_data_int.values()) if weekly_data_int else 1

    weekly_bars = ""
    for week in range(1, 53):
        count = weekly_data_int.get(week, 0)
        height_percent = (count / max_week_count * 100) if max_week_count > 0 else 0
        # Color gradient: green for early months, cyan for later
        month = (week - 1) // 4
        color = f"hsl({180 - month * 10}, 70%, 50%)"
        weekly_bars += f'<div class="week-bar" style="height: {height_percent}%; background-color: {color};" title="Week {week}: {count} films"></div>'

    # Calculate averages
    avg_per_month = stats['total_films'] / 12
    avg_per_week = stats['total_films'] / 52

    # Day of week chart
    day_names = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    day_of_week = stats.get('day_of_week', {})
    # Convert string keys to integers (from JSON serialization)
    day_of_week_int = {int(k): v for k, v in day_of_week.items()}
    max_day = max(day_of_week_int.values()) if day_of_week_int else 1

    day_bars = ""
    for i in range(7):
        count = day_of_week_int.get(i, 0)
        height = (count / max_day * 100) if max_day > 0 else 0
        day_bars += f'<div class="day-bar" style="height: {height}%;" title="{day_names[i]}: {count} films"><span class="day-count">{count}</span><span class="day-label">{day_names[i]}</span></div>'

    # All movies list (using local poster files)
    all_movies_html = ""
    sorted_movies = sorted(movies, key=lambda x: x.get('watched_date', ''))
    for movie in sorted_movies:
        poster_filename = f"assets/poster_{movie['tmdb_id']}.jpg"
        rating_display = f"{movie['rating']}/10" if movie.get('rating', 0) > 0 else "—"
        watch_date = format_date(movie['watched_date']) if movie.get('watched_date') else ""

        # Format tags
        tags = movie.get('tags', [])
        if isinstance(tags, list) and tags:
            tags_html = ' '.join([f'<span class="movie-tag">{tag}</span>' for tag in tags])
        else:
            tags_html = ""

        all_movies_html += f'''
        <div class="all-movies-item">
            <img src="{poster_filename}" class="all-movies-poster" onerror="this.src='assets/placeholder.jpg'"/>
            <div class="all-movies-info">
                <div class="all-movies-title">{movie['name']}</div>
                <div class="all-movies-meta">{movie.get('year', '')} • {rating_display} • {watch_date}</div>
                {f'<div class="all-movies-tags">{tags_html}</div>' if tags_html else ''}
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sim's {YEAR} in Film</title>
<meta name="description" content="{stats['total_films']} films watched in {YEAR} - {total_hours} hours of cinema">
<meta property="og:title" content="Sim's {YEAR} in Film">
<meta property="og:description" content="{stats['total_films']} films watched in {YEAR}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Sim's {YEAR} in Film">
<meta name="twitter:description" content="{stats['total_films']} films watched in {YEAR}">
<link rel="icon" href="" />
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: Helvetica, Arial, sans-serif;
    background-color: #fff;
  }}

  select {{
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    border: none;
    overflow: visible !important;
  }}

  .container {{
    max-width: 800px;
    margin: 20px auto 50px auto;
    padding: 0 20px;
  }}

  .header {{
    display: flex;
    align-items: center;
    min-height: 100px;
  }}

  .header-logo {{
    width: 146px;
    height: 145px;
  }}

  .header-text {{
    display: flex;
    justify-content: center;
    flex-grow: 1;
  }}

  .header-select {{
    align-self: center;
    margin: 0 0 0 10px;
    font-size: 3em;
    text-align: right;
    background-color: transparent;
  }}

  .header-year {{
    padding: 10px;
    font-size: 3em;
  }}

  .header-reviewed {{
    padding: 10px;
    font-size: 3em;
  }}

  .stats-grid {{
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin: 50px 0;
    padding: 30px 0;
    background-color: #f5f5f5;
    border-radius: 8px;
  }}

  .stat-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 10px 20px;
  }}

  .stat-number {{
    font-size: 3.5em;
    color: #333;
    padding: 5px;
    font-weight: 300;
  }}

  .stat-label {{
    font-size: 0.75em;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 5px;
    text-align: center;
    color: #666;
  }}

  .stats-summary {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 40px 0;
    gap: 40px;
    flex-wrap: wrap;
  }}

  .summary-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
  }}

  .summary-number {{
    font-size: 3em;
    font-weight: 300;
    color: #333;
  }}

  .summary-label {{
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
  }}

  .summary-arrow {{
    font-size: 2em;
    color: #ccc;
    align-self: center;
  }}

  .day-of-week-chart {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 80px;
    width: 200px;
    gap: 4px;
    margin-left: 20px;
    position: relative;
    padding-bottom: 20px;
  }}

  .day-bar {{
    flex: 1;
    background-color: #7f8c8d;
    position: relative;
    min-height: 5px;
    min-width: 20px;
    border-radius: 2px 2px 0 0;
    cursor: pointer;
    transition: opacity 0.2s;
  }}

  .day-bar:hover {{
    opacity: 0.7;
  }}

  .day-count {{
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.7em;
    color: #333;
    font-weight: 600;
    white-space: nowrap;
  }}

  .day-label {{
    position: absolute;
    bottom: -18px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.75em;
    color: #666;
    font-weight: 600;
  }}

  .section-title {{
    padding: 10px;
    font-size: 2em;
    margin: 50px 0 20px 0;
    text-align: center;
    font-weight: 300;
    letter-spacing: 1px;
  }}

  .section-subtitle {{
    padding: 10px;
    font-size: 1.2em;
    margin: 20px 0 10px 0;
    text-align: center;
    font-weight: 600;
  }}

  .people-section {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin: 30px 0;
  }}

  .person-card {{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 28%;
    min-width: 250px;
    margin: 10px;
  }}

  .person-label {{
    padding: 10px;
    font-size: 0.8em;
    font-weight: 600;
  }}

  .person-image {{
    width: 95%;
    border-radius: 8px;
  }}

  .person-name {{
    padding: 10px;
    font-size: 1.5em;
    font-family: Georgia, serif;
    font-weight: 600;
    text-align: center;
  }}

  .person-movies {{
    padding: 10px;
    font-size: 0.7em;
    font-weight: 400;
    text-align: center;
  }}

  .movies-grid {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    margin: 20px 0;
  }}

  .movie-item {{
    display: flex;
    flex-direction: column;
    width: 28%;
    min-width: 150px;
    max-width: 200px;
    position: relative;
    margin: 4px;
  }}

  .movie-poster-container {{
    position: relative;
  }}

  .movie-poster {{
    width: 100%;
    border-radius: 4px;
  }}

  .rating-badge {{
    position: absolute;
    top: 5px;
    right: 5px;
    background-color: #b11010;
    border-radius: 50px;
    padding: 4px 6px;
    color: white;
    font-weight: 600;
    font-size: 0.7em;
    font-family: 'Courier New', Courier, monospace;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }}

  .rating-number {{
    padding: 0;
  }}

  .divergent-label {{
    position: absolute;
    top: 10px;
    left: 0;
    right: 0;
    text-align: center;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 5px;
    font-size: 0.7em;
    font-weight: 600;
  }}

  .budget-label {{
    text-align: center;
    padding: 10px;
    font-size: 1em;
  }}

  .first-last-section {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin: 30px 0;
  }}

  .first-last-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 28%;
    min-width: 200px;
    margin: 10px;
  }}

  .first-last-label {{
    padding: 10px;
    font-size: 1em;
    font-weight: 600;
  }}

  .first-last-image {{
    width: 95%;
    border-radius: 4px;
  }}

  .first-last-date {{
    padding: 10px;
    font-size: 1em;
  }}

  .stat-bars {{
    max-width: 700px;
    margin: 20px auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}

  .stat-bar-item {{
    display: flex;
    justify-content: space-between;
    padding: 8px 15px;
    background-color: #f5f5f5;
    border-radius: 4px;
  }}

  .stat-bar-label {{
    font-weight: 400;
  }}

  .stat-bar-count {{
    font-weight: 600;
    color: #b11010;
  }}

  .gcl-container {{
    background-color: #f5f5f5;
    padding: 30px;
    border-radius: 8px;
    margin: 30px 0;
  }}

  .gcl-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }}

  .gcl-title {{
    font-size: 1.5em;
    font-weight: 300;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  .gcl-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 40px;
  }}

  .gcl-column {{
    display: flex;
    flex-direction: column;
  }}

  .bar-chart-row {{
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    gap: 10px;
  }}

  .bar-chart-label {{
    min-width: 100px;
    font-size: 0.9em;
    font-weight: 400;
  }}

  .bar-chart-bar {{
    height: 20px;
    border-radius: 3px;
    transition: width 0.3s ease;
    position: relative;
    min-width: 30px;
  }}

  .bar-chart-count {{
    position: absolute;
    left: 8px;
    top: 50%;
    transform: translateY(-50%);
    color: white;
    font-size: 0.85em;
    font-weight: 600;
  }}

  .person-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin: 20px auto;
    max-width: 800px;
  }}

  .person-small-card {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}

  .person-small-image {{
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 8px;
  }}

  .person-small-name {{
    font-size: 0.85em;
    font-weight: 600;
    margin-bottom: 3px;
  }}

  .person-small-count {{
    font-size: 0.75em;
    color: #666;
  }}

  .weekly-chart-container {{
    background-color: #f5f5f5;
    padding: 30px;
    border-radius: 8px;
    margin: 30px 0;
  }}

  .weekly-chart-header {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }}

  .weekly-chart-title {{
    color: #333;
    font-size: 1em;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 400;
  }}

  .weekly-chart {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    height: 200px;
    margin: 20px 0;
    padding: 10px 0;
    border-bottom: 2px solid #ddd;
    position: relative;
  }}

  .week-labels {{
    display: flex;
    justify-content: space-between;
    color: #666;
    font-size: 0.85em;
    margin-top: 10px;
  }}

  .week-bar {{
    flex: 1;
    margin: 0 1px;
    min-height: 3px;
    transition: all 0.2s;
    cursor: pointer;
  }}

  .week-bar:hover {{
    opacity: 0.8;
    transform: scaleY(1.05);
  }}

  .all-movies-section {{
    margin-top: 50px;
    border-top: 2px solid #eee;
    padding-top: 30px;
  }}

  .all-movies-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    margin: 20px 0;
  }}

  .all-movies-item {{
    display: flex;
    gap: 10px;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 4px;
  }}

  .all-movies-poster {{
    width: 60px;
    height: 90px;
    object-fit: cover;
    border-radius: 3px;
  }}

  .all-movies-info {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  .all-movies-title {{
    font-weight: 600;
    font-size: 0.9em;
    margin-bottom: 5px;
  }}

  .all-movies-meta {{
    font-size: 0.8em;
    color: #666;
  }}

  .all-movies-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 5px;
  }}

  .movie-tag {{
    font-size: 0.7em;
    padding: 2px 8px;
    background-color: #e8e8e8;
    border-radius: 3px;
    color: #555;
  }}

  @media (max-width: 768px) {{
    .header-logo {{
      width: 63px;
      height: 63px;
    }}

    .header-select, .header-year, .header-reviewed {{
      font-size: 20px;
    }}

    .stat-number {{
      font-size: 62px;
    }}

    .stat-label {{
      font-size: 15px;
    }}

    .movie-item {{
      width: 45%;
    }}

    .person-card, .first-last-item {{
      width: 45%;
    }}

    .all-movies-grid {{
      grid-template-columns: 1fr;
    }}

    .stat-bars {{
      grid-template-columns: 1fr;
    }}

    .person-grid {{
      grid-template-columns: repeat(3, 1fr);
    }}

    .gcl-grid {{
      grid-template-columns: 1fr;
      gap: 30px;
    }}

    .bar-chart-label {{
      min-width: 80px;
    }}

    .stats-summary {{
      flex-direction: column;
      gap: 20px;
    }}

    .day-of-week-chart {{
      margin-left: 0;
      width: 100%;
      max-width: 300px;
    }}
  }}
</style>
<script>
  document.addEventListener('DOMContentLoaded', () => {{
    const selectElement = document.querySelector('.header-select');
    if (selectElement) {{
      selectElement.onchange = (e) => {{
        window.location.href = e.target.value + '.html';
      }};
    }}
  }});
</script>
</head>
<body>
<div class="container">
  <div class="header">
    <h1 style="width: 100%; text-align: center; font-size: 3em; font-weight: 300; margin: 20px 0;">Sim's {YEAR} in Film</h1>
  </div>

  <div class="stats-grid">
    <div class="stat-item">
      <div class="stat-number">{stats['total_films']}</div>
      <div class="stat-label">Diary Entries</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">{len([m for m in movies if m.get('rating', 0) > 0])}</div>
      <div class="stat-label">Rated</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">{stats.get('recent_watches_count', 0)}</div>
      <div class="stat-label">New Releases</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">{total_hours}</div>
      <div class="stat-label">Hours</div>
    </div>
  </div>

  <div class="weekly-chart-container">
    <div class="weekly-chart-header">
      <div class="weekly-chart-title">BY WEEK</div>
    </div>
    <div class="weekly-chart">
      {weekly_bars}
    </div>
    <div class="week-labels">
      <span>Jan</span>
      <span>Dec</span>
    </div>
  </div>

  <div class="stats-summary">
    <div class="summary-item">
      <div class="summary-number">{stats['total_films']}</div>
      <div class="summary-label">Films logged</div>
    </div>
    <div class="summary-arrow">→</div>
    <div class="summary-item">
      <div class="summary-number">{avg_per_month:.1f}</div>
      <div class="summary-label">Average per month</div>
    </div>
    <div class="summary-arrow">→</div>
    <div class="summary-item">
      <div class="summary-number">{avg_per_week:.1f}</div>
      <div class="summary-label">Average per week</div>
    </div>
    <div class="day-of-week-chart">
      {day_bars}
    </div>
  </div>

  <div class="people-section">
    {top_actor_html}
    {top_director_html}
  </div>

  <div class="section-title">HIGHLY RATED FILMS</div>
  <div class="movies-grid">
    {highest_rated_html}
  </div>

  <div class="section-title">LOWEST RATED FILMS</div>
  <div class="movies-grid">
    {lowest_rated_html}
  </div>

  <div class="section-title">OLDEST • NEWEST • LONGEST • SHORTEST</div>
  <div class="first-last-section">
    <div class="first-last-item">
      <div class="first-last-label">OLDEST</div>
      <img src="{oldest_filename}" class="first-last-image"/>
      <div class="first-last-date">{oldest.get('name', '')} ({oldest.get('year', '')})</div>
    </div>
    <div class="first-last-item">
      <div class="first-last-label">NEWEST</div>
      <img src="{newest_filename}" class="first-last-image"/>
      <div class="first-last-date">{newest.get('name', '')} ({newest.get('year', '')})</div>
    </div>
  </div>
  <div class="first-last-section">
    <div class="first-last-item">
      <div class="first-last-label">LONGEST</div>
      <img src="{longest_filename}" class="first-last-image"/>
      <div class="first-last-date">{longest.get('name', '')} ({format_runtime(longest.get('runtime', 0))})</div>
    </div>
    <div class="first-last-item">
      <div class="first-last-label">SHORTEST</div>
      <img src="{shortest_filename}" class="first-last-image"/>
      <div class="first-last-date">{shortest.get('name', '')} ({format_runtime(shortest.get('runtime', 0))})</div>
    </div>
  </div>

  <div class="first-last-section">
    <div class="first-last-item">
      <div class="first-last-label">FIRST WATCH</div>
      <img src="{first_filename}" class="first-last-image"/>
      <div class="first-last-date">{first_date}</div>
    </div>
    <div class="first-last-item">
      <div class="first-last-label">LAST WATCH</div>
      <img src="{last_filename}" class="first-last-image"/>
      <div class="first-last-date">{last_date}</div>
    </div>
  </div>

  <div class="section-title">divergent ratings</div>
  <div class="movies-grid">
    {divergent_higher_html}
  </div>
  <div class="movies-grid">
    {divergent_lower_html}
  </div>

  <div class="section-title">popular watches</div>
  <div class="first-last-section">
    <div class="first-last-item">
      <div class="first-last-label">Most Popular Watch</div>
      <img src="{most_pop_filename}" class="first-last-image"/>
    </div>
    <div class="first-last-item">
      <div class="first-last-label">Least Popular Watch</div>
      <img src="{least_pop_filename}" class="first-last-image"/>
    </div>
  </div>

  <div class="section-title">movie budgets</div>
  <div class="section-subtitle">SMALLEST BUDGETS</div>
  <div class="movies-grid">
    {smallest_budgets_html}
  </div>
  <div class="section-subtitle">BIGGEST BUDGETS</div>
  <div class="movies-grid">
    {biggest_budgets_html}
  </div>

  <div class="gcl-container">
    <div class="gcl-header">
      <div class="gcl-title">Release Years & Decades</div>
      <div style="color: #00a8e1; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;">Most Watched</div>
    </div>
    <div class="gcl-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="gcl-column">
        {release_year_html}
      </div>
      <div class="gcl-column">
        {decades_html}
      </div>
    </div>
  </div>

  <div class="gcl-container">
    <div class="gcl-header">
      <div class="gcl-title">Genres, Countries & Languages</div>
      <div style="color: #00a8e1; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;">Most Watched</div>
    </div>
    <div class="gcl-grid">
      <div class="gcl-column">
        {genres_html}
      </div>
      <div class="gcl-column">
        {countries_html}
      </div>
      <div class="gcl-column">
        {languages_html}
      </div>
    </div>
  </div>

  <div class="section-title">CAST</div>
  <div class="person-grid">
    {top_10_cast_html}
  </div>

  <div class="section-title">DIRECTORS</div>
  <div class="person-grid">
    {top_10_directors_html}
  </div>

  <div class="all-movies-section">
    <div class="section-title">ALL {stats['total_films']} FILMS</div>
    <div class="all-movies-grid">
      {all_movies_html}
    </div>
  </div>

</div>
</body>
</html>
'''

    # Write the HTML file
    with open('sim_{YEAR}.html', 'w') as f:
        f.write(html)

    print("\n" + "=" * 60)
    print("ENHANCED HTML GENERATED!")
    print("=" * 60)
    print("\nCreated: sim_{YEAR}.html")
    print("\nNew sections added:")
    print("  - Weekly activity chart")
    print("  - Release year breakdown")
    print("  - Decades breakdown")
    print("  - Top genres")
    print("  - Top countries & languages")
    print("  - Oldest/Newest/Longest/Shortest films")
    print("  - Complete movie list at bottom")
    print("\nYou can now open this file in a browser to see your 2025 review!")


if __name__ == "__main__":
    main()
