'use client';

import { useState, useEffect } from 'react';

interface SentimentStats {
  total_complaints: number;
  avg_sentiment: number;
  negative_count: number;
  neutral_count: number;
  positive_count: number;
  timestamp: string;
}

interface TrendsData {
  image: string;
  stats: SentimentStats;
}

export default function TrendsPage() {
  const [trendsData, setTrendsData] = useState<TrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/sentiment-trends');
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setTrendsData(data);
        setError(null);
        setLastUpdate(new Date());
      }
    } catch (err) {
      setError('Failed to connect to Flask API. Make sure it\'s running on port 8000.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchTrends();
    }, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getSentimentColor = (score: number) => {
    if (score < 0.35) return 'text-red-600';
    if (score < 0.65) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getSentimentLabel = (score: number) => {
    if (score < 0.35) return 'Negative';
    if (score < 0.65) return 'Neutral';
    return 'Positive';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-[#E20074] mb-2">
                T-Mobile Sentiment Trends
              </h1>
              <p className="text-gray-600">
                Real-time sentiment analysis of website complaints
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="text-lg font-semibold text-gray-700">
                {lastUpdate.toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>

        {trendsData?.stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-lg p-5 border-l-4 border-[#E20074]">
              <h3 className="text-sm text-gray-600 mb-1">Total Complaints</h3>
              <p className="text-3xl font-bold text-gray-800">
                {trendsData.stats.total_complaints.toLocaleString()}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-5 border-l-4 border-red-500">
              <h3 className="text-sm text-gray-600 mb-1">Negative</h3>
              <p className="text-3xl font-bold text-red-600">
                {trendsData.stats.negative_count.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((trendsData.stats.negative_count / trendsData.stats.total_complaints) * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-5 border-l-4 border-yellow-500">
              <h3 className="text-sm text-gray-600 mb-1">Neutral</h3>
              <p className="text-3xl font-bold text-yellow-600">
                {trendsData.stats.neutral_count.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((trendsData.stats.neutral_count / trendsData.stats.total_complaints) * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-5 border-l-4 border-green-500">
              <h3 className="text-sm text-gray-600 mb-1">Positive</h3>
              <p className="text-3xl font-bold text-green-600">
                {trendsData.stats.positive_count.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((trendsData.stats.positive_count / trendsData.stats.total_complaints) * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-5 border-l-4 border-[#E8168B]">
              <h3 className="text-sm text-gray-600 mb-1">Avg Sentiment</h3>
              <p className={`text-3xl font-bold ${getSentimentColor(trendsData.stats.avg_sentiment)}`}>
                {trendsData.stats.avg_sentiment.toFixed(3)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {getSentimentLabel(trendsData.stats.avg_sentiment)}
              </p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-5 h-5 text-[#E20074] focus:ring-[#E20074] rounded"
              />
              <span className="text-sm font-medium text-gray-700">
                Auto-refresh (30s)
              </span>
            </label>
            {autoRefresh && (
              <span className="flex items-center gap-2 text-sm text-green-600">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                Live
              </span>
            )}
          </div>

          <button
            onClick={fetchTrends}
            disabled={loading}
            className="px-6 py-2 bg-[#E20074] text-white font-semibold rounded-lg hover:bg-[#E8168B] transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Updating...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh Now
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700 font-medium">{error}</p>
                <p className="text-xs text-red-600 mt-1">
                  Run: <code className="bg-red-100 px-2 py-1 rounded">python app.py</code>
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-6">
          {loading && !trendsData && (
            <div className="flex flex-col items-center justify-center py-20">
              <svg className="animate-spin h-16 w-16 text-[#E20074] mb-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p className="text-gray-600 text-lg">Generating sentiment analysis...</p>
              <p className="text-gray-400 text-sm mt-2">This may take a few moments</p>
            </div>
          )}

          {trendsData?.image && !loading && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Sentiment Trend Analysis
              </h2>
              <img
                src={trendsData.image}
                alt="Sentiment trends visualization"
                className="w-full rounded-lg shadow-md"
              />
              <p className="text-sm text-gray-500 text-center mt-4">
                Generated at {new Date(trendsData.stats.timestamp).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}