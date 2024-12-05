import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


season_stats = r"C:\Users\pillb\Documents\blog2\utah_nhl_players_stats.csv"
personal_info = r"C:\Users\pillb\Documents\blog2\utah_nhl_players_info.csv"

#load CSV files
season_stats_df = pd.read_csv(season_stats)
personal_info_df = pd.read_csv(personal_info)

#clean up names
season_stats_df['Player Name'] = season_stats_df['Player Name'].str.replace('-', ' ').str.title()


def convert_toi_to_seconds(toi):
    try:
        minutes, seconds = map(int, toi.split(':'))
        return minutes * 60 + seconds
    except:
        return None

def convert_height_to_inches(height):
        feet, inches = map(int, height.replace('"', '').split("'"))
        return feet * 12 + inches

#apply the function to the TOI/G column
season_stats_df['TOI/G_seconds'] = season_stats_df['TOI/G'].apply(convert_toi_to_seconds)
season_stats_df['TOI/G_minutes'] = season_stats_df['TOI/G_seconds'] / 60


#streamlit app
st.title("NHL Players Stats Viewer")

tab1, tab2, tab3= st.tabs(["Player Statistics", "Player Demographic", "Player Details"])

#Tab 1
with tab1:
    st.header("Visualize Player Statistics")
    
    # User choice: Career, specific season, or average stats
    view_choice = st.radio(
        "Choose a view:",
        options=["Career Stats", "Specific Season", "Career Averages"],
        horizontal=True,
    )
    
    if view_choice == "Career Stats":
        # Filter to only 'Career' rows
        career_df = season_stats_df[season_stats_df['Season'] == 'Career']
        st.subheader("Career Totals")
        
    elif view_choice == "Specific Season":
        # Dropdown for season selection
        seasons = sorted(season_stats_df["Season"].unique())
        selected_season = st.selectbox("Select a season:", seasons)
        
        # Filter for the selected season
        career_df = season_stats_df[season_stats_df["Season"] == selected_season]
        st.subheader(f"Stats for {selected_season}")
        
    elif view_choice == "Career Averages":
        # Exclude 'Career' row and calculate averages
        avg_df = season_stats_df[season_stats_df["Season"] != "Career"]
        numeric_columns = avg_df.select_dtypes(include='number')
        avg_df = avg_df.groupby("Player Name").mean().reset_index()
        career_df = avg_df
        st.subheader("Career Averages (Excluding Career Rows)")
    
    # Let users select a statistic to visualize, excluding certain columns
    exclude_columns = ["Player ID", "TOI/G_seconds"]
    stat_columns = [col for col in career_df.select_dtypes(include='number').columns if col not in exclude_columns]
    selected_stat = st.selectbox("Select a statistic to visualize:", stat_columns)
    
    # Add a slider to select the number of bars
    max_bars = len(career_df)
    num_bars = st.slider("Number of players to display:", min_value=1, max_value=max_bars, value=min(10, max_bars))
    
    # Sort data by selected stat and limit the number of bars
    sorted_df = career_df.sort_values(by=selected_stat, ascending=False).head(num_bars)
    fig = px.bar(
        sorted_df,
        x="Player Name",
        y=selected_stat,
        title=f"{view_choice} - {selected_stat}",
        labels={"Player Name": "Player", selected_stat: selected_stat},
        text=selected_stat,
    )
    st.plotly_chart(fig)

# Tab 2: Scatter Plot
with tab2:
    st.header("Height vs. Weight Scatter Plot")
    
    # Process Height: Convert to numeric (inches)
    personal_info_df['Height'] = personal_info_df['Height'].apply(convert_height_to_inches)
    
    # Ensure Weight is numeric
    personal_info_df['Weight'] = pd.to_numeric(personal_info_df['Weight'], errors='coerce')
    
    # Drop rows with missing or invalid data
    scatter_df = personal_info_df.dropna(subset=["Height", "Weight"])
    
    # Dropdown to choose color dimension
    color_by = st.radio(
        "Color by:",
        options=["Position", "Handedness"],
        horizontal=True,
    )
    
    # Create scatter plot using Plotly
    fig = px.scatter(
        scatter_df,
        x="Weight",
        y="Height",
        color=color_by,
        title="Height vs. Weight",
        labels={"Weight": "Weight (lbs)", "Height": "Height (inches)", color_by: color_by},
        hover_data=["Player Name"],
    )
    
    st.plotly_chart(fig)

# Tab 3: Player Details
with tab3:
    st.header("Player Details")
    
    # Dropdown to select a player
    player_list = season_stats_df["Player Name"].unique()
    selected_player = st.selectbox("Select a player:", sorted(player_list))
    
    # Filter stats for the selected player
    player_stats = season_stats_df[season_stats_df["Player Name"] == selected_player]
    player_info = personal_info_df[personal_info_df["Player Name"] == selected_player]
    
    # Display Player Stats Table
    st.subheader(f"{selected_player} - Season Stats")
    st.dataframe(player_stats)
    
    
    # Display Player Info as a text line
    st.subheader(f"{selected_player} - Personal Information")
    if not player_info.empty:
        for col, val in player_info.iloc[0].items():
            st.write(f"**{col}:** {val}")
    else:
        st.write("No personal information available.")