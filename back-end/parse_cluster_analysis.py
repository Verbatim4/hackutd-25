import csv
import re
from datetime import datetime

def parse_cluster_analysis(input_file, output_csv):
    """
    Parse the cluster analysis text file and create a CSV with cluster information.
    Marks clusters with rate limit errors as having no data.
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by cluster sections
    cluster_sections = re.split(r'={80}\nCLUSTER (\d+) - (\d+) complaints\n={80}', content)
    
    clusters_data = []
    
    # Process each cluster (skip first element which is header)
    for i in range(1, len(cluster_sections), 3):
        if i + 2 <= len(cluster_sections):
            cluster_id = int(cluster_sections[i])
            complaint_count = int(cluster_sections[i + 1])
            analysis_text = cluster_sections[i + 2].strip()
            
            # Check if this cluster has an error
            has_error = 'Error analyzing cluster' in analysis_text or '429 You exceeded your current quota' in analysis_text
            
            if has_error:
                # Mark as no data - leave fields blank
                cluster_data = {
                    'cluster_id': cluster_id,
                    'complaint_count': complaint_count,
                    'has_data': 'No',
                    'error': '',
                    'main_issue': '',
                    'common_patterns': '',
                    'severity': '',
                    'root_cause': '',
                    'recommended_action': '',
                    'full_analysis': ''
                }
            else:
                # Extract analysis components
                main_issue = extract_field(analysis_text, r'\*\*(?:1\. )?Main Issue\*\*:?\s*(.*?)(?=\*\*|$)', 'Not found')
                common_patterns = extract_field(analysis_text, r'\*\*(?:2\. )?Common Patterns\*\*:?\s*(.*?)(?=\*\*|$)', 'Not found')
                severity = extract_field(analysis_text, r'\*\*(?:3\. )?Severity Assessment\*\*:?\s*(.*?)(?=\*\*|$)', 'Not found')
                root_cause = extract_field(analysis_text, r'\*\*(?:4\. )?Root Cause\*\*:?\s*(.*?)(?=\*\*|$)', 'Not found')
                recommended_action = extract_field(analysis_text, r'\*\*(?:5\. )?Recommended Action\*\*:?\s*(.*?)(?=\*\*|$)', 'Not found')
                
                cluster_data = {
                    'cluster_id': cluster_id,
                    'complaint_count': complaint_count,
                    'has_data': 'Yes',
                    'error': '',
                    'main_issue': clean_text(main_issue),
                    'common_patterns': clean_text(common_patterns),
                    'severity': clean_text(severity),
                    'root_cause': clean_text(root_cause),
                    'recommended_action': clean_text(recommended_action),
                    'full_analysis': clean_text(analysis_text)
                }
            
            clusters_data.append(cluster_data)
    
    # Write to CSV
    if clusters_data:
        fieldnames = [
            'cluster_id',
            'complaint_count',
            'has_data',
            'error',
            'main_issue',
            'common_patterns',
            'severity',
            'root_cause',
            'recommended_action',
            'full_analysis'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clusters_data)
        
        print(f"✓ CSV file created: {output_csv}")
        print(f"  Total clusters: {len(clusters_data)}")
        print(f"  Clusters with data: {sum(1 for c in clusters_data if c['has_data'] == 'Yes')}")
        print(f"  Clusters with errors: {sum(1 for c in clusters_data if c['has_data'] == 'No')}")
    else:
        print("✗ No cluster data found in the file")


def extract_field(text, pattern, default=''):
    """Extract a field using regex pattern"""
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return default


def clean_text(text):
    """Clean up text by removing extra whitespace and newlines"""
    # Replace multiple newlines with a single space
    text = re.sub(r'\n+', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


if __name__ == '__main__':
    input_file = 'cluster_analysis_20251109_025757.txt'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = f'cluster_analysis_{timestamp}.csv'
    
    print(f"Parsing cluster analysis from: {input_file}")
    parse_cluster_analysis(input_file, output_csv)

