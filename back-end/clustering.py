import pandas as pd
from sklearn.cluster import DBSCAN
import seaborn as sns
import matplotlib.pyplot as plt

def run_clustering():
    # Load latest feedback data
    data = pd.read_csv('dfw_complaints.csv')  # master CSV with all complaints

    # Run DBSCAN
    X = data[['latitude', 'longitude']].values
    db = DBSCAN(eps=0.0009, min_samples=20).fit(X)
    data['cluster'] = db.labels_

    print("\nData with cluster labels:")
    print(data.head())

    # Count clusters and noise
    unique_clusters = set(db.labels_)
    n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
    n_noise = list(db.labels_).count(-1)

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

run_clustering()
