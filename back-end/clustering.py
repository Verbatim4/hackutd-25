import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import datetime
import time

def run_clustering():
    # Load latest feedback data
    data = pd.read_csv('dfw_complaints.csv')  # use master CSV with all complaints

    # Run DBSCAN
    X = data[['latitude', 'longitude']].values
    db = DBSCAN(eps=0.03, min_samples=2).fit(X)
    data['cluster'] = db.labels_

    print("\nData with cluster labels:")
    print(data.head())

    # Adjust severity for clustered complaints
    alpha = 0.5
    data['adjusted_severity'] = data['sentiment'].abs() * (1 + alpha * (data['cluster'] + 1))
    print("\nData with adjusted severity:")
    print(data.head())

    # Save updated CSV
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = f"outputs/hotspots_{timestamp}.csv"
    data.to_csv(output_file, index=False)
    print(f"\nSaved results to '{output_file}'")

    # Visualize clusters
    plt.figure(figsize=(8,6))
    unique_clusters = set(data['cluster'])
    colors = plt.cm.get_cmap('tab10', len(unique_clusters))

    for cluster_id in unique_clusters:
        cluster_points = data[data['cluster'] == cluster_id]
        if cluster_id == -1:
            color = 'black'  # noise points
            label = 'Noise'
        else:
            color = colors(cluster_id)
            label = f'Cluster {cluster_id}'
        plt.scatter(cluster_points['longitude'], cluster_points['latitude'], c=[color], s=100, label=label)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'T-Mobile Hotspots (Updated: {timestamp})')
    plt.legend()
    plt.savefig(f"maps/hotspot_map_{timestamp}.png")
    plt.close()
    print(f"Saved hotspot map to 'maps/hotspot_map_{timestamp}.png'")

# Run the clustering every hour
while True:
    run_clustering()
    print(" Sleeping for 1 hour...\n")
    time.sleep(3600)
