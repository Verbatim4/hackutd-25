"""
Add cluster numbers to the main complaints CSV file
"""
import pandas as pd
from clustering import get_cluster_indices

def add_clusters_to_main_csv(input_csv='dfw_complaints.csv', output_csv='dfw_complaints_with_clusters.csv'):
    """
    Run clustering and add cluster numbers to the main CSV file
    """
    print(f"Loading and clustering data from {input_csv}...")
    
    # Run clustering
    cluster_indices, cluster_data = get_cluster_indices(input_csv, eps=0.0009, min_samples=20)
    
    print(f"✓ Clustering complete!")
    print(f"  Total complaints: {len(cluster_data)}")
    print(f"  Clusters found: {len(cluster_data['cluster'].unique())}")
    
    # Save the data with cluster numbers
    cluster_data.to_csv(output_csv, index=False)
    
    print(f"✓ Saved to: {output_csv}")
    
    # Show cluster distribution
    print("\nCluster distribution:")
    cluster_counts = cluster_data['cluster'].value_counts().sort_index()
    for cluster_id, count in cluster_counts.items():
        if cluster_id == -1:
            print(f"  Cluster {cluster_id} (noise): {count} complaints")
        else:
            print(f"  Cluster {cluster_id}: {count} complaints")
    
    return cluster_data


if __name__ == '__main__':
    # Add clusters to the main CSV
    cluster_data = add_clusters_to_main_csv()
    print("\n✓ Complete! The file 'dfw_complaints_with_clusters.csv' now contains cluster numbers.")

