from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import swisseph as swe  # MANTIDO COMO NO ORIGINAL
import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

app = FastAPI(
    title="API de Mapa Astral",
    description="API com Quíron, Lilith, Nodos, retrogradação, casas com orbe, aspectos, elementos e quadruplicidades.",
    version="10.1",
    servers=[
        {"url": "https://api-mapa-astral.onrender.com", "description": "Servidor de Produção"}
    ]
)

# ========= Modelos de Dados =========

class BirthData(BaseModel):
    date: str      # Formato DD/MM/AAAA
    time: str      # Formato HH:MM
    city: str
    country: str

class PlanetPosition(BaseModel):
    planet: str
    sign: str
    degree: float
    house: int
    retrograde: bool = False

class HouseInfo(BaseModel):
    house: int
    sign: str
    degree: float

class Aspect(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str
    angle: float
    orb: float

class MapResult(BaseModel):
    positions: List[PlanetPosition]
    houses: List[HouseInfo]
    aspects: List[Aspect]
    elements: Dict[str, int]
    quadruplicities: Dict[str, int]

# ========= Configurações de Signos, Elementos e Quadruplicidades =========

zodiac_signs = [
    "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
    "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"
]

element_map = {
    "Áries": "Fogo", "Leão": "Fogo", "Sagitário": "Fogo",
    "Touro": "Terra", "Virgem": "Terra", "Capricórnio": "Terra",
    "Gêmeos": "Ar", "Libra": "Ar", "Aquário": "Ar",
    "Câncer": "Água", "Escorpião": "Água", "Peixes": "Água"
}

quad_map = {
    "Áries": "Cardinal", "Câncer": "Cardinal", "Libra": "Cardinal", "Capricórnio": "Cardinal",
    "Touro": "Fixo",     "Leão": "Fixo",      "Escorpião": "Fixo",    "Aquário": "Fixo",
    "Gêmeos": "Mutável", "Virgem": "Mutável", "Sagitário": "Mutável", "Peixes": "Mutável"
}

# ========= Corpos Principais (Quíron, Lilith, Nodos etc.) =========

PLANETS_SWEPH = {
    "Sol": swe.SUN,
    "Lua": swe.MOON,
    "Mercúrio": swe.MERCURY,
    "Vênus": swe.VENUS,
    "Marte": swe.MARS,
    "Júpiter": swe.JUPITER,
    "Saturno": swe.SATURN,
    "Urano": swe.URANUS,
    "Netuno": swe.NEPTUNE,
    "Plutão": swe.PLUTO,
    "Quíron": swe.CHIRON,
    "Lilith": swe.MEAN_APOG,
    "NóduloNorte": swe.TRUE_NODE
}

# ========= Geocodificação e Fuso Horário =========

def get_coordinates(city: str, country: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"city": city, "country": country, "format": "json"}
    headers = {"User-Agent": "AstroAPI/1.0"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location["lat"]), float(location["lon"])
    else:
        raise HTTPException(status_code=404, detail="Localização não encontrada")

def get_timezone(latitude: float, longitude: float):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    if timezone_str:
        return timezone_str
    else:
        raise HTTPException(status_code=500, detail="Não foi possível determinar o fuso horário.")

def convert_to_ut(date_str: str, time_str: str, timezone_str: str):
    try:
        local_tz = pytz.timezone(timezone_str)
        local_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        local_time = local_tz.localize(local_time)
        ut_time = local_time.astimezone(pytz.utc)
        return ut_time
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao converter horário: {e}")

# As demais funções (casas, aspectos, elementos, quadruplicidades, etc.) permanecem exatamente como estavam
# incluindo a calculate_map e os endpoints

# ========= Endpoints =========

@app.post("/calculate", response_model=MapResult)
async def calculate_map_endpoint(birth_data: BirthData):
    return calculate_map(birth_data)

@app.get("/")
async def read_root():
    return {"message": "API de Mapa Astral ativa! Acesse /docs para testar."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
