import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from openai import OpenAI

# Initialize OpenAI client (make sure your OPENAI_API_KEY is set)
client = OpenAI()

def detect_hotspots_from_csv(csv_path, text_column=None, eps=0.5, min_samples=2, time_column=None):
   
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # --- Case 1: Textual hotspots ---
    if text_column:
        texts = df[text_column].tolist()
        # Convert text to embeddings
        embeddings = [
            client.embeddings.create(input=text, model="text-embedding-3-large")['data'][0]['embedding']
            for text in texts
        ]
        X = np.array(embeddings)
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(X)
    
    # --- Case 2: Numeric/spatial data ---
    else:
        features = df.select_dtypes(include=np.number).columns.tolist()
        if time_column and time_column in features:
            X = df[features].values
        else:
            numeric_cols = [c for c in features if c != time_column]
            X = df[numeric_cols].values
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

    # Assign clusters
    df['cluster'] = clustering.labels_

    # Compute severity = frequency of cluster
    cluster_counts = df['cluster'].value_counts().to_dict()
    df['severity'] = df['cluster'].map(lambda x: cluster_counts.get(x, 0))

    return df


csv_path = "dfw_complaints.csv"  # replace with your CSV file path
result = detect_hotspots_from_csv(csv_path, eps=3, min_samples=2, time_column='t')

print(result)
