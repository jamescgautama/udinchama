"use client";

import Map, { Source, Layer } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

export default function MyMap() {
    return (
        <Map
            initialViewState={{
                longitude: 111.91,
                latitude: -0.31,
                zoom: 10,
            }}
            style={{ width: "100%", height: "600px" }}
            mapStyle={{
                version: 8,
                sources: {
                    osm: {
                        type: "raster",
                        tiles: [
                            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        ],
                        tileSize: 256,
                        attribution: "© OpenStreetMap contributors",
                    },
                    subtype: {
                        type: "raster",
                        tiles: [
                            "https://udf.ai/fc_QbKlijf4CsvgRTeHRFsF6/udf_1/run/tiles/{z}/{x}/{y}",
                        ],
                        tileSize: 256,
                    },
                },
                layers: [
                    {
                        id: "osm",
                        type: "raster",
                        source: "osm",
                    },
                    {
                        id: "subtype",
                        type: "raster",
                        source: "subtype",
                        paint: {
                            "raster-opacity": 0.7,
                        },
                    },
                ],
            }}
        />
    );
}