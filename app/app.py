"""
Rekordbox Collection Analyzer - Streamlit Web App

Upload your Rekordbox XML collection export and get insights about your music collection.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Tuple
from io import StringIO

# ============================================================================
# Configuration & Setup
# ============================================================================

st.set_page_config(
    page_title="Rekordbox Collection Analyzer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎵 Rekordbox Collection Analyzer")
st.markdown("Upload your Rekordbox XML collection export to explore your music collection with interactive visualizations.")

# ============================================================================
# Parsing Functions
# ============================================================================

def parse_tempo_marks(track_elem: ET.Element) -> List[Dict[str, Any]]:
    """Extract tempo marks from a track element."""
    tempos = []
    for tempo in track_elem.findall('TEMPO'):
        tempos.append({
            'start': float(tempo.get('Inizio', 0)),
            'bpm': float(tempo.get('Bpm', 0)),
            'meter': tempo.get('Metro', '4/4'),
            'beat': int(tempo.get('Battito', 0))
        })
    return tempos

def parse_position_marks(track_elem: ET.Element) -> List[Dict[str, Any]]:
    """Extract position marks (cue points) from a track element."""
    marks = []
    for mark in track_elem.findall('POSITION_MARK'):
        mark_data = {
            'name': mark.get('Name', ''),
            'type': int(mark.get('Type', 0)),
            'start': float(mark.get('Start', 0)),
            'num': int(mark.get('Num', -1)),
        }
        # Add color info if present
        if mark.get('Red'):
            mark_data['color'] = {
                'red': int(mark.get('Red')),
                'green': int(mark.get('Green')),
                'blue': int(mark.get('Blue'))
            }
        marks.append(mark_data)
    return marks

def parse_track(track_elem: ET.Element) -> Dict[str, Any]:
    """Convert a track XML element to a dictionary."""
    track = {
        'track_id': track_elem.get('TrackID'),
        'name': track_elem.get('Name', ''),
        'artist': track_elem.get('Artist', ''),
        'composer': track_elem.get('Composer', ''),
        'album': track_elem.get('Album', ''),
        'genre': track_elem.get('Genre', ''),
        'kind': track_elem.get('Kind', ''),
        'size': int(track_elem.get('Size', 0)),
        'total_time': int(track_elem.get('TotalTime', 0)),
        'year': int(track_elem.get('Year', 0)),
        'average_bpm': float(track_elem.get('AverageBpm', 0)),
        'date_added': track_elem.get('DateAdded', ''),
        'bit_rate': int(track_elem.get('BitRate', 0)),
        'sample_rate': int(track_elem.get('SampleRate', 0)),
        'play_count': int(track_elem.get('PlayCount', 0)),
        'rating': int(track_elem.get('Rating', 0)),
        'location': track_elem.get('Location', ''),
        'tonality': track_elem.get('Tonality', ''),
        'tempos': parse_tempo_marks(track_elem),
        'position_marks': parse_position_marks(track_elem),
    }
    return track

def parse_rekordbox_xml(xml_content: str) -> pd.DataFrame:
    """Parse Rekordbox XML collection and return a DataFrame."""
    root = ET.fromstring(xml_content)
    collection = root.find('COLLECTION')

    if collection is None:
        raise ValueError("No COLLECTION element found in XML")

    tracks = []
    for track_elem in collection.findall('TRACK'):
        tracks.append(parse_track(track_elem))

    return pd.DataFrame(tracks)

# ============================================================================
# Sidebar: File Upload
# ============================================================================

with st.sidebar:
    st.header("📁 Upload Collection")
    uploaded_file = st.file_uploader(
        "Select your Rekordbox XML collection file",
        type=['xml'],
        help="Export your collection from Rekordbox as XML"
    )

# ============================================================================
# Main App
# ============================================================================

if uploaded_file is not None:
    # Parse the file
    try:
        xml_content = uploaded_file.read().decode('utf-8')
        df = parse_rekordbox_xml(xml_content)

        st.success(f"✅ Successfully loaded {len(df)} tracks!")

        # ====================================================================
        # Key Statistics
        # ====================================================================

        st.header("📊 Collection Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Tracks", len(df))

        with col2:
            total_hours = df['total_time'].sum() / 3600
            st.metric("Total Duration", f"{total_hours:.1f} hours")

        with col3:
            unique_artists = df['artist'].nunique()
            st.metric("Unique Artists", unique_artists)

        with col4:
            unique_genres = df['genre'].nunique()
            st.metric("Unique Genres", unique_genres)

        # ====================================================================
        # Top Tracks by Play Count
        # ====================================================================

        st.header("🔥 Most Played Tracks")

        top_tracks = df.nlargest(25, 'play_count')[['name', 'artist', 'play_count', 'genre', 'average_bpm']].reset_index(drop=True)
        top_tracks.index = top_tracks.index + 1

        col_viz, col_table = st.columns([2, 1])

        with col_viz:
            # Bar chart of top 25 for visibility
            top_25 = df.nlargest(25, 'play_count').sort_values('play_count')
            fig_plays = px.bar(
                top_25,
                x='play_count',
                y='name',
                orientation='h',
                title='Top 25 Most Played Tracks',
                labels={'play_count': 'Play Count', 'name': 'Track Name'},
                color='play_count',
                color_continuous_scale='Viridis'
            )
            fig_plays.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_plays, config={})

        with col_table:
            st.subheader("Top Tracks")
            st.dataframe(top_tracks, width='stretch', height=400)

        # ====================================================================
        # BPM Distribution
        # ====================================================================

        st.header("🎼 BPM Distribution")

        col_hist, col_stats = st.columns([2, 1])

        with col_hist:
            fig_bpm = px.histogram(
                df[df['average_bpm'] > 0],
                x='average_bpm',
                nbins=50,
                title='Distribution of Track BPMs',
                labels={'average_bpm': 'BPM'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_bpm.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bpm, config={})

        with col_stats:
            bpm_data = df[df['average_bpm'] > 0]['average_bpm']
            st.metric("Median BPM", f"{bpm_data.median():.1f}")
            st.metric("Mean BPM", f"{bpm_data.mean():.1f}")
            st.metric("Min BPM", f"{bpm_data.min():.1f}")
            st.metric("Max BPM", f"{bpm_data.max():.1f}")

        # ====================================================================
        # Genre Breakdown
        # ====================================================================

        st.header("🎸 Genre Breakdown")

        col_genre_pie, col_genre_bar = st.columns(2)

        with col_genre_pie:
            genre_counts = df[df['genre'] != ''].groupby('genre').size().sort_values(ascending=False).head(20)
            fig_genre_pie = px.pie(
                values=genre_counts.values,
                names=genre_counts.index,
                title='Top 20 Genres (by track count)'
            )
            st.plotly_chart(fig_genre_pie, config={})

        with col_genre_bar:
            # Split genres by comma and count individual genres
            expanded_genres = []
            for genres_str in df[df['genre'] != '']['genre']:
                # Split by comma and strip whitespace
                individual_genres = [g.strip() for g in genres_str.split(',')]
                expanded_genres.extend(individual_genres)

            # Count individual genres
            from collections import Counter
            genre_counter = Counter(expanded_genres)
            genre_split_counts = pd.Series(dict(genre_counter)).sort_values(ascending=True).tail(15)

            fig_genre_split = px.bar(
                x=genre_split_counts.values,
                y=genre_split_counts.index,
                orientation='h',
                title='Top 15 Genres (by track count, split)',
                labels={'x': 'Track Count', 'y': 'Genre'},
                color=genre_split_counts.values,
                color_continuous_scale='Plasma'
            )
            fig_genre_split.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_genre_split, config={})

        # ====================================================================
        # Artist Breakdown
        # ====================================================================

        st.header("👨‍🎤 Top Artists")

        col_artist_plays, col_artist_count = st.columns(2)

        with col_artist_plays:
            artist_plays = df[df['artist'] != ''].groupby('artist')['play_count'].sum().sort_values(ascending=True).tail(20)
            fig_artist_plays = px.bar(
                x=artist_plays.values,
                y=artist_plays.index,
                orientation='h',
                title='Top 20 Artists (by play count)',
                labels={'x': 'Total Play Count', 'y': 'Artist'},
                color=artist_plays.values,
                color_continuous_scale='Blues'
            )
            fig_artist_plays.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_artist_plays, config={})

        with col_artist_count:
            artist_counts = df[df['artist'] != ''].groupby('artist').size().sort_values(ascending=True).tail(20)
            fig_artist_count = px.bar(
                x=artist_counts.values,
                y=artist_counts.index,
                orientation='h',
                title='Top 20 Artists (by track count)',
                labels={'x': 'Track Count', 'y': 'Artist'},
                color=artist_counts.values,
                color_continuous_scale='Greens'
            )
            fig_artist_count.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_artist_count, config={})

        # ====================================================================
        # Key Distribution
        # ====================================================================

        st.header("🎹 Key Distribution")

        col_key_counts, col_key_empty = st.columns([2, 1])

        with col_key_counts:
            key_counts = df[df['tonality'] != ''].groupby('tonality').size().sort_values(ascending=True).tail(30)
            fig_key = px.bar(
                x=key_counts.values,
                y=key_counts.index,
                orientation='h',
                title='Top 30 Keys (by track count)',
                labels={'x': 'Track Count', 'y': 'Key'},
                color=key_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_key.update_layout(showlegend=False, height=600)
            st.plotly_chart(fig_key, config={})

        # ====================================================================
        # Data Export
        # ====================================================================

        st.header("📥 Export Data")

        col_csv, col_json = st.columns(2)

        with col_csv:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="collection_analysis.csv",
                mime="text/csv"
            )

        with col_json:
            # Create NDJSON format
            ndjson_data = df.to_json(orient='records', lines=True)
            st.download_button(
                label="Download as NDJSON",
                data=ndjson_data,
                file_name="collection_analysis.ndjson",
                mime="application/x-ndjson"
            )

        # ====================================================================
        # Detailed Data Table
        # ====================================================================

        st.header("📋 Detailed Track Data")

        # Create display dataframe with selected columns
        display_df = df[['name', 'artist', 'genre', 'tonality', 'average_bpm', 'play_count', 'date_added']].copy()
        display_df.columns = ['Track', 'Artist', 'Genre', 'Key', 'BPM', 'Plays', 'Added']

        st.dataframe(display_df, width='stretch', height=600)

    except Exception as e:
        st.error(f"❌ Error parsing file: {str(e)}")

else:
    st.info("👈 Upload a Rekordbox XML collection file to get started!")

    st.markdown("""
    ## How to Export Your Rekordbox Collection

    To get your Rekordbox XML collection file:

    1. Open **Rekordbox** on your computer
    2. Go to **File** menu
    3. Select **Export Collection in xml format**
    4. Choose a location to save the file
    5. Upload the exported XML file using the file uploader on the left

    Once uploaded, you'll be able to explore your entire music collection with interactive visualizations!
    """)
