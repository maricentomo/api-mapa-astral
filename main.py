from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe
import requests
from datetime import datetime

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos.",
    version="5.0"
)

# ========= Modelos de Dados =========

class BirthData(BaseModel):
    date: str  # Formato: "DD/MM/AAAA"
    time: str  # Formato: "HH:MM" ou "HH:MM AM/PM"
    city: str
    country: str

class PlanetPosition(BaseModel):
    planet: str
    sign: str
    degree: float
    house: int

class MapResult(BaseModel):
    positions: List[PlanetPosition]
    aspects: List[Dict] = []
    houses: List[Dict] = []

# ========= Função de Conversão de Horário =========

def convert_to_24h_format(time_str: str) -> str:
    """Converte horário para o formato 24h, aceitando AM/PM ou HH:MM."""
    try:
        # Se o usuário passar no formato HH:MM, já funciona normalmente
        if ":" in time_str and len(time_str) == 5:
            return time_str
        # Se for AM/PM, convertemos
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        return time_obj.strftime("%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM ou HH:MM AM/PM.")

# ========= Função de Geocodificação =========

def get_coordinates(city: str, country: str):
    """Obtém latitude e longitude usando o Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"city": city, "country": country, "format": "json"}
    headers = {"User-Agent": "AstroAPI/1.0"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location["lat"]), float(location["lon"])
    else:
        raise HTTPException(status_code=404, detail="Localização não encontrada")

# ========= Função de Cálculo =========

def calculate_astrological_positions(birth_data: BirthData) -> MapResult:
    # Converte o horário para o formato correto
    time_24h = convert_to_24h_format(birth_data.time)

    # Obtemos as coordenadas com base na cidade e país
    latitude, longitude = get_coordinates(birth_data.city, birth_data.country)

    # Converte data e hora para calcular o dia juliano
    try:
        day, month, year = map(int, birth_data.date.split('/'))
        hour, minute = map(int, time_24h.split(':'))
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido.")

    ut = hour + minute / 60.0
    jd = swe.julday(year, month, day, ut)

    # Define o caminho para os arquivos de efemérides
    swe.set_ephe_path('./ephemeris')

    planets = {
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
    }

    zodiac_signs = [
        "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
        "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"
    ]

    # Calcular as cúspides das casas (sistema Placidus)
    houses, asc_mc = swe.houses(jd, latitude, longitude, b'A')

    house_list = []
    for i, cusp in enumerate(houses, start=1):
        sign_index = int(cusp // 30)
        sign = zodiac_signs[sign_index]
        degree = cusp % 30
        house_list.append({"house": i, "sign": sign, "degree": round(degree, 2)})

    # Determinar a casa de cada planeta
    def find_house(longitude):
        for i in range(12):
            cusp_start = houses[i]
            cusp_end = houses[(i + 1) % 12]
            if cusp_start < cusp_end:
                if cusp_start <= longitude < cusp_end:
                    return i + 1
            else:
                if longitude >= cusp_start or longitude < cusp_end:
                    return i + 1
        return 1

    positions = []
    for planet_name, planet_code in planets.items():
        pos, ret = swe.calc(jd, planet_code)
        if ret < 0:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}.")
        longitude = pos[0]
        sign_index = int(longitude // 30)
        sign = zodiac_signs[sign_index]
        degree = longitude % 30
        planet_house = find_house(longitude)
        positions.append(PlanetPosition(planet=planet_name, sign=sign, degree=round(degree, 2), house=planet_house))

    return MapResult(positions=positions, houses=house_list)

# ========= Endpoint =========

@app.post("/calculate", response_model=MapResult)
async def calculate_map(birth_data: BirthData):
    result = calculate_astrological_positions(birth_data)
    return result

@app.get("/")
async def read_root():
    return {"message": "API de Mapa Astral ativa! Acesse /docs para testar."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

