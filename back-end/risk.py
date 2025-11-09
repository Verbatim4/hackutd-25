import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

def detect_hotspots(df, eps_km=1, min_samples=250):
    """Cluster complaints by lat/lon using DBSCAN"""
    kms_per_radian = 6371.0088
    eps = eps_km / kms_per_radian
    coords = df[['lat', 'lon']].to_numpy()
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='haversine').fit(np.radians(coords))
    df['cluster_id'] = db.labels_
    return df[df['cluster_id'] != -1]


def aggregate_hotspots(df):
    df['tone_num'] = df['tone'].map({'angry': -1, 'neutral': 0, 'happy': 1})
    feature_df = df.groupby('cluster_id').apply(lambda x: pd.Series({
        'complaint_count': len(x),
        'avg_sentiment': x['sentiment_score'].mean(),
        'avg_tone_score': x['tone_num'].mean(),
        'network_share': (x['category']=='network').mean(),
        'latitude': x['latitude'].mean(),
        'longitude': x['longitude'].mean()
    })).reset_index()
    return feature_df


def label_risk(df):
    conditions = [
        (df['avg_sentiment'] < -0.3) & (df['complaint_count'] > 200),
        (df['avg_sentiment'] < 0) & (df['complaint_count'] > 100),
    ]
    choices = ['High', 'Medium']
    df['risk_level'] = np.select(conditions, choices, default='Low')
    return df


def build_graph(features, distance_threshold_km=2):
    """Create a PyTorch Geometric graph from hotspots"""
    coords = features[['lat','lon']].to_numpy()
    

    def haversine(coord1, coord2):
        lat1, lon1 = np.radians(coord1)
        lat2, lon2 = np.radians(coord2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2*np.arcsin(np.sqrt(a))
        return 6371.0088 * c
    
    N = coords.shape[0]
    edge_index = []
    for i in range(N):
        for j in range(i+1, N):
            if haversine(coords[i], coords[j]) <= distance_threshold_km:
                edge_index.append([i,j])
                edge_index.append([j,i])
    
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    

    node_features = features[['complaint_count','avg_sentiment','avg_tone_score',
                              'network_share','billing_share','support_share','app_share']].values
    x = torch.tensor(node_features, dtype=torch.float)
    

    risk_map = {'Low':0,'Medium':1,'High':2}
    y = torch.tensor(features['risk_level'].map(risk_map).values, dtype=torch.long)
    
    return Data(x=x, edge_index=edge_index, y=y)


class RiskGCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x


def run_pipeline(df):
 
    hotspots = detect_hotspots(df)

    features = aggregate_hotspots(hotspots)
    

    features = label_risk(features)
    

    data = build_graph(features)
    

    model = RiskGCN(in_channels=data.x.shape[1], hidden_channels=16, out_channels=3)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = torch.nn.CrossEntropyLoss()
    
    for epoch in range(200):
        model.train()
        optimizer.zero_grad()
        out = model(data)
        loss = criterion(out, data.y)
        loss.backward()
        optimizer.step()
        if epoch % 20 == 0:
            pred = out.argmax(dim=1)
            acc = (pred == data.y).sum().item() / data.y.size(0)
            print(f"Epoch {epoch}, Loss {loss.item():.4f}, Acc {acc:.4f}")
    

    model.eval()
    with torch.no_grad():
        out = model(data)
        predicted_risk = out.argmax(dim=1).numpy()
    
    risk_map_inv = {0:'Low',1:'Medium',2:'High'}
    features['predicted_risk'] = [risk_map_inv[i] for i in predicted_risk]
    
    return features, model

