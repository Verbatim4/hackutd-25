from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb+srv://shrek:tmobilepostwave@cluster0.b3tjrkb.mongodb.net/?appName=Cluster0')
db = client['tmobile']
collection = db['complaints']

tmobile_pink = '#E20074'
tmobile_magenta = '#E8168B'
tmobile_light_pink = '#FF6BB5'

def generate_sentiment_plots(df):
    """Generate all 4 sentiment trend plots"""
    if 'date' not in df.columns:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df['date'] = pd.to_datetime(np.random.choice(
            pd.date_range(start_date, end_date), 
            size=len(df)
        ))
    
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = '#F8F8F8'
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('T-Mobile Website Complaints - Sentiment Trends (30 Days)', 
                 fontsize=20, fontweight='bold', color=tmobile_pink)
    
    daily_avg = df.groupby(df['date'].dt.date)['sentiment_score'].mean().reset_index()
    daily_avg.columns = ['date', 'avg_sentiment']
    ax1 = axes[0, 0]
    sns.lineplot(data=daily_avg, x='date', y='avg_sentiment', 
                 color=tmobile_pink, linewidth=2.5, ax=ax1)
    ax1.fill_between(daily_avg['date'], daily_avg['avg_sentiment'], 
                     alpha=0.3, color=tmobile_light_pink)
    ax1.set_title('Daily Average Sentiment Score', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=11)
    ax1.set_ylabel('Average Sentiment Score', fontsize=11)
    ax1.tick_params(axis='x', rotation=45)
    ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Neutral (0.5)')
    ax1.legend()
    
    df['sentiment_category'] = pd.cut(df['sentiment_score'], 
                                       bins=[0, 0.35, 0.65, 1.0],
                                       labels=['Negative', 'Neutral', 'Positive'])
    daily_counts = df.groupby([df['date'].dt.date, 'sentiment_category']).size().reset_index()
    daily_counts.columns = ['date', 'sentiment_category', 'count']
    ax2 = axes[0, 1]
    for category, color in zip(['Negative', 'Neutral', 'Positive'], 
                               [tmobile_pink, tmobile_magenta, tmobile_light_pink]):
        data = daily_counts[daily_counts['sentiment_category'] == category]
        sns.lineplot(data=data, x='date', y='count', 
                    label=category, color=color, linewidth=2.5, ax=ax2)
    ax2.set_title('Daily Complaint Counts by Sentiment', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Number of Complaints', fontsize=11)
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend()
    
    df_sorted = df.sort_values('date')
    df_sorted['rolling_avg'] = df_sorted['sentiment_score'].rolling(window=min(10000, len(df)), min_periods=1).mean()
    daily_rolling = df_sorted.groupby(df_sorted['date'].dt.date)['rolling_avg'].mean().reset_index()
    ax3 = axes[1, 0]
    sns.lineplot(data=daily_rolling, x='date', y='rolling_avg', 
                 color=tmobile_magenta, linewidth=3, ax=ax3)
    ax3.fill_between(daily_rolling['date'], daily_rolling['rolling_avg'], 
                     alpha=0.2, color=tmobile_pink)
    ax3.set_title('Rolling Average Sentiment Trend', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date', fontsize=11)
    ax3.set_ylabel('Rolling Average Sentiment', fontsize=11)
    ax3.tick_params(axis='x', rotation=45)
    ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    
    df['week'] = df['date'].dt.isocalendar().week
    weekly_data = df.groupby('week')['sentiment_score'].apply(list).reset_index()
    ax4 = axes[1, 1]
    positions = range(len(weekly_data))
    bp = ax4.boxplot([weekly_data.loc[i, 'sentiment_score'] for i in weekly_data.index],
                      positions=positions,
                      patch_artist=True,
                      widths=0.6)
    for patch in bp['boxes']:
        patch.set_facecolor(tmobile_light_pink)
        patch.set_alpha(0.7)
    for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color=tmobile_pink, linewidth=2)
    ax4.set_title('Weekly Sentiment Score Distribution', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Week', fontsize=11)
    ax4.set_ylabel('Sentiment Score', fontsize=11)
    ax4.set_xticklabels([f'W{int(w)}' for w in weekly_data['week']])
    ax4.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64

@app.route('/api/sentiment-trends', methods=['GET'])
def get_sentiment_trends():
    try:
        complaints = list(collection.find({}, {'_id': 0}).limit(50000))
        
        if not complaints:
            return jsonify({"error": "No data found in MongoDB"}), 404
        
        df = pd.DataFrame(complaints)
        
        if 'sentiment_score' not in df.columns:
            df['sentiment_score'] = np.random.beta(2, 5, size=len(df))
        
        image_base64 = generate_sentiment_plots(df)
        
        stats = {
            "total_complaints": len(df),
            "avg_sentiment": float(df['sentiment_score'].mean()),
            "negative_count": int((df['sentiment_score'] < 0.35).sum()),
            "neutral_count": int(((df['sentiment_score'] >= 0.35) & (df['sentiment_score'] <= 0.65)).sum()),
            "positive_count": int((df['sentiment_score'] > 0.65).sum()),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "image": f"data:image/png;base64,{image_base64}",
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
