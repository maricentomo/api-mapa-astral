from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe
import requests
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos com ajuste automático de fuso horário.",
    version="7.0"
)

# ========= Modelos de Dados =========

class BirthData(BaseModel):
    date: str  # Formato: "DD/MM/AAAA"
    time: str  # Formato: "HH:MM"
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

# ========= Função de Geocodificação =========

def get_coordinates(city: str, country: str):
    """Obtém latitude e longitude usando o Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"city": city, "country": country, "format": "json"}
    headers = {"User-Agent": "AstroAPI/1.0"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        location = response.json()[0]
        latitude = float(location["lat"])
        longitude = float(location["lon"])
        return latitude, longitude
    else:
        raise HTTPException(status_code=404, detail="Localização não encontrada")

# ========= Função para Obter o Fuso Horário =========

def get_timezone(latitude: float, longitude: float):
    """Retorna o fuso horário com base na latitude e longitude."""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    if timezone_str:
        return timezone_str
    else:
        raise HTTPException(status_code=500, detail="Não foi possível determinar o fuso horário.")

# ========= Função para Converter para UT =========

def convert_to_ut(date_str: str, time_str: str, timezone_str: str):
    """Converte horário local para UT automaticamente com base no fuso horário detectado."""
    try:
        local_tz = pytz.timezone(timezone_str)
        local_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        local_time = local_tz.localize(local_time)
        ut_time = local_time.astimezone(pytz.utc)
        return ut_time
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao converter horário: {e}")

# ========= Função de Cálculo =========

def calculate_astrological_positions(birth_data: BirthData) -> MapResult:
    # Obtemos as coordenadas com base na cidade e país
    latitude, longitude = get_coordinates(birth_data.city, birth_data.country)

    # Determinamos o fuso horário corretamente
    timezone_str = get_timezone(latitude, longitude)

    # Convertemos para UT com base no fuso correto
    dt_ut = convert_to_ut(birth_data.date, birth_data.time, timezone_str)
    day, month, year = dt_ut.day, dt_ut.month, dt_ut.year
    ut = dt_ut.hour + dt_ut.minute / 60.0

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
    houses, asc_mc = swe.houses(jd, latitude, longitude, b'P')

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
            if cusp_start <= cusp_end:
                if cusp_start <= longitude < cusp_end:
                    return i + 1
            else:
                # Trata a transição de Peixes para Áries
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
