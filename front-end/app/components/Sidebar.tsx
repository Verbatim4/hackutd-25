'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-pink-200 flex flex-col z-40">

      <Link
        href="/"
        className={`flex items-center gap-3 px-6 py-4 hover:bg-pink-50 transition-colors ${
          pathname === '/' ? 'bg-pink-50 border-l-4 border-pink-500' : ''
        }`}
      >
        <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-pink-600 rounded-lg flex items-center justify-center font-bold text-white shadow-md">
          T
        </div>
        <span className="font-semibold text-lg text-pink-600">T-Mobile</span>
      </Link>


      <nav className="flex flex-col mt-4">
        <Link
          href="/"
          className={`px-6 py-3 hover:bg-pink-50 transition-colors text-gray-700 ${
            pathname === '/' ? 'bg-pink-50 border-l-4 border-pink-500' : ''
          }`}
        >
          Home
        </Link>
        <Link
          href="/trends"
          className={`px-6 py-3 hover:bg-pink-50 transition-colors text-gray-700 ${
            pathname === '/trends' ? 'bg-pink-50 border-l-4 border-pink-500' : ''
          }`}
        >
          Trends
        </Link>
        <Link
          href="/issues"
          className={`px-6 py-3 hover:bg-pink-50 transition-colors text-gray-700 ${
            pathname === '/issues' ? 'bg-pink-50 border-l-4 border-pink-500' : ''
          }`}
        >
          Issues
        </Link>
      </nav>
    </div>
  );
}

