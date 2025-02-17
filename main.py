from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe
import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos com Quíron, Lilith, Nodos, casas com orbe de transição e aspectos com orbes específicas.",
    version="9.0",
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

# ========= Configurações de Signos e Elementos =========

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

# ========= Corpos Principais: Inclui Quíron, Lilith, Nodos e ASC/MC =========
# NóduloNorte = swe.TRUE_NODE (ou swe.NORTH_NODE); NóduloSul será calculado manualmente

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
    "Lilith": swe.MEAN_APOG,      # Lilith Média
    "NóduloNorte": swe.TRUE_NODE
    # NóduloSul será +180° do NóduloNorte
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
    """Converte horário local para UT."""
    try:
        local_tz = pytz.timezone(timezone_str)
        local_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        local_time = local_tz.localize(local_time)
        ut_time = local_time.astimezone(pytz.utc)
        return ut_time
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao converter horário: {e}")

# ========= Funções para Casas, Orbe de Transição e Aspectos =========

def find_house_with_orb(planet_long: float, houses: List[float]) -> int:
    """
    Determina em qual casa está o planeta, considerando:
      - 6° de orbe para casas comuns
      - 8° de orbe para casa 1 (Asc) ou casa 10 (MC)
    """
    for i in range(12):
        cusp_start = houses[i]
        cusp_end = houses[(i + 1) % 12]

        # Nominal: planet_long está entre cusp_start e cusp_end (com wrap)
        if cusp_start <= cusp_end:
            # Caso não cruza 360
            if cusp_start <= planet_long < cusp_end:
                nominal_house = i + 1
                # Distância até o final desta casa
                distance_to_next = cusp_end - planet_long
                next_house_id = ((i + 1) % 12) + 1
                # Orbe = 8° se for casa 1 ou 10, senão 6°
                orb = 8 if next_house_id in [1, 10] else 6
                if distance_to_next <= orb:
                    return next_house_id
                return nominal_house

        else:
            # cruza 360
            if planet_long >= cusp_start or planet_long < cusp_end:
                nominal_house = i + 1
                if planet_long >= cusp_start:
                    distance_to_next = (cusp_end + 360) - planet_long if cusp_end < planet_long else 0
                else:
                    distance_to_next = cusp_end - planet_long
                next_house_id = ((i + 1) % 12) + 1
                orb = 8 if next_house_id in [1, 10] else 6
                if 0 < distance_to_next <= orb:
                    return next_house_id
                return nominal_house

    # fallback
    return 1

def calculate_aspects(positions: List[PlanetPosition]) -> List[Aspect]:
    """
    Identifica aspectos:
      - Conjunção, Quadratura, Oposição, Trígono → orbe = 8°
      - Sextil → orbe = 6°
    """
    aspect_defs = [
        ("Conjunção", 0, 8),
        ("Oposição", 180, 8),
        ("Quadratura", 90, 8),
        ("Trígono", 120, 8),
        ("Sextil", 60, 6)
    ]

    def to_360(p: PlanetPosition) -> float:
        sign_idx = zodiac_signs.index(p.sign)
        return sign_idx*30 + p.degree

    aspects = []
    n = len(positions)
    for i in range(n):
        for j in range(i+1, n):
            p1 = positions[i]
            p2 = positions[j]
            deg1 = to_360(p1)
            deg2 = to_360(p2)
            diff = abs(deg1 - deg2)
            diff = min(diff, 360 - diff)

            for asp_name, asp_angle, orb in aspect_defs:
                if abs(diff - asp_angle) <= orb:
                    aspects.append(Aspect(
                        planet1=p1.planet,
                        planet2=p2.planet,
                        aspect_type=asp_name,
                        angle=round(diff, 2),
                        orb=round(abs(diff - asp_angle), 2)
                    ))
    return aspects

def calculate_elements(positions: List[PlanetPosition]) -> Dict[str, int]:
    """
    Conta elementos apenas para:
    - Sol, Lua, Ascendente, MC valem 2 pontos
    - Demais planetas 'normais' valem 1 ponto
    - Quíron, Lilith, NóduloNorte, NóduloSul não entram
    """
    counts = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}
    dois_pontos = {"Sol", "Lua", "Ascendente", "MeioCéu"}

    for p in positions:
        if p.planet in ["Quíron", "Lilith", "NóduloNorte", "NóduloSul"]:
            continue
        # Descobrir elemento
        elem = element_map[p.sign]
        peso = 2 if p.planet in dois_pontos else 1
        counts[elem] += peso

    return counts

# ========= Função Principal que Calcula Mapa =========

def calculate_map(birth_data: BirthData) -> MapResult:
    # 1) Geocodificação e Fuso
    lat, lon = get_coordinates(birth_data.city, birth_data.country)
    tz_str = get_timezone(lat, lon)

    # 2) Converter data/hora local p/ UT
    dt_ut = convert_to_ut(birth_data.date, birth_data.time, tz_str)
    day, month, year = dt_ut.day, dt_ut.month, dt_ut.year
    ut_hour = dt_ut.hour + dt_ut.minute/60.0

    # 3) JD
    jd = swe.julday(year, month, day, ut_hour)
    swe.set_ephe_path("./ephemeris")

    # 4) Casas e asc_mc (Placidus)
    houses, asc_mc = swe.houses(jd, lat, lon, b'P')

    # Montar infos de casas
    house_list = []
    for i, cusp in enumerate(houses, start=1):
        sign_idx = int(cusp // 30)
        sign = zodiac_signs[sign_idx]
        deg = cusp % 30
        house_list.append(HouseInfo(
            house=i,
            sign=sign,
            degree=round(deg, 2)
        ))

    # 5) Calcular posições
    positions: List[PlanetPosition] = []
    for planet_name, code in PLANETS_SWEPH.items():
        pos, ret = swe.calc(jd, code)
        if ret < 0:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}")
        longit = pos[0]
        sign_idx = int(longit // 30)
        sign = zodiac_signs[sign_idx]
        deg = longit % 30
        planet_house = find_house_with_orb(longit, houses)

        positions.append(PlanetPosition(
            planet=planet_name,
            sign=sign,
            degree=round(deg, 2),
            house=planet_house
        ))

    # NóduloSul = NóduloNorte + 180° (mod 360)
    nodo_norte = next((p for p in positions if p.planet == "NóduloNorte"), None)
    if nodo_norte:
        nodonorte_deg360 = zodiac_signs.index(nodo_norte.sign)*30 + nodo_norte.degree
        south_deg = (nodonorte_deg360 + 180) % 360
        south_sign_idx = int(south_deg // 30)
        south_sign = zodiac_signs[south_sign_idx]
        south_deg_in_sign = south_deg % 30
        # Determinar casa do nodo sul
        nodo_sul_house = find_house_with_orb(south_deg, houses)
        positions.append(PlanetPosition(
            planet="NóduloSul",
            sign=south_sign,
            degree=round(south_deg_in_sign, 2),
            house=nodo_sul_house
        ))

    # Calcular Asc e MC como planetas especiais
    # asc_mc[0] = Asc, asc_mc[1] = MC
    asc_long = asc_mc[0]
    asc_sign_idx = int(asc_long // 30)
    asc_sign = zodiac_signs[asc_sign_idx]
    asc_deg = asc_long % 30
    asc_house = 1  # Asc nominalmente na casa 1
    positions.append(PlanetPosition(
        planet="Ascendente",
        sign=asc_sign,
        degree=round(asc_deg, 2),
        house=asc_house
    ))

    mc_long = asc_mc[1]
    mc_sign_idx = int(mc_long // 30)
    mc_sign = zodiac_signs[mc_sign_idx]
    mc_deg = mc_long % 30
    mc_house = 10  # MC nominalmente na casa 10
    positions.append(PlanetPosition(
        planet="MeioCéu",
        sign=mc_sign,
        degree=round(mc_deg, 2),
        house=mc_house
    ))

    # 6) Calcular aspectos
    aspects_list = calculate_aspects(positions)

    # 7) Calcular distribuição de elementos
    elements_count = calculate_elements(positions)

    return MapResult(
        positions=positions,
        houses=house_list,
        aspects=aspects_list,
        elements=elements_count
    )

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
