import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
from screentime import query_database

# Default values
DEFAULT_UNNECESSARY_APPS = ['ios', 'Netflix', 'Tweetie2']
DEFAULT_SCREEN_TIME_GOAL = 1  # in hours
DEFAULT_PICKUP_GOAL = 50

# Alternative activities
ALTERNATIVE_ACTIVITIES = [
    "Write in your notebook",
    "Take a walk",
    "Message a friend",
    "Go to the gym",
    "Play with the baby",
    "Read a book",
    "Practice meditation",
    "Learn a new skill online"
]

def convert_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, pytz.UTC)

def seconds_to_hours(seconds):
    return seconds / 3600

def get_color(value, thresholds):
    if value < thresholds[0]:
        return "green"
    elif value < thresholds[1]:
        return "yellow"
    else:
        return "red"

def get_color_intensity(hours, goal):
    if hours < goal * 0.25:
        return "rgba(0, 255, 0, 0.1)"  # Very light green
    elif hours < goal * 0.5:
        return "rgba(0, 255, 0, 0.4)"  # Light green
    elif hours < goal * 0.75:
        return "rgba(0, 255, 0, 0.7)"  # Medium green
    else:
        return "rgba(0, 255, 0, 1)"    # Dark green

def main():
    local_tz = datetime.now().astimezone().tzinfo
    st.title(f"Screen Time Goal Tracker")

    # Sidebar for user inputs
    st.sidebar.header("Settings")

    # Screen time goal input (using float)
    screen_time_goal = st.sidebar.number_input("Daily Screen Time Goal (hours)", 
                                            min_value=0.1, 
                                            max_value=24.0, 
                                            value=float(DEFAULT_SCREEN_TIME_GOAL), 
                                            step=0.1)

    # Pickup goal input (using int)
    pickup_goal = st.sidebar.number_input("Daily Pickup Goal", 
                                        min_value=1, 
                                        max_value=1000, 
                                        value=int(DEFAULT_PICKUP_GOAL), 
                                        step=1)

    # Unnecessary apps input (unchanged)
    unnecessary_apps = st.sidebar.text_area("Unnecessary Apps (one per line)", 
                                            value="\n".join(DEFAULT_UNNECESSARY_APPS))
    unnecessary_apps = [app.strip() for app in unnecessary_apps.split("\n") if app.strip()]

    # Calculate thresholds based on user inputs
    screen_time_thresholds = [0.75 * screen_time_goal, screen_time_goal]
    pickup_thresholds = [0.75 * pickup_goal, pickup_goal]

    try: 
        # Set the date range for the last 4 weeks
        end_date = datetime.now(local_tz)
        start_date = end_date - timedelta(weeks=4)

        # Fetch data for the last 4 weeks
        all_data = query_database(start_date=start_date, end_date=end_date)
        df = pd.DataFrame(all_data)

        # Find the most recent date in the data
        most_recent_date = df['end_time'].max().date()
        st.subheader(f"Data updated to: {most_recent_date.strftime('%Y-%m-%d')}")

        # Convert usage from seconds to hours
        df["usage_hours"] = df["usage"].apply(seconds_to_hours)

        # Clean the device_model column
        df['device_model'] = df['device_model'].fillna('').astype(str)

        # Filter for iPhone data
        iphone_df = df[df['device_model'].str.contains('iPhone', case=False, na=False)]

        # If no iPhone data is found, show a message and stop execution
        if iphone_df.empty:
            st.error("No iPhone data found. Please check your data source.")
            return

        # 1. Display goals
        st.header("Screen Time Goals")
        st.write(f"1. Unnecessary screen time < {screen_time_goal}h")
        st.write(f"2. Pickups < {pickup_goal}")

        # 2. Calculate unnecessary screen time and accesses
        unnecessary_df = iphone_df[iphone_df['app'].str.contains('|'.join(unnecessary_apps), case=False, na=False)]
        today_unnecessary = unnecessary_df[unnecessary_df['start_time'].dt.date == end_date.date()]['usage_hours'].sum()
        today_accesses = unnecessary_df[unnecessary_df['start_time'].dt.date == end_date.date()].shape[0]

        # Display unnecessary screen time and accesses side by side
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Today's Unnecessary Screen Time")
            color = get_color(today_unnecessary, screen_time_thresholds)
            st.markdown(f"<h1 style='color: {color};'>{today_unnecessary:.2f} hours</h1>", unsafe_allow_html=True)

        with col2:
            st.subheader("Today's Number of Accesses")
            color = get_color(today_accesses, pickup_thresholds)
            st.markdown(f"<h1 style='color: {color};'>{today_accesses}</h1>", unsafe_allow_html=True)

        if get_color(today_unnecessary, screen_time_thresholds) == "red":
            st.subheader("Suggestions for alternative activities:")
            for activity in ALTERNATIVE_ACTIVITIES:
                st.write(f"- {activity}")

        # 3. Daily screen time trend for the last 4 weeks
        st.header("Daily Screen Time Trend (Last 4 Weeks)")
        daily_usage = iphone_df.groupby(iphone_df["start_time"].dt.date)["usage_hours"].sum().reset_index()
        fig_daily = px.bar(daily_usage, x="start_time", y="usage_hours", 
                        labels={"usage_hours": "Total Usage (hours)", "start_time": "Date"},
                        title="Daily Screen Time (Last 4 Weeks)")
        fig_daily.update_traces(texttemplate='%{y:.2f}', textposition='outside')
        st.plotly_chart(fig_daily)

        # 4. Daily pickups trend for the last 4 weeks
        st.header("Daily Pickups Trend (Last 4 Weeks)")
        daily_pickups = iphone_df.groupby(iphone_df["start_time"].dt.date).size().reset_index(name='pickups')
        fig_pickups = px.line(daily_pickups, x="start_time", y="pickups", 
                            labels={"pickups": "Number of Pickups", "start_time": "Date"},
                            title="Daily Pickups (Last 4 Weeks)")
        fig_pickups.update_traces(mode="markers+lines", marker=dict(size=8), texttemplate='%{y}', textposition='top center')
        st.plotly_chart(fig_pickups)

        # 5. Daily goal achievement for the last week (commit-graph style)
        st.header("Daily Screen Time Achievement (Last Week)")
        last_week_start = end_date - timedelta(days=6)
        last_week_df = iphone_df[iphone_df["start_time"].dt.date >= last_week_start.date()]
        daily_achievement = last_week_df.groupby(last_week_df["start_time"].dt.date)["usage_hours"].sum().reset_index()
        daily_achievement['unnecessary_time'] = unnecessary_df[unnecessary_df["start_time"].dt.date >= last_week_start.date()].groupby(unnecessary_df["start_time"].dt.date)["usage_hours"].sum().reset_index()["usage_hours"]
        daily_achievement['accesses'] = unnecessary_df[unnecessary_df["start_time"].dt.date >= last_week_start.date()].groupby(unnecessary_df["start_time"].dt.date).size().reset_index()[0]
        
        fig_achievement = go.Figure()
        
        for i, row in daily_achievement.iterrows():
            color = get_color_intensity(row['unnecessary_time'], screen_time_goal)
            fig_achievement.add_trace(go.Scatter(
                x=[row['start_time'], row['start_time']],
                y=[0, 1],
                mode='lines',
                line=dict(color=color, width=20),
                name=f"{row['start_time'].strftime('%Y-%m-%d')}: {row['unnecessary_time']:.2f} hours"
            ))

        fig_achievement.update_layout(
            title="Daily Screen Time Achievement (Last Week)",
            xaxis_title="Date",
            yaxis_title="",
            yaxis=dict(showticklabels=False, showgrid=False),
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_achievement)

        # Add a legend explaining the color intensities
        st.write("Color intensity guide:")
        col1, col2, col3, col4 = st.columns(4)
        col1.color_picker(f"< {screen_time_goal/4}h", "#E6FFE6", disabled=True)
        col2.color_picker(f"{screen_time_goal/4}h - {screen_time_goal/2}h", "#66FF66", disabled=True)
        col3.color_picker(f"{screen_time_goal/2}h - {3*screen_time_goal/4}h", "#00FF00", disabled=True)
        col4.color_picker(f"> {3*screen_time_goal/4}h", "#00CC00", disabled=True)

        # 6. Table of app usage for the last 24 hours
        st.header("App Usage Details (Last 24 Hours)")
        
        # Calculate the start time for the last 24 hours
        last_24_hours = end_date - timedelta(days=1)
        
        # Filter data for the last 24 hours
        last_day_df = iphone_df[iphone_df['end_time'] >= last_24_hours]
        
        # Prepare data for the table
        app_usage = last_day_df.groupby('app')['usage_hours'].sum().reset_index()
        app_usage = app_usage.sort_values('usage_hours', ascending=False)
        app_usage['usage_hours'] = app_usage['usage_hours'].round(2)
        
        # Display the table using Streamlit's native table function
        st.dataframe(app_usage, use_container_width=True)

        # Update any date/time displays to show they're in local time
        st.write(f"All times are in your local timezone: {local_tz}")

    except FileNotFoundError as e:
        st.error(f"Error: {str(e)}")
        st.write("The Screen Time database file could not be found. Make sure you're running this on a Mac with Screen Time enabled.")
    except PermissionError as e:
        st.error(f"Error: {str(e)}")
        st.write("The script doesn't have permission to read the Screen Time database. Try running the script with sudo or adjust file permissions.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.write("Please check your database file and ensure Screen Time is properly set up on your Mac.")

if __name__ == "__main__":
    main()