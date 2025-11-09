# Clustering Setup Instructions

## Step 1: Install Dependencies

Make sure you're in the virtual environment and have all dependencies installed:

```bash
pip install -r ../requirements.txt
```

## Step 2: Generate Clustered Data

Run the clustering script to add cluster numbers to the main CSV file:

```bash
python add_clusters_to_csv.py
```

This will:
- Load `dfw_complaints.csv`
- Run DBSCAN clustering
- Create `dfw_complaints_with_clusters.csv` with cluster numbers added
- Display cluster distribution

## Step 3: Start the Server

Once the clustered data file is created, start the Flask server:

```bash
python server.py
```

## API Endpoints for Clusters

### Get All Clusters
```
GET http://localhost:5000/api/clusters
```
Returns list of all clusters with counts and centers.

### Get Specific Cluster Data
```
GET http://localhost:5000/api/clusters/{cluster_id}
```
Returns all data points (complaints) in the specified cluster.

Example:
```bash
curl http://localhost:5000/api/clusters/0
```

### Get Cluster Analysis
```
GET http://localhost:5000/api/clusters/analysis
```
Returns AI-generated analysis for all clusters from the CSV.

## Files Generated

- `dfw_complaints_with_clusters.csv` - Main data file with cluster numbers
- `cluster_analysis_YYYYMMDD_HHMMSS.txt` - Full text analysis report
- `cluster_analysis_YYYYMMDD_HHMMSS.csv` - Structured analysis data
- `hotspot_map.png` - Visualization of clusters

## Example Usage

```python
import requests

# Get all clusters
response = requests.get('http://localhost:5000/api/clusters')
clusters = response.json()

# Get data points in cluster 0
response = requests.get('http://localhost:5000/api/clusters/0')
cluster_0_data = response.json()

# Get AI analysis
response = requests.get('http://localhost:5000/api/clusters/analysis')
analysis = response.json()
```

