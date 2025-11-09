import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import datetime

# Step 1: Load latest feedback data
data = pd.read_csv('dfw_complaints_with_clusters.csv')

# Step 2: Run DBSCAN
X = data[['latitude', 'longitude']]
db = DBSCAN(eps=0.03, min_samples=2).fit(X)
data['cluster'] = db.labels_

# Step 3: Recalculate adjusted severity
alpha = 0.5
data['adjusted_severity'] = data['sentiment'].abs() * (1 + alpha * (data['cluster'] + 1))

# Step 4: Save updated data
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
output_file = f"outputs/hotspots_{timestamp}.csv"
data.to_csv(output_file, index=False)

# Step 5: Plot map
plt.figure(figsize=(8,6))
unique_clusters = set(data['cluster'])
colors = plt.cm.get_cmap('tab10', len(unique_clusters))

for cluster_id in unique_clusters:
    cluster_points = data[data['cluster'] == cluster_id]
    if cluster_id == -1:
        color = 'black'
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


# Run the job every hour
while True:
    analyze_complaints()
    print("⏳ Sleeping for 1 hour...\n")
    time.sleep(3600)
