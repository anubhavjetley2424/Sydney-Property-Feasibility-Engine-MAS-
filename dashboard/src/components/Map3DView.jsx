import React from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, ColumnLayer } from '@deck.gl/layers';
import Map from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

export default function Map3DView({ lat = -33.8151, lng = 151.0012 }) {
  const INITIAL_VIEW_STATE = {
    longitude: lng,
    latitude: lat,
    zoom: 14,
    pitch: 45,
    bearing: 0
  };

  // Mock Data: Active DA Applications from your Scraper
  const daData = [
    { position: [lng + 0.002, lat + 0.002], size: 100 },
    { position: [lng - 0.003, lat + 0.001], size: 80 },
    { position: [lng + 0.001, lat - 0.004], size: 120 },
  ];

  // Mock Data: Older sold properties with price driving the 3D column height
  const soldData = [
    { position: [lng + 0.004, lat - 0.002], price: 1450000 },
    { position: [lng - 0.002, lat - 0.003], price: 2100000 },
    { position: [lng - 0.005, lat + 0.004], price: 980000 },
  ];

  const layers = [
    // 3D Columns for Sold Prices
    new ColumnLayer({
      id: 'sold-prices',
      data: soldData,
      diskResolution: 6,
      radius: 35,
      extruded: true,
      pickable: true,
      elevationScale: 0.05,
      getPosition: d => d.position,
      getFillColor: [227, 232, 228, 200], // Sage color
      getElevation: d => d.price,
    }),
    // Scatterplot for Active DAs
    new ScatterplotLayer({
      id: 'da-applications',
      data: daData,
      pickable: true,
      opacity: 0.8,
      stroked: true,
      filled: true,
      radiusScale: 1,
      radiusMinPixels: 4,
      radiusMaxPixels: 10,
      lineWidthMinPixels: 1,
      getPosition: d => d.position,
      getFillColor: [255, 59, 48], // Red indicator
      getLineColor: [0, 0, 0],
    })
  ];

  return (
    <div className="w-full h-full relative rounded-[24px] overflow-hidden border border-tileBorder">
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      >
        <Map
          mapboxAccessToken={MAPBOX_TOKEN}
          mapStyle="mapbox://styles/mapbox/dark-v11"
        />
      </DeckGL>
      <div className="absolute bottom-4 left-4 bg-appBg/80 backdrop-blur border border-white/10 p-3 rounded-xl text-xs">
        <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 bg-sageBg rounded-sm" /> 3D: Sold Price History</div>
        <div className="flex items-center gap-2"><div className="w-3 h-3 bg-[#ff3b30] rounded-full" /> Scatter: Active DAs</div>
      </div>
    </div>
  );
}