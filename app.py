import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def extract_and_save_data(input_file="watch-history.json", output_file_youtube="youtube_data.json", output_file_youtube_music="youtube_music_data.json"):
    """
    Extracts data from the input JSON file based on headers and saves them into separate JSON files.

    Parameters:
        input_file (str): Path to the input JSON file.
        output_file_youtube (str): Path to save the extracted YouTube data.
        output_file_youtube_music (str): Path to save the extracted YouTube Music data.
    """
    try:
        # Read data from the input file with explicit encoding
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Initialize lists to store extracted data
        youtube_data = []
        youtube_music_data = []

        # Extract data for YouTube and YouTube Music
        for item in data:
            if item["header"] == "YouTube Music":
                youtube_music_data.append(item)
            elif item["header"] == "YouTube":
                youtube_data.append(item)

        # Save extracted data into separate JSON files
        with open(output_file_youtube, "w") as youtube_file:
            json.dump(youtube_data, youtube_file, indent=2)

        print("Extraction and saving completed.")
    except Exception as e:
        print(f"Error: {e}")
        

def json_to_dataframe(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return pd.DataFrame(data)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON file '{file_path}'.")
        return None

def clean_data(df):
    try:
        columns_to_drop = ['details', 'activityControls', 'products', 'header']
        df_cleaned = df.drop(columns=columns_to_drop)
        df_cleaned['title'] = df_cleaned['title'].str.replace('Watched', '')
        return df_cleaned
    except KeyError as e:
        print(f"Error: Key '{e}' not found in DataFrame.")
        return None

def extract_time_components(df):
    try:
        df['time'] = df['time'].apply(convert_to_datetime)
    except ValueError:
        print("Error: Unable to parse datetime string")
        return df
    
    try:
        if 'time' in df:
            df['day'] = df['time'].dt.day
            df['month'] = df['time'].dt.month
            df['year'] = df['time'].dt.year
            df['hour'] = df['time'].dt.hour
            df['minute'] = df['time'].dt.minute
            df['second'] = df['time'].dt.second
        return df
    except KeyError as e:
        print(f"Error: Key '{e}' not found in DataFrame.")
        return None

def convert_to_datetime(date_str):
    try:
        return pd.to_datetime(date_str)
    except ValueError:
        pass
    
    try:
        return pd.to_datetime(date_str, format='%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        pass
    
    try:
        return pd.to_datetime(date_str, format='%Y/%m/%d %H:%M:%S')
    except ValueError:
        pass
    
    try:
        return pd.to_datetime(date_str, format='%b %d, %Y %H:%M:%S')
    except ValueError:
        pass

    print(f"Error: Unable to convert '{date_str}' to datetime.")
    return None

def extract_time_of_day(hour):
    if 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    elif 18 <= hour < 24:
        return 'Evening'
    else:
        return 'Night'

def extract_season(month):
    if 3 <= month <= 5:
        return 'Spring'
    elif 6 <= month <= 8:
        return 'Summer'
    elif 9 <= month <= 11:
        return 'Autumn'
    else:
        return 'Winter'
    
def extract_weekend(day):
    if day in [5, 6]:
        return True
    else:
        return False

def process_json_data(file_path):
    df = json_to_dataframe(file_path)
    if df is not None:
        df_cleaned = clean_data(df)
        if df_cleaned is not None:
            df_cleaned = extract_time_components(df_cleaned)
            if df_cleaned is not None:
                df_cleaned['time'] = df_cleaned['time'].apply(convert_to_datetime)
                df_cleaned['time_of_day'] = df_cleaned['hour'].apply(extract_time_of_day)
                df_cleaned['season'] = df_cleaned['month'].apply(extract_season)
                df_cleaned['weekend'] = df_cleaned['time'].dt.weekday.apply(extract_weekend)
                return df_cleaned
    return None

# Function to visualize distribution of views over time_of_day
def visualize_time_of_day(df):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(x='time_of_day', data=df, ax=ax)
    ax.set_title('Distribution of Views by Time of Day')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Count of Views')
    st.pyplot(fig)

# Function to visualize views by season
def visualize_season(df):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(x='season', data=df, ax=ax)
    ax.set_title('Views by Season')
    ax.set_xlabel('Season')
    ax.set_ylabel('Count of Views')
    st.pyplot(fig)

# Function to visualize views on weekends vs weekdays
def visualize_weekend(df):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(x='weekend', data=df, ax=ax)
    ax.set_title('Views on Weekends vs Weekdays')
    ax.set_xlabel('Is Weekend?')
    ax.set_ylabel('Count of Views')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Weekday', 'Weekend'])
    st.pyplot(fig)

# Function to visualize views over months
def visualize_monthly_views(df):
    monthly_views = df.groupby('month').size()
    fig, ax = plt.subplots(figsize=(10, 6))
    monthly_views.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Monthly Views')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Views')
    ax.set_xticklabels(monthly_views.index, rotation=0)
    st.pyplot(fig)

# Function to visualize views by hour
def visualize_hourly_views(df):
    hourly_views = df.groupby('hour').size()
    fig, ax = plt.subplots(figsize=(12, 6))
    hourly_views.plot(kind='line', marker='o', color='orange', ax=ax)
    ax.set_title('Hourly Views')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Number of Views')
    ax.set_xticks(range(0, 24))
    ax.grid(True)
    st.pyplot(fig)

# Main Streamlit app
def main():
    st.title('YouTube Data Visualization')
    extract_and_save_data()
    youtube_data_df = process_json_data("youtube_data.json")
    if youtube_data_df is not None:
        st.subheader('Visualizations:')
        visualize_time_of_day(youtube_data_df)
        visualize_season(youtube_data_df)
        visualize_weekend(youtube_data_df)
        visualize_monthly_views(youtube_data_df)
        visualize_hourly_views(youtube_data_df)

if __name__ == "__main__":
    main()
