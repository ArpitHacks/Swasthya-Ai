# Swasthya AI

Swasthya AI is a web-based urban healthcare companion that helps users find nearby hospitals, check air quality, browse doctors, and get symptom-based triage guidance.

## Features

- Location-aware hospital search using OpenStreetMap Overpass API
- Air quality lookup via Open-Meteo AQI API
- Mock doctor recommendations for quick browsing
- Symptom triage chat assistant for emergency and non-emergency guidance
- Progressive web app support via `manifest.json` and `sw.js`

## Project Structure

- `index.html` — Frontend user interface with map, search, chat, and interactive sections
- `backend/main.py` — FastAPI backend providing hospital, AQI, doctor, and chat endpoints
- `manifest.json` — PWA metadata for installable app behavior
- `sw.js` — Service worker registration for offline capabilities
- `icon.svg` — App icon asset

## Tech Stack

- HTML/CSS/JavaScript frontend
- Leaflet.js for interactive map support
- FastAPI backend in Python
- External APIs: Overpass API, Open-Meteo AQI API

## Local Setup

1. Install Python dependencies:

```powershell
cd backend
python -m pip install -r requirements.txt
```

2. Run the backend server:

```powershell
python main.py
```

3. Open `index.html` in a browser or serve it from a local static host.

> If you use a browser server, make sure the frontend can reach the backend API endpoints.

## Notes

- The backend uses `requests` and `fastapi`.
- The app is designed for demo and prototype use; some data is mocked when external APIs fail.
- Adjust the host and port in `backend/main.py` if needed.

## License

Add your preferred license here.
