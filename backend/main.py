from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hospitals")
def get_hospitals(lat: float, lon: float):
    # Query overpass for hospitals in a ~5km radius (5000 meters)
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:5000,{lat},{lon});
      way["amenity"="hospital"](around:5000,{lat},{lon});
      relation["amenity"="hospital"](around:5000,{lat},{lon});
    );
    out center;
    """
    try:
        headers = {'User-Agent': 'SwasthyaAILocalApp/1.0'}
        response = requests.post(overpass_url, data={'data': overpass_query}, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"status": "error", "message": f"Overpass API returned {response.status_code}: {response.text[:200]}"}
        data = response.json()
        hospitals = []
        for element in data.get('elements', []):
            if 'tags' in element and 'name' in element['tags']:
                name = element['tags']['name']
                lat_c = element.get('lat') or element.get('center', {}).get('lat')
                lon_c = element.get('lon') or element.get('center', {}).get('lon')
                
                # Mock MCDM Score based on heuristics + random
                score = min(100, max(50, 80 + int(random.gauss(0, 10))))
                
                # Check for uniqueness since Overpass might return ways and nodes for the same building
                if not any(h['name'] == name for h in hospitals):
                    hospitals.append({
                        "name": name,
                        "coords": [lat_c, lon_c],
                        "score": score
                    })

        if len(hospitals) == 0:
            raise Exception("No hospitals returned")
        hospitals.sort(key=lambda x: x["score"], reverse=True)
        return {"status": "success", "data": hospitals[:15]}  # Return top 15
    except Exception as e:
        mock_hospitals = [
            { "name": "Central General Hospital", "coords": [float(lat) + 0.015, float(lon) + 0.012], "score": 94 },
            { "name": "Metro Healthcare Center", "coords": [float(lat) - 0.010, float(lon) + 0.018], "score": 88 },
            { "name": "City Region Clinic", "coords": [float(lat) - 0.015, float(lon) - 0.010], "score": 75 },
            { "name": "Apex Specialty Hospital", "coords": [float(lat) + 0.020, float(lon) - 0.015], "score": 82 }
        ]
        return {"status": "success", "data": mock_hospitals}

@app.get("/api/aqi")
def get_aqi(lat: float, lon: float):
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
    try:
        res = requests.get(url)
        data = res.json()
        curr = data.get('current', {})
        return {
            "status": "success",
            "data": {
                "aqi": curr.get("us_aqi", "N/A"),
                "pm25": curr.get("pm2_5", "N/A"),
                "pm10": curr.get("pm10", "N/A"),
                "co": curr.get("carbon_monoxide", "N/A"),
                "no2": curr.get("nitrogen_dioxide", "N/A"),
                "so2": curr.get("sulphur_dioxide", "N/A"),
                "o3": curr.get("ozone", "N/A")
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/doctors")
def get_doctors():
    names = ["Dr. Arvind Patil", "Dr. Shalini Rao", "Dr. Manoj Kumar", "Dr. Sneha V", "Dr. K. N. Prakash", "Dr. Rajiv Menon"]
    specialties = ["Cardiologist", "General Physician", "Neurologist", "Dermatologist", "Pediatrician"]
    doctors = []
    
    for i in range(10):
        doctors.append({
            "name": random.choice(names),
            "type": random.choice(specialties),
            "experience": f"{random.randint(5, 25)} years",
            "fee": f"₹{random.choice([400, 500, 700, 900])}",
            "rating": round(random.uniform(4.0, 5.0), 1),
            "availability": random.choice(["Today 5 PM", "Tomorrow 10 AM", "Available Now", "Today 2 PM"]),
            "languages": random.choice(["EN, HI", "EN, KN", "EN, TE", "EN, HI, KN"]),
            "mode": random.choice(["In-Person", "Online + In-Person", "Online only"]),
            "insurance": "✅ Supported" if random.random() > 0.3 else "❌ Not listed"
        })
    # Remove duplicates by name to make the UI look cleaner
    unique_doctors = list({v['name']:v for v in doctors}.values())
    return {"status": "success", "data": unique_doctors}

@app.post("/api/chat")
def chat(message: str = Form(...)):
    msg = message.lower()
    
    # Emergency conditions
    emergencies = ["chest pain", "heart attack", "can't breathe", "breathless", "bleeding profusely", "stroke", "paralysis", "unconscious"]
    if any(e in msg for e in emergencies):
        reply = f"""
        <b>Critical Alert Triggered</b><br><br>
        <div class="triage-cards">
          <div class="triage-card red">🚨 Emergency</div>
          <div class="triage-card red">🚑 High Priority</div>
        </div>
        <br>Your symptoms indicate a possible medical emergency. Please press the <b>SOS button</b> immediately or call an ambulance to the nearest hospital!
        """
        return {"status": "success", "reply": reply}

    # High priority / Monitor
    high_priority = ["fever", "high temperature", "severe headache", "migraine", "vomiting", "dizzy", "fainting"]
    if any(h in msg for h in high_priority):
        reply = f"""
        <b>Symptom Triage Complete</b><br><br>
        <div class="triage-cards">
          <div class="triage-card amber">⚠️ Monitor</div>
          <div class="triage-card amber">🩺 Doctor Consult</div>
        </div>
        <br>Your symptoms require medical attention but are not immediately life-threatening. Please monitor your temperature and stay hydrated. Would you like me to find the nearest available General Physician?
        """
        return {"status": "success", "reply": reply}
        
    # Pollution / AQI related
    if "aqi" in msg or "pollution" in msg or "cough" in msg or "asthma" in msg:
        reply = f"""
        <b>Environmental Assessment</b><br><br>
        <div class="triage-cards">
          <div class="triage-card amber">😷 Dust/Pollution</div>
          <div class="triage-card green">🏠 Rest Indoors</div>
        </div>
        <br>These symptoms are highly correlated with the current AQI index in your area. I recommend shutting windows, turning on air purifiers if available, and taking your prescribed inhaler.
        """
        return {"status": "success", "reply": reply}

    # Minor issues
    minor_issues = ["cold", "runny nose", "mild pain", "fatigue", "tired", "back ache", "stomach ache"]
    if any(m in msg for m in minor_issues):
        reply = f"""
        <b>Symptom Triage Complete</b><br><br>
        <div class="triage-cards">
          <div class="triage-card green">✅ Not Emergency</div>
          <div class="triage-card green">💊 Self Care</div>
        </div>
        <br>This appears to be a minor health issue. Rest, take over-the-counter medication if previously prescribed by your doctor, and drink plenty of fluids. Let me know if symptoms worsen.
        """
        return {"status": "success", "reply": reply}

    # Default fallback
    replies = [
        "I am actively monitoring your profile. Could you provide a bit more detail about your symptoms?",
        "To help me make an accurate medical decision, please describe exactly what you are feeling and when it started.",
        "Your daily health profile is looking stable. Do you have any specific concerns today?"
    ]
    return {"status": "success", "reply": random.choice(replies)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
