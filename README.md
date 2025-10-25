# Rekordbox Collection Analyzer

A Streamlit web application for analyzing and visualizing your Rekordbox DJ music collection.

## Features

- **Upload & Parse**: Upload your Rekordbox XML collection export
- **Collection Overview**: Total tracks, duration, unique artists, genres, and average rating
- **Top Tracks**: Bar chart and table of your most-played tracks
- **BPM Distribution**: Histogram showing the spread of track BPMs
- **Genre Breakdown**: Pie chart and bar chart of genre statistics
- **Artist Analysis**: Most-played artists and artists with most tracks
- **Rating Distribution**: Histogram of track ratings
- **Data Export**: Download analysis results as CSV or NDJSON

## Requirements

- Python 3.8+
- Dependencies: streamlit, pandas, plotly

## Installation

Install dependencies using uv:

```bash
uv sync
```

Or using pip with the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Running the App

```bash
uv run streamlit run app.py
```

The app will start on `http://localhost:8501`

## Usage

1. Click "Upload" in the sidebar
2. Select your Rekordbox XML collection file
3. Explore the various analyses and visualizations
4. Download results as CSV or NDJSON if desired

## Data Format

The app expects a Rekordbox XML collection export. Each track contains:

- **Basic Info**: Track name, artist, composer, album, genre
- **Audio Properties**: File type, size, duration, bit rate, sample rate
- **Musical Data**: BPM, key/tonality, year
- **DJ Data**: Play count, rating, date added, file location
- **Advanced**: Tempo changes, cue points with colors

## Output

### CSV Export
All track data in tabular format, suitable for spreadsheet analysis.

### NDJSON Export
Newline-delimited JSON format, one track per line. Great for streaming processing or database imports.

## Files

- `app.py`: Main Streamlit application
- `README.md`: This file
