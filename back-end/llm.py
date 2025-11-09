import google.generativeai as genai
import pandas as pd
import os
import time
from typing import Dict, List, Any
from datetime import datetime

# Configure Google Gemini API
# Set API key manually
os.environ["GOOGLE_API_KEY"] = ""
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def summarize_cluster(cluster_data: pd.DataFrame, cluster_id: int, model_name: str = "gemini-2.5-pro") -> str:
    """
    Summarizes a single cluster using Google Gemini.
    
    Args:
        cluster_data: DataFrame containing all data with cluster assignments
        cluster_id: The specific cluster ID to summarize
        model_name: Gemini model to use (default: gemini-2.5-pro)
    
    Returns:
        str: Summary of the cluster
    """
    # Filter data for this cluster
    cluster_subset = cluster_data[cluster_data['cluster'] == cluster_id]
    
    if cluster_subset.empty:
        return f"Cluster {cluster_id} has no data points."
    
    # Prepare cluster information
    cluster_size = len(cluster_subset)
    
    # Get location statistics
    lat_mean = cluster_subset['latitude'].mean()
    lon_mean = cluster_subset['longitude'].mean()
    
    # Extract descriptions from this cluster
    descriptions = cluster_subset['description'].tolist()
    
    # Sample descriptions for analysis (use more if cluster is small)
    sample_size = min(20, len(descriptions))
    sample_descriptions = descriptions[:sample_size]
    
    # Create a concise representation of the cluster data
    cluster_info = []
    cluster_info.append(f"Cluster ID: {cluster_id}")
    cluster_info.append(f"Number of complaints: {cluster_size}")
    cluster_info.append(f"Location: Latitude {lat_mean:.6f}, Longitude {lon_mean:.6f}")
    
    # Build prompt for Gemini focusing on descriptions
    descriptions_text = "\n".join([f"- {desc}" for desc in sample_descriptions])
    
    prompt = f"""
You are an AI assistant analyzing geographic clusters of customer complaints. 

CLUSTER INFORMATION:
- Cluster ID: {cluster_id}
- Total Complaints: {cluster_size}
- Geographic Center: Lat {lat_mean:.6f}, Lon {lon_mean:.6f}

SAMPLE COMPLAINTS FROM THIS CLUSTER:
{descriptions_text}

TASK:
Analyze these complaints and provide:
1. **Main Issue**: What is the primary problem or theme in this cluster? (1-2 sentences)
2. **Common Patterns**: What recurring issues or concerns appear across multiple complaints?
3. **Severity Assessment**: Rate the severity (Low/Medium/High) based on the nature and frequency of issues
4. **Root Cause**: What underlying problem might be causing these complaints?
5. **Recommended Action**: What specific action should be prioritized to address this cluster?

Keep your analysis focused, actionable, and concise (4-6 sentences total).
"""
    
    # Initialize the model
    model = genai.GenerativeModel(model_name)
    
    # Generate summary
    response = model.generate_content(prompt)
    
    return response.text


def summarize_all_clusters(cluster_data: pd.DataFrame, model_name: str = "gemini-2.5-pro", delay_seconds: float = 5.0) -> Dict[int, str]:
    """
    Summarizes all clusters in the dataset using Google Gemini with rate limiting.
    
    Args:
        cluster_data: DataFrame containing all data with cluster assignments
        model_name: Gemini model to use (default: gemini-2.5-pro)
        delay_seconds: Delay between API calls to avoid rate limiting (default: 5.0 seconds)
    
    Returns:
        dict: {cluster_id: summary_text, ...}
    """
    unique_clusters = sorted(cluster_data['cluster'].unique())
    summaries = {}
    
    print(f"Analyzing {len(unique_clusters)} clusters with {delay_seconds}s delay between API calls...")
    
    for idx, cluster_id in enumerate(unique_clusters, 1):
        if cluster_id == -1:
            # DBSCAN noise points
            summaries[cluster_id] = "Noise cluster: These are outlier data points that don't fit into any cluster."
            print(f"[{idx}/{len(unique_clusters)}] Cluster {cluster_id}: Skipped (noise)")
        else:
            print(f"[{idx}/{len(unique_clusters)}] Analyzing Cluster {cluster_id}...", end=" ")
            try:
                summaries[cluster_id] = summarize_cluster(cluster_data, cluster_id, model_name)
                print("✓ Done")
                
                # Rate limiting: wait before next API call (except for last cluster)
                if idx < len(unique_clusters):
                    time.sleep(delay_seconds)
            except Exception as e:
                print(f"✗ Error: {e}")
                summaries[cluster_id] = f"Error analyzing cluster: {str(e)}"
                # Wait longer if there's an error (might be rate limit)
                time.sleep(delay_seconds * 2)
    
    return summaries


def generate_overall_analysis(cluster_data: pd.DataFrame, 
                             cluster_summaries: Dict[int, str], 
                             model_name: str = "gemini-2.5-pro") -> str:
    """
    Generates an overall analysis across all clusters using Google Gemini.
    
    Args:
        cluster_data: DataFrame containing all data with cluster assignments
        cluster_summaries: Dictionary of cluster summaries from summarize_all_clusters
        model_name: Gemini model to use (default: gemini-2.5-pro)
    
    Returns:
        str: Overall analysis and insights
    """
    # Prepare overview statistics
    total_items = len(cluster_data)
    num_clusters = len(cluster_data['cluster'].unique())
    noise_count = len(cluster_data[cluster_data['cluster'] == -1])
    
    # Build comprehensive prompt
    prompt = f"""
You are an AI assistant analyzing geographic complaint clusters for a telecommunications company.

OVERVIEW:
- Total Complaints: {total_items:,}
- Number of Geographic Clusters: {num_clusters}
- Outlier Complaints: {noise_count}

INDIVIDUAL CLUSTER ANALYSES:
"""
    
    for cluster_id, summary in sorted(cluster_summaries.items()):
        if cluster_id != -1:  # Skip noise cluster in detailed summary
            cluster_size = len(cluster_data[cluster_data['cluster'] == cluster_id])
            prompt += f"\n--- Cluster {cluster_id} ({cluster_size} complaints) ---\n{summary}\n"
    
    prompt += """

STRATEGIC ANALYSIS REQUESTED:
1. **Priority Ranking**: Which 3 clusters require immediate attention and why?
2. **Common Themes**: What patterns appear across multiple geographic clusters?
3. **Root Causes**: What are the likely underlying infrastructure or service issues?
4. **Resource Allocation**: Where should technical teams be deployed first?
5. **Long-term Strategy**: What systemic improvements would prevent these issues?

Provide a strategic, executive-level analysis (6-8 sentences).
"""
    
    print("\nGenerating overall strategic analysis...")
    
    # Initialize the model
    model = genai.GenerativeModel(model_name)
    
    # Add rate limiting before overall analysis
    time.sleep(5.0)
    
    # Generate overall analysis
    response = model.generate_content(prompt)
    
    return response.text


if __name__ == '__main__':
    # Example usage
    from clustering import get_cluster_indices
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"cluster_analysis_{timestamp}.txt"
    
    def log(message, file_handle=None):
        """Print to console and write to file"""
        print(message)
        if file_handle:
            file_handle.write(message + "\n")
            file_handle.flush()
    
    # Open output file
    with open(output_file, 'w', encoding='utf-8') as f:
        log(f"Cluster Analysis Report - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f)
        log("="*80, f)
        log("", f)
        
        log("Loading and clustering data...", f)
        csv_path = "dfw_complaints.csv"
        cluster_indices, cluster_data = get_cluster_indices(csv_path, eps=0.0009, min_samples=20)
        
        log("", f)
        log("="*80, f)
        log("CLUSTER SUMMARIES - ANALYZING COMPLAINT DESCRIPTIONS", f)
        log("="*80, f)
        log("", f)
        
        # Summarize all clusters with rate limiting
        # Using 5 seconds delay to ensure no rate limiting (12 requests/minute max)
        # Free tier allows 15 requests/minute, so 5s = safe buffer
        log(f"Analyzing clusters with 5 second delays to prevent rate limiting...", f)
        log("", f)
        
        summaries = summarize_all_clusters(cluster_data, delay_seconds=5.0)
        
        log("", f)
        log("="*80, f)
        log("INDIVIDUAL CLUSTER RESULTS", f)
        log("="*80, f)
        
        for cluster_id, summary in sorted(summaries.items()):
            if cluster_id != -1:  # Skip noise cluster
                cluster_size = len(cluster_data[cluster_data['cluster'] == cluster_id])
                log("", f)
                log("="*80, f)
                log(f"CLUSTER {cluster_id} - {cluster_size} complaints", f)
                log("="*80, f)
                log(summary, f)
        
        log("", f)
        log("="*80, f)
        log("STRATEGIC OVERALL ANALYSIS", f)
        log("="*80, f)
        log("", f)
        
        # Generate overall analysis
        overall = generate_overall_analysis(cluster_data, summaries)
        log(overall, f)
        
        log("", f)
        log("="*80, f)
        log("ANALYSIS COMPLETE", f)
        log("="*80, f)
        log("", f)
        log(f"Full analysis saved to: {output_file}", f)
    
    print(f"\n✓ Complete! Analysis saved to: {output_file}")

