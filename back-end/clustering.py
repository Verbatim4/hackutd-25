import pandas as pd
from sklearn.cluster import DBSCAN
import seaborn as sns
import matplotlib.pyplot as plt

def run_clustering(csv_path='dfw_complaints.csv', eps=0.0009, min_samples=20):
    """
    Runs DBSCAN clustering on complaint data based on latitude/longitude.
    
    Args:
        csv_path: Path to the CSV file with complaint data
        eps: DBSCAN epsilon parameter (max distance between points in a cluster)
        min_samples: DBSCAN min_samples parameter (min points to form a cluster)
    
    Returns:
        pd.DataFrame: DataFrame with cluster labels added
    """
    # Load latest feedback data
    data = pd.read_csv(csv_path)

    # Run DBSCAN
    X = data[['latitude', 'longitude']].values
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    data['cluster'] = db.labels_

    return data


def get_cluster_indices(csv_path='dfw_complaints.csv', eps=0.0009, min_samples=20):
    """
    Returns cluster indices and the clustered data.
    
    Args:
        csv_path: Path to the CSV file with complaint data
        eps: DBSCAN epsilon parameter
        min_samples: DBSCAN min_samples parameter
    
    Returns:
        tuple: (cluster_indices dict, clustered DataFrame)
    """
    data = run_clustering(csv_path, eps, min_samples)
    
    # Group indices by cluster
    cluster_indices = {}
    for idx, row in data.iterrows():
        cluster_id = row['cluster']
        if cluster_id not in cluster_indices:
            cluster_indices[cluster_id] = []
        cluster_indices[cluster_id].append(idx)
    
    return cluster_indices, data


def visualize_clusters(data):
    """
    Creates and saves a visualization of the clustered data.
    
    Args:
        data: DataFrame with cluster labels
    """
    # Count clusters and noise
    unique_clusters = set(data['cluster'])
    n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
    n_noise = list(data['cluster']).count(-1)

    print(f"\nDetected {n_clusters} clusters and {n_noise} noise points.")
    print(f"Cluster label range: {sorted(unique_clusters)}")

    # Separate noise and clusters
    noise = data[data['cluster'] == -1]
    clusters = data[data['cluster'] != -1]

    # Set Seaborn theme
    sns.set(style="whitegrid", context="talk")

    # Create scatter plot
    plt.figure(figsize=(10, 8))

    # Plot noise (transparent)
    if not noise.empty:
        sns.scatterplot(
            data=noise,
            x="longitude",
            y="latitude",
            color="gray",
            alpha=0.05,
            s=8,
            linewidth=0,
            label="Noise"
        )

    # Plot clusters
    if not clusters.empty:
        sns.scatterplot(
            data=clusters,
            x="longitude",
            y="latitude",
            hue="cluster",
            palette="tab10",
            s=10,
            linewidth=0,
            alpha=0.8,
            legend="full"
        )

    # Customize axes and layout
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'T-Mobile Hotspots — {n_clusters} Clusters Detected')
    plt.legend(title="Cluster", loc='best', fontsize='small')
    plt.tight_layout()

    # Save plot
    plt.savefig("hotspot_map.png", dpi=300)
    plt.close()
    print("Saved hotspot map to 'hotspot_map.png'")


if __name__ == '__main__':
    csv_path = 'dfw_complaints.csv'
    cluster_indices, data = get_cluster_indices(csv_path)
    
    print("\nData with cluster labels:")
    print(data.head())
    
    print("\nCluster Indices:")
    for cluster_id, indices in cluster_indices.items():
        print(f"Cluster {cluster_id}: {len(indices)} items")
    
    # Visualize the clusters
    visualize_clusters(data)
