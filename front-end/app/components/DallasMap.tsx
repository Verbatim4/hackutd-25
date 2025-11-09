'use client';

import { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Circle, useMap, Popup } from 'react-leaflet';
import type L from 'leaflet';

// Dallas center coordinates
const DALLAS_CENTER: [number, number] = [32.7767, -96.7970];

// Dallas bounds to restrict map view
const DALLAS_BOUNDS: L.LatLngBoundsExpression = [
  [32.65, -97.0], // Southwest corner
  [33.0, -96.6],  // Northeast corner
];

// Data issues locations
const dataIssuesLocations = [
  {
    position: [32.7767, -96.7970] as [number, number],
    name: 'Downtown Dallas',
    performance: 'poor',
    issues: 145,
    type: 'data',
    sentiment: 'negative',
    severity: -1,
    tags: ['slow speed', 'billing', 'connection drops'],
  },
  {
    position: [32.8000, -96.7900] as [number, number],
    name: 'Uptown Dallas',
    performance: 'poor',
    issues: 98,
    type: 'data',
    sentiment: 'negative',
    severity: -1,
    tags: ['slow speed', 'billing'],
  },
  {
    position: [32.7800, -96.7700] as [number, number],
    name: 'Deep Ellum',
    performance: 'poor',
    issues: 112,
    type: 'data',
    sentiment: 'negative',
    severity: -1,
    tags: ['connection drops', 'slow speed', 'billing'],
  },
  {
    position: [32.8600, -96.8100] as [number, number],
    name: 'North Dallas',
    performance: 'excellent',
    issues: 12,
    type: 'data',
    sentiment: 'positive',
    severity: 1,
    tags: ['fast speed', 'reliable'],
  },
  {
    position: [32.9100, -96.7400] as [number, number],
    name: 'Plano Area',
    performance: 'excellent',
    issues: 8,
    type: 'data',
    sentiment: 'positive',
    severity: 1,
    tags: ['excellent coverage', 'fast speed'],
  },
  {
    position: [32.9600, -96.8200] as [number, number],
    name: 'Addison',
    performance: 'excellent',
    issues: 15,
    type: 'data',
    sentiment: 'neutral',
    severity: 0,
    tags: ['average speed', 'reliable'],
  },
];

// Internet issues locations
const internetIssuesLocations = [
  {
    position: [32.7767, -96.7970] as [number, number],
    name: 'Downtown Dallas',
    performance: 'poor',
    issues: 132,
    type: 'internet',
    sentiment: 'negative',
    severity: -1,
    tags: ['slow speed', 'billing', 'outages'],
  },
  {
    position: [32.8000, -96.7900] as [number, number],
    name: 'Uptown Dallas',
    performance: 'poor',
    issues: 87,
    type: 'internet',
    sentiment: 'negative',
    severity: -1,
    tags: ['slow speed', 'billing'],
  },
  {
    position: [32.7800, -96.7700] as [number, number],
    name: 'Deep Ellum',
    performance: 'poor',
    issues: 105,
    type: 'internet',
    sentiment: 'negative',
    severity: -1,
    tags: ['outages', 'slow speed'],
  },
  {
    position: [32.8600, -96.8100] as [number, number],
    name: 'North Dallas',
    performance: 'excellent',
    issues: 9,
    type: 'internet',
    sentiment: 'positive',
    severity: 1,
    tags: ['fast speed', 'reliable'],
  },
  {
    position: [32.9100, -96.7400] as [number, number],
    name: 'Plano Area',
    performance: 'excellent',
    issues: 5,
    type: 'internet',
    sentiment: 'positive',
    severity: 1,
    tags: ['excellent coverage', 'fast speed'],
  },
  {
    position: [32.9600, -96.8200] as [number, number],
    name: 'Addison',
    performance: 'excellent',
    issues: 11,
    type: 'internet',
    sentiment: 'neutral',
    severity: 0,
    tags: ['average speed', 'reliable'],
  },
];

type LocationData = typeof dataIssuesLocations[0];

function MapContent({ 
  locations, 
  onHover, 
  onHoverPosition,
  hoveredIndex,
  onZoomChange,
  onMapReady
}: { 
  locations: LocationData[]; 
  onHover: (index: number | null) => void;
  onHoverPosition: (position: { x: number; y: number } | null) => void;
  hoveredIndex: number | null;
  onZoomChange: (isZoomed: boolean) => void;
  onMapReady: (map: L.Map) => void;
}) {
  const map = useMap();

  useEffect(() => {
    onMapReady(map);
  }, [map, onMapReady]);

  useEffect(() => {
    map.setView(DALLAS_CENTER, 11);
    map.setMaxBounds(DALLAS_BOUNDS);
    map.setMinZoom(10);
    map.setMaxZoom(16);
    onZoomChange(false);
  }, [map, onZoomChange]);

  // Track zoom level changes
  useEffect(() => {
    const updateZoomState = () => {
      const currentZoom = map.getZoom();
      const isZoomed = currentZoom > 11;
      onZoomChange(isZoomed);
    };

    map.on('zoomend', updateZoomState);
    map.on('moveend', updateZoomState);

    return () => {
      map.off('zoomend', updateZoomState);
      map.off('moveend', updateZoomState);
    };
  }, [map, onZoomChange]);

  // Update tooltip position when map moves/zooms
  useEffect(() => {
    if (hoveredIndex !== null) {
      const updatePosition = () => {
        const location = locations[hoveredIndex];
        const point = map.latLngToContainerPoint(location.position);
        onHoverPosition({ x: point.x, y: point.y });
      };

      map.on('move', updatePosition);
      map.on('zoom', updatePosition);

      return () => {
        map.off('move', updatePosition);
        map.off('zoom', updatePosition);
      };
    }
  }, [map, hoveredIndex, locations, onHoverPosition]);

  const handleMouseOver = (index: number, location: LocationData) => {
    onHover(index);
    // Calculate pixel position of the dot
    const point = map.latLngToContainerPoint(location.position);
    onHoverPosition({ x: point.x, y: point.y });
  };

  const handleMouseOut = () => {
    onHover(null);
    onHoverPosition(null);
  };

  const handleClick = (location: LocationData) => {
    // Zoom into the clicked location
    map.setView(location.position, 14, {
      animate: true,
      duration: 0.5
    });
  };

  return (
    <>
      {locations.map((location, index) => (
        <Circle
          key={index}
          center={location.position}
          radius={800}
          pathOptions={{
            fillColor: location.performance === 'poor' ? '#dc2626' : '#16a34a',
            fillOpacity: 1,
            color: location.performance === 'poor' ? '#dc2626' : '#16a34a',
            weight: 0,
            opacity: 1,
          }}
          eventHandlers={{
            mouseover: () => handleMouseOver(index, location),
            mouseout: handleMouseOut,
            click: () => handleClick(location),
          }}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold text-lg mb-2">{location.name}</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Sentiment:</strong> {location.sentiment}</p>
                <p><strong>Reviews:</strong> {location.issues}</p>
                <p><strong>Severity:</strong> {location.severity}</p>
                {location.tags && location.tags.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-semibold mb-1">Top Complaints:</p>
                    <div className="flex flex-wrap gap-1">
                      {location.tags.map((tag, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 bg-pink-50 text-pink-700 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Popup>
        </Circle>
      ))}
    </>
  );
}

type MapView = 'data' | 'internet';

export default function DallasMap({ view }: { view: MapView }) {
  const [isMounted, setIsMounted] = useState(false);
  const [hoveredLocation, setHoveredLocation] = useState<number | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ x: number; y: number } | null>(null);
  const [isZoomed, setIsZoomed] = useState(false);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const locations = view === 'data' ? dataIssuesLocations : internetIssuesLocations;

  const handleMapReady = (map: L.Map) => {
    mapInstanceRef.current = map;
  };

  const handleResetMap = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView(DALLAS_CENTER, 11, {
        animate: true,
        duration: 0.5
      });
    }
  };

  if (!isMounted) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <p className="text-gray-600">Loading map...</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={DALLAS_CENTER}
        zoom={11}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
        maxBounds={DALLAS_BOUNDS}
        minZoom={10}
        maxZoom={16}
        key={view}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="map-tiles"
        />
        <MapContent 
          locations={locations} 
          onHover={setHoveredLocation}
          onHoverPosition={setHoverPosition}
          hoveredIndex={hoveredLocation}
          onZoomChange={setIsZoomed}
          onMapReady={handleMapReady}
        />
      </MapContainer>

      {/* Reset Map Button */}
      {isZoomed && (
        <button
          onClick={handleResetMap}
          className="absolute top-4 right-4 bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg shadow-lg z-[1000] flex items-center gap-2 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reset View
        </button>
      )}
      
      {/* Hover Tooltip - Positioned above the dot */}
      {hoveredLocation !== null && hoverPosition && (
        <div 
          className="absolute bg-white rounded-lg shadow-xl p-4 z-[1000] border-2 border-pink-300 min-w-[250px] pointer-events-none"
          style={{
            left: `${hoverPosition.x}px`,
            top: `${hoverPosition.y - 180}px`,
            transform: 'translateX(-50%)',
          }}
        >
          <h3 className="font-bold text-lg mb-3 text-pink-600">{locations[hoveredLocation].name}</h3>
          <div className="space-y-2 text-sm mb-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-700">Sentiment:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                locations[hoveredLocation].sentiment === 'positive' 
                  ? 'bg-green-100 text-green-700' 
                  : locations[hoveredLocation].sentiment === 'negative'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {locations[hoveredLocation].sentiment}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-700">Reviews:</span>
              <span className="text-gray-600">{locations[hoveredLocation].issues}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-700">Severity:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                locations[hoveredLocation].severity === 1
                  ? 'bg-green-100 text-green-700'
                  : locations[hoveredLocation].severity === -1
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {locations[hoveredLocation].severity}
              </span>
            </div>
          </div>
          {/* Tags */}
          <div className="mt-3 pt-3 border-t border-pink-200">
            <p className="text-xs font-semibold text-gray-600 mb-2">Top Complaints:</p>
            <div className="flex flex-wrap gap-1.5">
              {locations[hoveredLocation].tags?.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-pink-50 text-pink-700 rounded text-xs border border-pink-200"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 z-[1000] border-2 border-pink-300">
        <h3 className="font-semibold mb-2 text-sm text-pink-600">Performance Indicators</h3>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          <span className="text-sm text-gray-700">High Risk Zones</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-700">Strong Coverage Zone</span>
        </div>
      </div>
    </div>
  );
}



