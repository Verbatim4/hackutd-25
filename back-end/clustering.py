import pandas as pd
import matplotlib as plt

# Load CSV file
data = pd.read_csv('dfw_complaints.csv')

# Check the first rows
print(data.head())


from sklearn.cluster import DBSCAN

# Use latitude and longitude for clustering
coords = data[['latitude', 'longitude']].values

# DBSCAN parameters
db = DBSCAN(eps=0.03, min_samples=2).fit(coords)

# Add cluster labels to your dataframe
data['cluster'] = db.labels_
print("\nData with cluster labels:")
print(data.head())

# Step 6: Adjust severity for clustered complaints
# Noise points (cluster = -1) remain unadjusted
alpha = 0.5
data['adjusted_severity'] = data['sentiment'].abs() * (1 + alpha * (data['cluster'] + 1))
print("\nData with adjusted severity:")
print(data.head())

# Step 7: Save results to new CSV
data.to_csv('dfw_complaints_with_clusters.csv', index=False)
print("\nSaved results to 'dfw_complaints_with_clusters.csv'")

# Step 8: Visualize clusters
unique_clusters = set(data['cluster'])
colors = plt.cm.get_cmap('tab10', len(unique_clusters))

plt.figure(figsize=(8,6))

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
plt.title('DBSCAN Hotspots of Negative Sentiment in DFW')
plt.legend()
plt.show()
