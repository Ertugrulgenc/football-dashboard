import streamlit as st
import pandas as pd
import altair as alt
import re # Import regex for extracting matchday number
from datetime import datetime, timedelta # Import for date calculations

# Set page configuration for a wider layout
st.set_page_config(layout="wide")

# Google Drive file IDs
GAME_EVENTS_FILE_ID = "11L7_jJ_6rU3D43vsd4IQVqY3_BB_l9-H"
GAMES_FILE_ID = "1Z42XEB60ogr280R3FrhvIvqgWaoP81JO"

# Construct Google Drive direct download URLs using f-strings
# For game_events.csv, explicitly using the drive.usercontent.google.com domain
# as seen in the error message, along with &confirm=t.
GAME_EVENTS_CSV_URL = f"https://drive.usercontent.google.com/download?id={GAME_EVENTS_FILE_ID}&export=download&confirm=t"
GAMES_CSV_URL = f"https://drive.google.com/uc?export=download&id={GAMES_FILE_ID}&confirm=t"

# --- Data Loading and Caching (for game_events.csv) ---
@st.cache_data
def load_events_data(file_path):
    """
    Loads the game events data from a CSV file.
    Performs basic data cleaning and type conversion.
    """
    try:
        # Using engine='python' and on_bad_lines='warn' for robustness against malformed CSVs
        df = pd.read_csv(file_path, sep=',', engine='python', on_bad_lines='warn')

        # Check if 'minute' column exists
        if 'minute' not in df.columns:
            st.error(f"Error: 'minute' column not found in game events data. Available columns: {df.columns.tolist()}")
            return None

        # Convert 'minute' to a numeric type, coercing errors to NaN
        df['minute'] = pd.to_numeric(df['minute'], errors='coerce')
        # Drop rows where 'minute' could not be converted (NaNs)
        df.dropna(subset=['minute'], inplace=True)

        # Filter out negative 'minute' values
        df = df[df['minute'] >= 0].copy()

        # Ensure 'type' and 'club_id' are in a suitable format
        df['type'] = df['type'].astype(str)
        df['club_id'] = df['club_id'].astype(str)
        return df
    except Exception as e: # Catch broader exceptions for URL loading
        st.error(f"Error loading game events data from URL: {e}. Please ensure the URL is correct and accessible and the file format is valid CSV.")
        return None

# --- Data Loading and Caching (for games.csv) ---
@st.cache_data
def load_games_data(file_path):
    """
    Loads the games data from a CSV file.
    Extracts matchday number and calculates total goals.
    """
    try:
        # Using engine='python' and on_bad_lines='warn' for robustness against malformed CSVs
        df = pd.read_csv(file_path, sep=',', engine='python', on_bad_lines='warn')

        # Check if essential columns exist before proceeding
        required_cols = ['home_club_goals', 'away_club_goals', 'round', 'date', 'competition_id']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Error: Required column '{col}' not found in games data. Available columns: {df.columns.tolist()}")
                return None

        # Convert goal columns to numeric, coercing errors to NaN
        df['home_club_goals'] = pd.to_numeric(df['home_club_goals'], errors='coerce')
        df['away_club_goals'] = pd.to_numeric(df['away_club_goals'], errors='coerce')
        # Drop rows where goal counts could not be converted
        df.dropna(subset=['home_club_goals', 'away_club_goals'], inplace=True)

        # Calculate total goals
        df['total_goals'] = df['home_club_goals'] + df['away_club_goals']

        # Extract matchday number from 'round' column
        # Use regex to find digits at the beginning of the string
        df['matchday_number'] = df['round'].astype(str).apply(lambda x: int(re.match(r'^\d+', x).group(0)) if re.match(r'^\d+', x) else None)
        df.dropna(subset=['matchday_number'], inplace=True)
        df['matchday_number'] = df['matchday_number'].astype(int)

        # Convert 'date' column to datetime objects for filtering by year
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)

        # Ensure 'competition_id' is in a suitable format
        df['competition_id'] = df['competition_id'].astype(str)
        return df
    except Exception as e: # Catch broader exceptions for URL loading
        st.error(f"Error loading games data from URL: {e}. Please ensure the URL is correct and accessible and the file format is valid CSV.")
        return None


# --- Main Application ---

# Load the data for game events
df_events = load_events_data(GAME_EVENTS_CSV_URL)

# Load the data for games
df_games = load_games_data(GAMES_CSV_URL)

if df_events is not None:
    # --- Dashboard Title ---
    st.title("🏆 Interactive Game Events Dashboard")
    st.markdown("""
    Explore game events using the controls and visualizations below.
    1.  **Select an event type** from the dropdown to see its distribution over the course of a match.
        The first chart now includes an interval for "90+5" minutes.
    2.  The second chart is a **heatmap** showing the frequency of all event types across game minutes.
    3.  The third chart displays **average goals per matchday** for selected competitions, allowing multi-selection and filtering for the last 10 years.
    4.  **Hover over the charts** to see detailed tooltips.
    """)

    # --- UI Interaction: Sidebar for Controls ---
    st.sidebar.header("Dashboard Controls")
    # Create a dropdown for selecting the event type for the first chart.
    event_type_options = sorted(df_events['type'].unique())
    selected_type = st.sidebar.selectbox(
        "Select an Event Type for Histogram:",
        options=event_type_options,
        index=event_type_options.index('Goals') # Default to 'Goals'
    )

    # --- Data Filtering for Histogram ---
    filtered_df = df_events[df_events['type'] == selected_type].copy()

    # --- Visualization 1: Histogram of Events over Time ---
    st.header(f"Distribution of '{selected_type}' Events During a Match")
    st.markdown("This chart shows when events of the selected type occur during a match, including extra time up to 95 minutes.")

    # Define the binning for the first chart to start from 0 and go up to 95 minutes
    # This creates 5-minute intervals: [0,5), [5,10), ..., [85,90), [90,95)
    time_hist = alt.Chart(filtered_df).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3,
        color='#4c78a8' # Static color
    ).encode(
        x=alt.X('minute:Q', bin=alt.Bin(step=5, extent=[0, 95]), title='Game Minute Interval'),
        y=alt.Y('count():Q', title='Number of Events'),
        tooltip=[
            alt.Tooltip('minute:Q', bin=True, title='Time Range (minutes)'),
            alt.Tooltip('count():Q', title='Total Events')
        ]
    ).properties(
        width='container',
        height=300
    )

    st.altair_chart(time_hist, use_container_width=True)


    # --- Visualization 2: Event Type vs. Game Minute Heatmap ---
    st.header("Event Frequency Heatmap by Type and Game Minute")
    st.markdown("This heatmap visualizes the concentration of all event types across different 5-minute intervals of the game.")

    # Prepare data for heatmap: Group by binned minute and event type, then count
    heatmap_data = df_events.copy()
    # Remove 'Shootout' events from the heatmap data
    heatmap_data = heatmap_data[heatmap_data['type'] != 'Shootout'].copy()

    # Bin 'minute' into 5-minute intervals, extending up to 95 minutes
    bins_range = list(range(0, 100, 5))
    labels = [f'{i}-{i+4}' for i in range(0, 90, 5)] + ['90-95+']
    heatmap_data['minute_bin'] = pd.cut(heatmap_data['minute'],
                                        bins=bins_range,
                                        right=False,
                                        labels=labels,
                                        include_lowest=True
                                       )

    # Aggregate counts for the heatmap
    heatmap_counts = heatmap_data.groupby(['minute_bin', 'type']).size().reset_index(name='count')

    # Ensure all event types (excluding 'Shootout') are represented across all minute bins for consistent heatmap
    all_minutes = labels
    all_types = sorted(heatmap_counts['type'].unique())
    full_grid = pd.MultiIndex.from_product([all_minutes, all_types], names=['minute_bin', 'type']).to_frame(index=False)

    # Merge with actual counts, filling missing combinations with 0
    heatmap_final_df = pd.merge(full_grid, heatmap_counts, on=['minute_bin', 'type'], how='left').fillna(0)

    # Define the order of minute bins for the x-axis
    minute_bin_order = labels

    heatmap_chart = alt.Chart(heatmap_final_df).mark_rect().encode(
        x=alt.X('minute_bin:N', title='Game Minute Interval', sort=minute_bin_order),
        y=alt.Y('type:N', title='Event Type'),
        color=alt.Color('count:Q', title='Number of Events', scale=alt.Scale(range='heatmap')),
        tooltip=[
            alt.Tooltip('minute_bin:N', title='Minute Interval'),
            alt.Tooltip('type:N', title='Event Type'),
            alt.Tooltip('count:Q', title='Number of Events')
        ]
    ).properties(
        width='container',
        height=500
    )

    st.altair_chart(heatmap_chart, use_container_width=True)

    # --- Visualization 3: Average Goals per Matchday ---
    if df_games is not None:
        st.header("Average Goals per Matchday by Competition")
        st.markdown("This chart shows the average of home and away goals for each matchday, filtered by competition.")

        # Define the allowed competition IDs
        allowed_competition_ids = ['FR1', 'GB1', 'TR1', 'IT1', 'NL1', 'ES1']

        # Filter the unique competition options to only include the allowed ones
        competition_options = sorted([comp for comp in df_games['competition_id'].unique() if comp in allowed_competition_ids])

        # Sidebar control for competition_id (changed to multiselect)
        selected_competitions = st.sidebar.multiselect(
            "Select Competition IDs for Goals per Matchday:",
            options=competition_options,
            default=[comp for comp in allowed_competition_ids if comp in competition_options]
        )

        # Checkbox for last 10 years filter
        show_last_10_years = st.sidebar.checkbox("Show data from last 10 years only", value=True)

        if selected_competitions:
            filtered_games_df = df_games[df_games['competition_id'].isin(selected_competitions)].copy()

            # Apply "last 10 years" filter if checkbox is selected
            if show_last_10_years and not filtered_games_df.empty:
                latest_date = filtered_games_df['date'].max()
                start_date_filter = latest_date - timedelta(days=365*10)
                filtered_games_df = filtered_games_df[filtered_games_df['date'] >= start_date_filter].copy()

            # Apply TR1 matchday limit if TR1 is selected and data exists for it
            if 'TR1' in selected_competitions and not filtered_games_df.empty:
                tr1_df = filtered_games_df[
                    (filtered_games_df['competition_id'] == 'TR1') &
                    (filtered_games_df['matchday_number'] <= 40)
                ].copy()

                filtered_games_df = filtered_games_df[filtered_games_df['competition_id'] != 'TR1']
                filtered_games_df = pd.concat([filtered_games_df, tr1_df])

            # Aggregate average goals per matchday per competition
            goals_per_matchday = filtered_games_df.groupby(['matchday_number', 'competition_id'])['total_goals'].mean().reset_index()

            # Create the line chart with color encoding for competition_id
            goals_chart = alt.Chart(goals_per_matchday).mark_line(point=True).encode(
                x=alt.X('matchday_number:Q', title='Matchday Number', scale=alt.Scale(domainMin=0)),
                y=alt.Y('total_goals:Q', title='Average Goals'),
                color=alt.Color('competition_id:N', title='Competition ID'),
                tooltip=[
                    alt.Tooltip('matchday_number:Q', title='Matchday'),
                    alt.Tooltip('competition_id:N', title='Competition'),
                    alt.Tooltip('total_goals:Q', title='Average Goals', format='.2f')
                ]
            ).properties(
                width='container',
                height=400,
                title="Average Goals per Matchday for Selected Competitions"
            ).interactive()

            st.altair_chart(goals_chart, use_container_width=True)
        else:
            st.info("Please select at least one competition to view the chart.")
    else:
        st.warning("Could not load 'games.csv' data for 'Average Goals per Matchday' chart. Please check the file path and try again.")

else:
    st.warning("Data could not be loaded. Please check the file path and try again.")
