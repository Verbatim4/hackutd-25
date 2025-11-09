'use client';

type SummaryData = {
  totalComplaints: number;
  redZones: number;
  actionTickets: number;
};

export default function SummarySidebar({ data }: { data: SummaryData }) {
  return (
    <div className="fixed right-0 top-16 bottom-0 w-80 bg-white border-l border-pink-200 p-6 overflow-y-auto z-30 shadow-lg">
      <h2 className="text-xl font-bold text-pink-600 mb-6">Dallas Summary</h2>
      
      <div className="space-y-4">
        {/* Total Complaints Box */}
        <button className="w-full text-left bg-gradient-to-br from-pink-50 to-white rounded-lg p-5 border-2 border-pink-200 shadow-md hover:shadow-lg hover:border-pink-300 transition-all cursor-pointer">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Total Complaints</h3>
            <svg className="w-6 h-6 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-3xl font-bold text-pink-600">{data.totalComplaints.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">Across all regions</p>
        </button>

        {/* Red Zones Box */}
        <button className="w-full text-left bg-gradient-to-br from-red-50 to-white rounded-lg p-5 border-2 border-red-200 shadow-md hover:shadow-lg hover:border-red-300 transition-all cursor-pointer">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Red Zones</h3>
            <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p className="text-3xl font-bold text-red-600">{data.redZones}</p>
          <p className="text-xs text-gray-500 mt-2">Regions requiring attention</p>
        </button>

        {/* Action Tickets Box */}
        <button className="w-full text-left bg-gradient-to-br from-blue-50 to-white rounded-lg p-5 border-2 border-blue-200 shadow-md hover:shadow-lg hover:border-blue-300 transition-all cursor-pointer">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Action Tickets</h3>
            <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <p className="text-3xl font-bold text-blue-600">{data.actionTickets}</p>
          <p className="text-xs text-gray-500 mt-2">Recommended solutions</p>
        </button>
      </div>
    </div>
  );
}

