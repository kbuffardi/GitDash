import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def prepare_survey_data(df):
    """
    Prepare survey data by aggregating responses by team and computing mean scores
    for different dimensions of team dynamics.
    """
    # Group questions by categories
    conflict_questions = [
        'How frequently do you have disagreements within your work group about the task of the project you are working on?',
        'How often do people in your work group have conflicting opinions about the project you are working on?',
        'How much emotional conflict is there in your work group?',
        'How often do people get angry while working in your group?',
        'How much conflict of ideas is there in your work group?',
        'How often do you disagree about resource allocation in your work group?',
        'How much relationship tension is there in your work group?',
        'How often are there disagreements about who should do what in your work group?',
        'How much conflict is there in your group about task responsibilities?'
    ]
    
    collaboration_questions = [
        'Team members get to participate in enjoyable activities',
        'Team members enjoy spending time together',
        'Team members get along well',
        'Team members like each other',
        'Team members like the work that the group does',
        'Being part of the team allows team members to do enjoyable work'
    ]
    
    commitment_questions = [
        "I'm unhappy with my team's level of commitment to the task",
        'Our team is united in trying to reach its goals for performance',
        'Our team members have conflicting aspirations for the team\'s performance'
    ]
    
    # Calculate mean scores for each dimension by team
    team_metrics = df.groupby('Your Team').agg({
        **{q: 'mean' for q in conflict_questions},
        **{q: 'mean' for q in collaboration_questions},
        **{q: 'mean' for q in commitment_questions}
    })
    
    # Calculate aggregate scores
    team_metrics['conflict_score'] = team_metrics[conflict_questions].mean(axis=1)
    team_metrics['collaboration_score'] = team_metrics[collaboration_questions].mean(axis=1)
    team_metrics['commitment_score'] = team_metrics[commitment_questions].mean(axis=1)
    
    # Invert negative questions so higher always means better
    team_metrics['commitment_score'] = 6 - team_metrics['commitment_score']  # Assuming 5-point scale
    
    return team_metrics[['conflict_score', 'collaboration_score', 'commitment_score']]

def compute_cluster_summary_stats(team_metrics):
    """
    Compute mean, standard deviation, and Gini index for each classification 
    across conflict, collaboration, and commitment scores.
    """
    def gini(array):
        array = np.sort(array)
        n = array.size
        cumulative = np.cumsum(array)
        gini_index = (2 * np.sum((np.arange(1, n + 1) * array))) / (n * cumulative[-1]) - (n + 1) / n
        return gini_index

    dimensions = ['conflict_score', 'collaboration_score', 'commitment_score']
    classifications = team_metrics['classification'].unique()
    stats = {}

    for classification in classifications:
        cluster_data = team_metrics[team_metrics['classification'] == classification]
        stats[classification] = {}
        for dim in dimensions:
            scores = cluster_data[dim].values
            stats[classification][f'{dim}_mean'] = np.mean(scores)
            stats[classification][f'{dim}_std'] = np.std(scores)
            stats[classification][f'{dim}_gini'] = gini(scores)

    cluster_stats_df = pd.DataFrame.from_dict(stats, orient='index')
    return cluster_stats_df


def classify_teams(survey_data_path):
    """
    Classify teams into categories based on survey responses using clustering.
    """
    df = pd.read_csv(survey_data_path)
    team_metrics = prepare_survey_data(df)

    # Standardize features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(team_metrics)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)
    team_metrics['cluster'] = clusters  # Add cluster assignments

    # Calculate GLOBAL means for comparison
    global_conflict_mean = team_metrics['conflict_score'].mean()
    global_collab_mean = team_metrics['collaboration_score'].mean()
    global_commit_mean = team_metrics['commitment_score'].mean()

    # Characterize clusters
    cluster_means = team_metrics.groupby('cluster').mean()
    cluster_labels = {}

    for cluster in cluster_means.index:
        conflict = cluster_means.loc[cluster, 'conflict_score']
        collab = cluster_means.loc[cluster, 'collaboration_score']
        commit = cluster_means.loc[cluster, 'commitment_score']

        # Classification logic
        if (collab > global_collab_mean) and (commit > global_commit_mean) and (conflict < global_conflict_mean):
            label = 'High-performing'
        elif (conflict > global_conflict_mean) and (collab < global_collab_mean) and (commit < global_commit_mean):
            label = 'Struggling'
        else:
            label = 'Balanced'
        
        cluster_labels[cluster] = label


    team_metrics['classification'] = team_metrics['cluster'].map(cluster_labels)
    
    return team_metrics

def visualize_classifications(team_metrics):


    features = team_metrics[['conflict_score', 'collaboration_score', 'commitment_score']]

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(StandardScaler().fit_transform(features))

    viz_data = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'])
    viz_data.index = team_metrics.index
    viz_data['classification'] = team_metrics['classification']
    viz_data['team'] = team_metrics.index
    
    return viz_data

def plot_team_classifications(viz_data):

    colors = {
        'High-performing': 'green',
        'Struggling': 'red',
        'Balanced': 'blue'
    }

    plt.figure(figsize=(10, 8))

    for classification in colors:
        mask = viz_data['classification'] == classification
        plt.scatter(
            viz_data[mask]['PC1'], 
            viz_data[mask]['PC2'],
            c=colors[classification],
            label=classification,
            alpha=0.6
        )

    for idx, row in viz_data.iterrows():
        plt.annotate(
            row['team'],
            (row['PC1'], row['PC2']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8
        )
    
    plt.xlabel('First Principal Component')
    plt.ylabel('Second Principal Component')
    plt.title('Team Classifications based on Survey Responses')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig('team_classifications.png')
    plt.close()

if __name__ == "__main__":

    survey_data_path = "data/coded_survey_anonymous.csv"
    team_classifications = classify_teams(survey_data_path)

    print("\nTeam Classifications:")
    print(team_classifications[['classification']])
    team_classifications[['classification']].to_csv('team_classifications.csv')
    viz_data = visualize_classifications(team_classifications)
    plot_team_classifications(viz_data)
    
    print("\nVisualization Data:")
    print(viz_data)
    print("\nVisualization has been saved as 'team_classifications.png'")
    cluster_summary = compute_cluster_summary_stats(team_classifications)
    print("\nCluster Summary Statistics:")
    print(cluster_summary)
    cluster_summary.to_csv('cluster_summary_statistics.csv') 

