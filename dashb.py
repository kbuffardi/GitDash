import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
@st.cache_data
def load_data():
    repo_data = pd.read_csv("data/coded_collated_data.csv")
    survey_data = pd.read_csv("data/coded_survey_anonymous.csv")
    return repo_data, survey_data

repo_data, survey_data = load_data()

# Extract unique teams, semesters, years, and weeks
teams = repo_data["Your Team"].unique()
teams.sort()
semesters = repo_data["Semester"].unique()
years = repo_data["Year"].unique()
weeks = sorted(repo_data["week"].dropna().unique().astype(int))

# Streamlit UI
st.title("Team Contribution Dashboard")
st.sidebar.header("Filters")

# Filter by team
selected_team = st.sidebar.selectbox("Select a Team", teams)
team_data = repo_data[repo_data["Your Team"] == selected_team]

# Get unique semesters and years for the selected team
team_semesters = team_data["Semester"].unique()
team_years = team_data["Year"].unique()

# Filter by semester and year if multiple options exist
if len(team_semesters) > 1 or len(team_years) > 1:
    selected_semester = st.sidebar.selectbox("Select a Semester", team_semesters)
    selected_year = st.sidebar.selectbox("Select a Year", team_years)
    team_data = team_data[(team_data["Semester"] == selected_semester) & 
                          (team_data["Year"] == selected_year)]
else:
    selected_semester = team_semesters[0] if len(team_semesters) > 0 else None
    selected_year = team_years[0] if len(team_years) > 0 else None

# Filter by week
team_weeks = sorted(team_data["week"].dropna().unique().astype(int))
if len(team_weeks) > 0:
    selected_week = st.sidebar.selectbox("Select a Week", team_weeks)
    team_data_week = team_data[team_data["week"] == selected_week]
else:
    selected_week = None
    team_data_week = pd.DataFrame()

# Display team overview
st.header(f"Team {selected_team} - {selected_semester} {selected_year}")

# Compute overall team metrics
num_commits = team_data[team_data["Action"] == "commit"].shape[0]
num_issues = team_data[team_data["Action"] == "issue"].shape[0]
num_pr = team_data[team_data["Action"] == "pull_request"].shape[0]
num_pr_closed = team_data[(team_data["Action"] == "pull_request") & (team_data["Request_Status"] == "closed")].shape[0]
num_pr_open = team_data[(team_data["Action"] == "pull_request") & (team_data["Request_Status"] == "closed")].shape[0]
num_closed_issues = team_data[(team_data["Action"] == "issue") & (team_data["Request_Status"] == "closed")].shape[0]
num_open_issues = team_data[(team_data["Action"] == "issue") & (team_data["Request_Status"] == "open")].shape[0]

# Create columns for metrics
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    st.metric("Total Commits", num_commits)
with col2:
    st.metric("Total Issues", num_issues)
with col3:
    st.metric("Closed Issues", num_closed_issues)
with col4:
    st.metric("Open Issues", num_open_issues)
with col5:
    st.metric("Open Issues", num_open_issues)
with col6:
    st.metric("Closed Issues", num_closed_issues)
with col7:
    st.metric("Open Issues", num_open_issues)

# Get all team members from entire dataset for selected team/semester/year
all_team_members = set(team_data["Author"].unique())

# Show week specific data
if selected_week is not None and not team_data_week.empty:
    st.header(f"Week {selected_week} Contributions")
    
    # Get active team members from the selected week
    active_members = set(team_data_week["Author"].unique())
    
    # Display week metrics
    week_commits = team_data_week[team_data_week["Action"] == "commit"].shape[0]
    week_issues = team_data_week[team_data_week["Action"] == "issue"].shape[0]
    week_closed = team_data_week[(team_data_week["Action"] == "issue") & 
                                (team_data_week["Request_Status"] == "closed")].shape[0]
    
    # Create columns for week metrics
    wcol1, wcol2, wcol3 = st.columns(3)
    with wcol1:
        st.metric("Week Commits", week_commits)
    with wcol2:
        st.metric("Week Issues", week_issues)
    with wcol3:
        st.metric("Week Closed Issues", week_closed)
    
    # Show individual member contributions with color coding
    st.subheader("Team Member Contributions")
    
    # Create a DataFrame for all team members (active and inactive)
    member_contributions = []
    
    for member in all_team_members:
        # Check if the member was active in the selected week
        is_active = member in active_members
        
        # Get contributions for active members
        if is_active:
            member_data = team_data_week[team_data_week["Author"] == member]
            commits = member_data[member_data["Action"] == "commit"].shape[0]
            issues = member_data[member_data["Action"] == "issue"].shape[0]
        else:
            commits = 0
            issues = 0
        
        # Add status color indicator
        status = "🟢 Active" if is_active else "🔴 Inactive"
        
        member_contributions.append({
            "Team Member": member,
            "Status": status,
            "Commits": commits,
            "Issues": issues,
            "Total Actions": commits + issues,
            "Active": is_active  # Used for sorting
        })
    
    member_df = pd.DataFrame(member_contributions)
    
    # Sort by activity status and then by total actions
    member_df = member_df.sort_values(by=["Active", "Total Actions"], ascending=[False, False])
    
    if not member_df.empty:
        # Create a styled dataframe with colored rows based on activity
        st.markdown("### Team Member Status")
        
        # Create a colorful box display of active/inactive members
        cols = st.columns(4)
        for i, (_, row) in enumerate(member_df.iterrows()):
            col_idx = i % 4
            with cols[col_idx]:
                if row["Active"]:
                    st.success(f"**{row['Team Member']}**: {row['Total Actions']} actions")
                else:
                    st.error(f"**{row['Team Member']}**: No activity")
        
        # Show detailed table
        st.markdown("### Detailed Contribution Table")
        display_df = member_df[["Team Member", "Status", "Commits", "Issues", "Total Actions"]]
        st.dataframe(display_df.set_index("Team Member"))
        
        # Create visualizations for active members only
        active_df = member_df[member_df["Active"]]
        if not active_df.empty:
            st.subheader("Active Member Contributions")
            
            # Create bar chart for total actions
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot with green color for active members
            sns.barplot(x="Team Member", y="Total Actions", data=active_df, 
                        color="green", ax=ax)
            plt.xticks(rotation=45)
            plt.title("Contributions by Active Members")
            st.pyplot(fig)
            
            # Create breakdown of actions
            st.subheader("Breakdown by Action Type")
            action_data = []
            for _, row in active_df.iterrows():
                member = row["Team Member"]
                member_commits = row["Commits"]
                member_issues = row["Issues"]
                
                if member_commits > 0:
                    action_data.append({"Team Member": member, "Action": "Commits", "Count": member_commits})
                if member_issues > 0:
                    action_data.append({"Team Member": member, "Action": "Issues", "Count": member_issues})
            
            action_df = pd.DataFrame(action_data)
            if not action_df.empty:
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                sns.barplot(x="Team Member", y="Count", hue="Action", data=action_df, ax=ax2)
                plt.xticks(rotation=45)
                plt.title("Contribution Breakdown by Type")
                st.pyplot(fig2)
        
        # Create visualization of active vs inactive members
        activity_counts = member_df["Status"].value_counts()
        
        fig3, ax3 = plt.subplots(figsize=(8, 8))
        colors = ['#ff6b6b', '#51cf66']  # Red for inactive, Green for active
        plt.pie(activity_counts, labels=activity_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title('Team Member Activity Status')
        plt.axis('equal')
        st.pyplot(fig3)
    else:
        st.write("No member data found for this week.")
else:
    st.info("Please select a week to view team member contributions.")

# Show detailed activity in selected week
if selected_week is not None and not team_data_week.empty:
    st.header("Detailed Activity Log")
    
    # Select columns to display
    display_columns = ["Author", "Action", "Repo_ID", "Request_Status", "Close_date"]
    st.dataframe(team_data_week[display_columns])

# Add contribution trend over time
st.header("Team Member Activity Over Weeks")

# Check if there's enough data for the heatmap
if not team_data.empty and "week" in team_data.columns and len(all_team_members) > 0:
    # Create a heatmap of activity by member and week
    st.subheader("Activity Heatmap (Green = Active, Red = Inactive)")
    
    # Get all weeks for selected team/semester/year
    all_weeks = sorted(team_data["week"].dropna().unique().astype(int))
    
    # Create a matrix of activity (1 for active, 0 for inactive)
    activity_data = []
    
    for member in all_team_members:
        member_weeks = {}
        
        # Default all weeks to inactive
        for week in all_weeks:
            member_weeks[week] = 0
        
        # Mark weeks with activity
        member_activity = team_data[team_data["Author"] == member]
        active_weeks = member_activity["week"].dropna().unique().astype(int)
        
        for week in active_weeks:
            member_weeks[week] = 1
        
        # Add row to activity data
        row_data = {"Member": member}
        row_data.update({f"Week {week}": member_weeks[week] for week in all_weeks})
        activity_data.append(row_data)
    
    activity_df = pd.DataFrame(activity_data)
    
    # Create a pivot table for the heatmap
    if len(all_weeks) > 0:
        # Create the heatmap table
        st.markdown("### Weekly Activity by Team Member")
        heatmap_table = activity_df.set_index("Member")
        
        # Style the dataframe with color coding
        def color_activity(val):
            color = 'background-color: #51cf66' if val == 1 else 'background-color: #ff6b6b'
            return color
        
        styled_heatmap = heatmap_table.style.applymap(color_activity)
        st.dataframe(styled_heatmap)
        
        # Show actual heatmap visualization
        week_cols = [col for col in activity_df.columns if col.startswith("Week")]
        if len(week_cols) > 0:
            fig4, ax4 = plt.subplots(figsize=(12, len(all_team_members) * 0.8 + 2))
            heatmap_data = activity_df[week_cols].set_index(activity_df["Member"])
            sns.heatmap(heatmap_data, cmap=["#ff6b6b", "#51cf66"], cbar=False, 
                       linewidths=.5, yticklabels=True, ax=ax4)
            plt.title("Team Member Activity by Week (Green = Active, Red = Inactive)")
            plt.tight_layout()
            st.pyplot(fig4)
    else:
        st.write("Not enough weekly data to create activity heatmap.")
else:
    st.write("Insufficient data to create the weekly activity visualization.")