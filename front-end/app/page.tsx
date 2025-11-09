'use client';

import { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import SummarySidebar from './components/SummarySidebar';

const DallasMap = dynamic(() => import('./components/DallasMap'), {
  ssr: false,
});

// Import location data to calculate summary
const dataIssuesLocations = [
  { issues: 145, performance: 'poor' },
  { issues: 98, performance: 'poor' },
  { issues: 112, performance: 'poor' },
  { issues: 12, performance: 'excellent' },
  { issues: 8, performance: 'excellent' },
  { issues: 15, performance: 'excellent' },
];

const internetIssuesLocations = [
  { issues: 132, performance: 'poor' },
  { issues: 87, performance: 'poor' },
  { issues: 105, performance: 'poor' },
  { issues: 9, performance: 'excellent' },
  { issues: 5, performance: 'excellent' },
  { issues: 11, performance: 'excellent' },
];

export default function Home() {
  const [view, setView] = useState<'data' | 'internet'>('data');

  const summaryData = useMemo(() => {
    const locations = view === 'data' ? dataIssuesLocations : internetIssuesLocations;
    const totalComplaints = locations.reduce((sum, loc) => sum + loc.issues, 0);
    const redZones = locations.filter(loc => loc.performance === 'poor').length;
    // Action tickets: typically 1-2 per red zone, plus some for high-complaint areas
    const actionTickets = redZones * 2 + Math.floor(totalComplaints / 50);
    
    return {
      totalComplaints,
      redZones,
      actionTickets,
    };
  }, [view]);

  return (
    <div className="h-screen w-full flex">
      <div className="flex-1 flex flex-col">
        <div className="p-6 bg-gradient-to-r from-pink-50 to-white border-b border-pink-200">
          <h1 className="text-2xl font-bold text-pink-600">Dallas Performance Map</h1>
        </div>
        <div className="h-[calc(100vh-240px)] mr-80 relative">
          {/* Toggle Bar - Centered above map */}
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000]">
            <div className="flex items-center gap-1 bg-white rounded-full px-1 py-1 border border-pink-200 shadow-sm">
              <button
                onClick={() => setView('data')}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                  view === 'data'
                    ? 'bg-pink-500 text-white'
                    : 'text-gray-600 hover:bg-pink-50'
                }`}
              >
                Data Issues
              </button>
              <button
                onClick={() => setView('internet')}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                  view === 'internet'
                    ? 'bg-pink-500 text-white'
                    : 'text-gray-600 hover:bg-pink-50'
                }`}
              >
                Internet Issues
              </button>
            </div>
          </div>
          <DallasMap view={view} />
        </div>
      </div>
      <SummarySidebar data={summaryData} />
    </div>
  );
}
