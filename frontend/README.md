# MineSight AI — React Frontend (Map Development)

This is a dedicated, isolated React + Vite development environment created to build and test the modular **ManganeseProspectivityMap** geospatial component.

## Key Notes
- **MVP Unmodified**: The existing Python/FastAPI backend and vanilla HTML/CSS/JS dashboard (`Mang/dashboard/`) remain completely intact and operational.
- **Testing Route**: Visiting `/map-demo` renders the `MapDemoPage` testing harness.
- **Data Location**: Real exploration datasets (`exploration_scores.json`, `occurrences.csv`) will later be placed into `public/data/`.
- **Integration**: This frontend is currently an isolated component testing environment and will eventually be integrated with the main MineSight AI platform.

## Getting Started

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Visit [http://localhost:5173/map-demo](http://localhost:5173/map-demo) in your browser.
