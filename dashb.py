import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime


# Set page config for a cleaner look
st.set_page_config(layout="wide", page_title="Team Contribution Dashboard", page_icon="📊")

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    h1, h2, h3 {margin-top: 1rem; margin-bottom: 0.5rem;}
    .metric-card {background-color: #f9f9f9; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
    .status-active {background-color: #d4edda; color: #155724; border-radius: 0.3rem; padding: 0.5rem; box-shadow: 0 0 5px rgba(0,0,0,0.05);}
    .status-inactive {background-color: #f8d7da; color: #721c24; border-radius: 0.3rem; padding: 0.5rem; box-shadow: 0 0 5px rgba(0,0,0,0.05);}
    .classification-high {background-color: #d1e7dd; color: #0f5132; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center;}
    .classification-balanced {background-color: #fff3cd; color: #664d03; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center;}
    .classification-struggling {background-color: #f8d7da; color: #842029; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center;}
    .classification-icon {font-size: 2rem; margin-bottom: 0.5rem;}
    .classification-label {font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;}
    .classification-desc {font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    repo_data = pd.read_csv("data/coded_collated_data_t.csv")
    survey_data = pd.read_csv("data/coded_survey_anonymous.csv")
    classification_data = pd.read_csv("team_classifications.csv")
    return repo_data, survey_data, classification_data

repo_data, survey_data, classification_data = load_data()

# Extract unique teams, semesters, years, and weeks
teams = repo_data["Your Team"].unique()
teams.sort()
weeks = sorted(repo_data["week"].dropna().unique().astype(int))

# Sidebar with cleaner organization
with st.sidebar:
    st.image("https://via.placeholder.com/150x60?text=TeamTrack", width=150)
    st.title("Filters")
    
    # Filter by team
    selected_team = st.selectbox("Select a Team", teams)
    team_data = repo_data[repo_data["Your Team"] == selected_team]
    
    # Get team classification
    team_classification = classification_data[classification_data["Your Team"] == selected_team]["classification"].values[0] if len(classification_data[classification_data["Your Team"] == selected_team]) > 0 else "Unknown"
    
    # Get semester and year for display purposes only
    if not team_data.empty:
        # Just take the most recent semester and year for display
        selected_semester = team_data["Semester"].iloc[0]
        selected_year = team_data["Year"].iloc[0]
    else:
        selected_semester = "Unknown"
        selected_year = "Unknown"
    
    # Filter by week with improved UI
    team_weeks = sorted(team_data["week"].dropna().unique().astype(int))
    if len(team_weeks) > 0:
        week_options = ["All Weeks"] + [str(w) for w in team_weeks]
        selected_week = st.selectbox("Select a Week", week_options)
        
        if selected_week == "All Weeks":
            team_data_week = team_data
        else:
            team_data_week = team_data[team_data["week"] == int(selected_week)]
    else:
        selected_week = None
        team_data_week = pd.DataFrame()
        
    # Add a Member filter in sidebar
    all_team_members = set(team_data["Author"].unique())
    member_options = ["All Members"] + sorted(all_team_members)
    selected_member = st.selectbox("Select a Team Member", member_options)
    
    # Add view toggle for consolidated UI
    st.divider()
    st.subheader("View Options")
    show_activity_log = st.checkbox("Show Activity Log", value=False)
    show_member_details = st.checkbox("Show Member Details", value=True)
    show_trends = st.checkbox("Show Activity Trends", value=True)
    show_classification = st.checkbox("Show Classification Details", value=True)

# Display team overview with more modern design
st.title("Team Contribution Dashboard")
st.title(f"Team {selected_team} Dashboard")
st.subheader(f"{selected_semester} {selected_year}")

# Display the classification prominently at the top
if team_classification != "Unknown":
    classification_colors = {
        "High-performing": "classification-high",
        "Balanced": "classification-balanced",
        "Struggling": "classification-struggling"
    }
    
    classification_icons = {
        "High-performing": "🏆",
        "Balanced": "⚖️",
        "Struggling": "🔧"
    }
    
    classification_descriptions = {
        "High-performing": "Team demonstrates consistent contributions, balanced workload, and high quality interactions.",
        "Balanced": "Team shows steady progress with room for improvement in consistency or collaboration.",
        "Struggling": "Team needs attention in activity levels, member engagement, or coordination."
    }
    
    st.markdown(f"""
    <div class="{classification_colors.get(team_classification, 'metric-card')}">
        <div class="classification-icon">{classification_icons.get(team_classification, '📊')}</div>
        <div class="classification-label">Classification: {team_classification}</div>
        <div class="classification-desc">{classification_descriptions.get(team_classification, '')}</div>
    </div>
    """, unsafe_allow_html=True)


# Compute overall team metrics
num_commits = team_data[team_data["Action"] == "commit"].shape[0]
num_issues = team_data[team_data["Action"] == "issue"].shape[0]
num_prs = team_data[team_data["Action"] == "pull_request"].shape[0]
num_reviews = team_data[team_data["Action"] == "code_review"].shape[0]
num_comments = team_data[team_data["Action"] == "comment"].shape[0]

# Better metrics display with improved alignment
col1, col2, col3, col4, col5 = st.columns(5)

# Add custom CSS for better metric alignment
st.markdown("""
<style>
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 0.5rem;
        padding: 1.2rem 0.8rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📝</div>
        <div class="metric-value">{}</div>
        <div class="metric-label">Commits</div>
    </div>
    """.format(num_commits), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🔍</div>
        <div class="metric-value">{}</div>
        <div class="metric-label">Issues</div>
    </div>
    """.format(num_issues), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🔄</div>
        <div class="metric-value">{}</div>
        <div class="metric-label">Pull Requests</div>
    </div>
    """.format(num_prs), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-value">{}</div>
        <div class="metric-label">Code Reviews</div>
    </div>
    """.format(num_reviews), unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">💬</div>
        <div class="metric-value">{}</div>
        <div class="metric-label">Comments</div>
    </div>
    """.format(num_comments), unsafe_allow_html=True)

# Get all team members from entire dataset for selected team/semester/year
all_team_members = set(team_data["Author"].unique())

# Create tabs for better organization of content
tab1, tab2, tab3 = st.tabs(["Weekly Activity", "Team Analysis", "Member Insights"])

with tab1:
    # Show week specific data in a cleaner layout
    if selected_week is not None and not team_data_week.empty and selected_week != "All Weeks":
        st.header(f"Week {selected_week} Contributions")
        
        # Get active team members from the selected week
        active_members = set(team_data_week["Author"].unique())
        
        # Display week metrics in a more compact way
        week_metrics = {
            "Commits": team_data_week[team_data_week["Action"] == "commit"].shape[0],
            "Issues": team_data_week[team_data_week["Action"] == "issue"].shape[0],
            "PRs": team_data_week[team_data_week["Action"] == "pull_request"].shape[0],
            "Reviews": team_data_week[team_data_week["Action"] == "code_review"].shape[0],
            "Comments": team_data_week[team_data_week["Action"] == "comment"].shape[0]
        }
        
        # Use plotly for better interactive charts
        fig = go.Figure(data=[
            go.Bar(
                x=list(week_metrics.keys()),
                y=list(week_metrics.values()),
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            )
        ])
        fig.update_layout(
            title="Weekly Activity Breakdown",
            xaxis_title="Activity Type",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show a single visualization for team member status instead of redundant ones
        if show_member_details:
            st.subheader("Team Member Status & Contributions")
            
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
                    prs = member_data[member_data["Action"] == "pull_request"].shape[0]
                    reviews = member_data[member_data["Action"] == "code_review"].shape[0]
                    comments = member_data[member_data["Action"] == "comment"].shape[0]
                    last_action_row = member_data.sort_values("Timestamp", ascending=False).iloc[0]
                    last_action_date = last_action_row["Timestamp"]
                    if pd.notnull(last_action_date):
                        last_action_date = pd.to_datetime(last_action_date)
                        last_action_days_ago = (datetime.now() - last_action_date).days
                    else:
                        last_action_days_ago = "N/A"
                    
                else:
                    commits = issues = prs = reviews = comments = 0
                
                member_contributions.append({
                    "Team Member": member,
                    "Status": "Active" if is_active else "Inactive",
                    "Commits": commits,
                    "Issues": issues,
                    "Pull Requests": prs,
                    "Code Reviews": reviews,
                    "Comments": comments,
                    "Total Actions": commits + issues + prs + reviews + comments,
                    "Last Action Days Ago" : last_action_days_ago if is_active else "N/A",
                    "Active": is_active
                })
            
            member_df = pd.DataFrame(member_contributions)
            
            # Sort by activity status and then by total actions
            member_df = member_df.sort_values(by=["Active", "Total Actions"], ascending=[False, False])
            
            if not member_df.empty:
                # Create two columns for status cards and breakdown chart
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Activity counts for a clear single visualization
                    active_count = member_df[member_df["Active"]].shape[0]
                    inactive_count = member_df[~member_df["Active"]].shape[0]
                    
                    # Create a donut chart with plotly for better aesthetics
                    fig = go.Figure(data=[go.Pie(
                        labels=["Active", "Inactive"],
                        values=[active_count, inactive_count],
                        hole=.5,
                        marker_colors=['#2ecc71', '#e74c3c']
                    )])
                    fig.update_layout(
                        title_text="Member Activity Status",
                        showlegend=True,
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display member status in cards
                    st.markdown("### Team Members")
                    active_df = member_df[member_df["Active"]]
                    inactive_df = member_df[~member_df["Active"]]
                    
                    st.markdown("#### 🟢 Active")
                    for _, row in active_df.iterrows():
                        st.markdown(f'<div class="status-active">{row["Team Member"]}: {row["Total Actions"]} actions</div>',
                                   unsafe_allow_html=True)
                    
                    st.markdown("#### 🔴 Inactive")
                    for _, row in inactive_df.iterrows():
                        st.markdown(f'<div class="status-inactive">{row["Team Member"]}</div>',
                                  unsafe_allow_html=True)
                
                with col2:
                    # Create a unified visualization for active members
                    active_members_df = member_df[member_df["Active"]].copy()
                    if not active_members_df.empty:
                        # Create a stacked bar chart with plotly for action breakdown
                        active_members_df = active_members_df.sort_values("Total Actions", ascending=False)
                        
                        fig = go.Figure()
                        
                        # Add traces, one for each action type
                        fig.add_trace(go.Bar(
                            y=active_members_df["Team Member"],
                            x=active_members_df["Commits"],
                            name="Commits",
                            orientation='h',
                            marker=dict(color='rgba(31, 119, 180, 0.8)')
                        ))
                        fig.add_trace(go.Bar(
                            y=active_members_df["Team Member"],
                            x=active_members_df["Issues"],
                            name="Issues",
                            orientation='h',
                            marker=dict(color='rgba(255, 127, 14, 0.8)')
                        ))
                        fig.add_trace(go.Bar(
                            y=active_members_df["Team Member"],
                            x=active_members_df["Pull Requests"],
                            name="Pull Requests",
                            orientation='h',
                            marker=dict(color='rgba(44, 160, 44, 0.8)')
                        ))
                        fig.add_trace(go.Bar(
                            y=active_members_df["Team Member"],
                            x=active_members_df["Code Reviews"],
                            name="Code Reviews",
                            orientation='h',
                            marker=dict(color='rgba(214, 39, 40, 0.8)')
                        ))
                        fig.add_trace(go.Bar(
                            y=active_members_df["Team Member"],
                            x=active_members_df["Comments"],
                            name="Comments",
                            orientation='h',
                            marker=dict(color='rgba(148, 103, 189, 0.8)')
                        ))
                        
                        fig.update_layout(
                            barmode='stack',
                            title="Activity Breakdown by Member",
                            height=400,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Show detailed table with expandable rows for better space usage
                with st.expander("View Detailed Contribution Table"):
                    display_df = member_df[["Team Member", "Status", "Commits", "Issues", "Pull Requests", "Code Reviews", "Comments", "Total Actions","Last Action Days Ago"]]
                    st.dataframe(display_df.set_index("Team Member"))

with tab2:
    if show_trends:
        st.header("Team Activity Analysis")
        
        # Activity trends over time - more interactive and visually appealing
        if not team_data.empty and "week" in team_data.columns:
            # Group data by week and action type
            weekly_activity = team_data.groupby(["week", "Action"]).size().reset_index(name="Count")
            
            if not weekly_activity.empty:
                # Use Plotly for interactive line chart
                fig = px.line(
                    weekly_activity, 
                    x="week", 
                    y="Count", 
                    color="Action",
                    markers=True,
                    title="Weekly Activity Trends",
                    labels={"week": "Week", "Count": "Number of Actions", "Action": "Activity Type"}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        # Team member activity heatmap - simplified and more effective
        if not team_data.empty and "week" in team_data.columns and len(all_team_members) > 0:
            st.subheader("Team Activity Patterns")
            
            # Combine the two heatmaps into one meaningful visualization
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create a heatmap of activity by member and week
                all_weeks = sorted(team_data["week"].dropna().unique().astype(int))
                activity_data = []
                
                for member in all_team_members:
                    member_weeks = {}
                    
                    # Default all weeks to inactive
                    for week in all_weeks:
                        member_weeks[week] = 0
                    
                    # Count actual activities per week
                    member_activity = team_data[team_data["Author"] == member]
                    week_counts = member_activity.groupby("week").size()
                    
                    for week, count in week_counts.items():
                        member_weeks[week] = count
                    
                    # Add row to activity data
                    row_data = {"Member": member}
                    row_data.update({f"Week {week}": member_weeks[week] for week in all_weeks})
                    activity_data.append(row_data)
                
                activity_df = pd.DataFrame(activity_data)
                
                if len(all_weeks) > 0 and not activity_df.empty:
                    # Create activity heatmap with intensity instead of binary
                    week_cols = [col for col in activity_df.columns if col.startswith("Week")]
                    heatmap_data = activity_df[week_cols].set_index(activity_df["Member"])
                    
                    # Create a custom colormap from red to green
                    colors = [(0.8, 0.2, 0.2), (1.0, 1.0, 0.6), (0.2, 0.8, 0.2)]
                    cmap = LinearSegmentedColormap.from_list("activity_cmap", colors, N=100)
                    
                    fig, ax = plt.subplots(figsize=(12, len(all_team_members) * 0.8 + 2))
                    sns.heatmap(heatmap_data, cmap=cmap, annot=True, fmt="d",
                              linewidths=.5, yticklabels=True, ax=ax)
                    plt.title("Team Activity Intensity by Week")
                    plt.tight_layout()
                    st.pyplot(fig)
            
            with col2:
                # Create a summary of activity types by week
                if len(all_weeks) > 0:
                    # Prepare data for activity type summary - use a donut chart for better visualization
                    action_counts = team_data["Action"].value_counts()
                    
                    # Create a donut chart
                    fig = go.Figure(data=[go.Pie(
                        labels=action_counts.index,
                        values=action_counts.values,
                        hole=.4,
                        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    )])
                    fig.update_layout(
                        title_text="Overall Activity Distribution",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Member-specific drilldown - more consolidated and visually appealing
    if selected_member != "All Members":
        # Filter data for the selected member
        member_data = team_data[team_data["Author"] == selected_member]
        
        if not member_data.empty:
            st.header(f"{selected_member}'s Contributions")
            
            # Display member's overall contributions with visually appealing cards
            member_metrics = {
                "📝 Commits": member_data[member_data["Action"] == "commit"].shape[0],
                "🔍 Issues": member_data[member_data["Action"] == "issue"].shape[0],
                "🔄 PRs": member_data[member_data["Action"] == "pull_request"].shape[0],
                "✅ Reviews": member_data[member_data["Action"] == "code_review"].shape[0],
                "💬 Comments": member_data[member_data["Action"] == "comment"].shape[0]
            }
            
            cols = st.columns(5)
            metrics = [
                ("📝 Commits", member_metrics["📝 Commits"]),
                ("🔍 Issues", member_metrics["🔍 Issues"]), 
                ("🔄 PRs", member_metrics["🔄 PRs"]),
                ("✅ Reviews", member_metrics["✅ Reviews"]),
                ("💬 Comments", member_metrics["💬 Comments"])
            ]

            for i, (label, value) in enumerate(metrics):
                with cols[i]:
                    icon, text = label.split(" ", 1)
                    st.markdown(f"""
                        <div class='metric-card'>
                        <div class='metric-icon'>{icon}</div>
                        <div class='metric-value'>{value}</div>
                        <div class='metric-label'>{text}</div>
                        </div>
                    """, unsafe_allow_html=True)
            # Create two columns for charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Display a timeline of contributions - interactive chart
                st.subheader("Contribution Timeline")
                timeline_data = member_data.groupby("week")["Action"].value_counts().unstack(fill_value=0)
                
                if not timeline_data.empty:
                    # Convert to long format for plotly
                    timeline_long = timeline_data.reset_index().melt(
                        id_vars="week", 
                        value_vars=timeline_data.columns,
                        var_name="Action",
                        value_name="Count"
                    )
                    
                    # Create interactive area chart
                    fig = px.area(
                        timeline_long, 
                        x="week", 
                        y="Count", 
                        color="Action",
                        title=f"Activity Timeline for {selected_member}",
                        labels={"week": "Week", "Count": "Number of Actions"}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Visualize the breakdown of actions - more visually appealing
                st.subheader("Action Breakdown")
                action_counts = member_data["Action"].value_counts()
                
                colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 
                         'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)', 
                         'rgba(148, 103, 189, 0.8)']
                
                fig = go.Figure(data=[go.Bar(
                    x=action_counts.index,
                    y=action_counts.values,
                    marker_color=colors[:len(action_counts)]
                )])
                
                fig.update_layout(
                    title=f"Activity Distribution for {selected_member}",
                    xaxis_title="Action Type",
                    yaxis_title="Count",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed activity log if requested
            if show_activity_log:
                with st.expander("View Activity Log"):
                    st.dataframe(
                        member_data[["week", "Action", "Request_Status", "Timestamp","Message"]].sort_values("week"),
                        hide_index=True
                    )
    else:
        # Display aggregated view for all members
        st.header("All Team Members Comparison")
        
        # Create a DataFrame for comparative analysis
        member_summary = []
        for member in all_team_members:
            member_data = team_data[team_data["Author"] == member]
            
            member_summary.append({
                "Team Member": member,
                "Commits": member_data[member_data["Action"] == "commit"].shape[0],
                "Issues": member_data[member_data["Action"] == "issue"].shape[0],
                "Pull Requests": member_data[member_data["Action"] == "pull_request"].shape[0],
                "Code Reviews": member_data[member_data["Action"] == "code_review"].shape[0],
                "Comments": member_data[member_data["Action"] == "comment"].shape[0],
                "Total Actions": member_data.shape[0],
                "Active Weeks": member_data["week"].nunique()
            })
        
        member_summary_df = pd.DataFrame(member_summary).sort_values("Total Actions", ascending=False)
        
        # Create an interactive visualization comparing all members
        fig = px.bar(
            member_summary_df, 
            x="Team Member", 
            y=["Commits", "Issues", "Pull Requests", "Code Reviews", "Comments"],
            title="Contribution Comparison Across Team",
            labels={"value": "Number of Actions", "variable": "Action Type"},
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show the data table with expandable view
        with st.expander("View Detailed Member Comparison"):
            st.dataframe(member_summary_df.set_index("Team Member"))
        
        # Show consistency analysis - who contributes most consistently
        st.subheader("Contribution Consistency Analysis")
        
        # Calculate consistency metrics
        if "week" in team_data.columns:
            total_weeks = team_data["week"].nunique()
            
            for i in range(len(member_summary)):
                if total_weeks > 0:
                    member_summary[i]["Consistency %"] = round((member_summary[i]["Active Weeks"] / total_weeks) * 100, 1)
                else:
                    member_summary[i]["Consistency %"] = 0
            
            consistency_df = pd.DataFrame(member_summary)[["Team Member", "Active Weeks", "Consistency %", "Total Actions"]]
            consistency_df = consistency_df.sort_values("Consistency %", ascending=False)
            
            # Create a scatterplot showing consistency vs total contributions
            fig = px.scatter(
                consistency_df,
                x="Consistency %",
                y="Total Actions",
                size="Total Actions",
                color="Consistency %",
                hover_name="Team Member",
                text="Team Member",
                title="Contribution Volume vs Consistency",
                labels={"Consistency %": "% of Weeks with Activity", "Total Actions": "Total Contributions"},
                height=500,
                color_continuous_scale="viridis"
            )
            
            fig.update_traces(textposition='top center')
            fig.update_layout(xaxis_range=[0, 105])
            st.plotly_chart(fig, use_container_width=True)

# Footer with information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Team Contribution Dashboard v2.0 | Updated: March 2025
</div>
""", unsafe_allow_html=True)