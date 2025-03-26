import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    repo_data = pd.read_csv("data/coded_collated_data.csv")
    survey_data = pd.read_csv("data/coded_survey_anonymous.csv")
    team_classifications = pd.read_csv("team_classifications.csv")
    return repo_data, survey_data, team_classifications

repo_data, survey_data, team_classifications = load_data()

# Extract unique teams, semesters, and years
teams = team_classifications["Your Team"].unique()
semesters = repo_data["Semester"].unique()
years = repo_data["Year"].unique()

# Streamlit UI
st.title("Team Contribution Dashboard")
st.sidebar.header("Filters")

# User choice: Filter by team or semester/year
filter_option = st.sidebar.radio("Filter by:", ("Team", "Semester & Year"))

if filter_option == "Team":
    selected_team = st.sidebar.selectbox("Select a Team", teams)
    selected_year, selected_semester = None, None
else:
    selected_year = st.sidebar.selectbox("Select a Year", years)
    selected_semester = st.sidebar.selectbox("Select a Semester", semesters)
    selected_team = None

# Merge repo data with classifications
repo_data = repo_data.rename(columns={"Your Team": "Team"})
team_classifications = team_classifications.rename(columns={"Your Team": "Team"})
merged_data = repo_data.merge(team_classifications, on="Team", how="left")

# Filter data based on selected criteria
if selected_year and selected_semester:
    team_data = merged_data[(merged_data["Semester"] == selected_semester) & (merged_data["Year"] == selected_year)]
elif selected_team:
    team_data = merged_data[merged_data["Team"] == selected_team]
else:
    team_data = merged_data  # Default to all data

# Compute metrics
num_commits = (team_data[team_data["Action"] == "commit"].shape[0])
num_issues = (team_data[team_data["Action"] == "issue"].shape[0])
num_prs = (team_data[team_data["Action"] == "pull_request"].shape[0])
num_reviews = (team_data[team_data["Action"] == "code_review"].shape[0])

# Separate Views
if filter_option == "Semester & Year":
    st.subheader(f"Metrics for {selected_semester} {selected_year}")
    st.metric("Total Commits", num_commits)
    st.metric("Total Issues", num_issues)
    st.metric("Total Pull Requests", num_prs)
    st.metric("Total Code Reviews", num_reviews)

elif filter_option == "Team":
    st.subheader(f"Metrics for Team {selected_team}")
    st.metric("Total Commits", num_commits)
    st.metric("Total Issues", num_issues)
    st.metric("Total Pull Requests", num_prs)
    st.metric("Total Code Reviews", num_reviews)
    
    # Display team classification
    team_class = team_classifications[team_classifications["Team"] == selected_team]["classification"].values
    st.subheader("Team Classification")
    st.write(team_class[0] if len(team_class) > 0 else "Not Classified")
    
    # List team members
    st.subheader("Team Members")
    members = team_data["Author"].unique()
    selected_member = st.selectbox("Select a Member", members)
    
    # Display individual contributions
    st.subheader(f"Contributions of {selected_member}")
    member_data = team_data[team_data["Author"] == selected_member]
    st.dataframe(member_data)
