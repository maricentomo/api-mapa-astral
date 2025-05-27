from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import swisseph as swe
import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

app = FastAPI(
    title="API de Mapa Astral",
    description="API com Quíron, Lilith, Nodos, retrogradação, casas com orbe, aspectos, elementos e quadruplicidades.",
    version="10.1",
    servers=[
        {"url": "https://api-mapa-astral-production.up.railway.app", "description": "Servidor de Produção"}
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
    quadruplicities: Dict[str, int]  # <-- ADICIONAMOS AQUI

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
    # NóduloSul = +180° do NóduloNorte manualmente
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

# ========= Funções para Casas, Orbe de Transição e Aspectos =========

def find_house_with_orb(planet_long: float, houses: List[float]) -> int:
    """
    Determina em qual casa está o planeta (Sol, Lua, etc.), aplicando:
      - 6° de orbe para casas comuns
      - 8° se a próxima casa for 1 ou 10
    """
    for i in range(12):
        cusp_start = houses[i]
        cusp_end = houses[(i + 1) % 12]

        if cusp_start <= cusp_end:
            if cusp_start <= planet_long < cusp_end:
                nominal_house = i + 1
                dist_next = cusp_end - planet_long
                next_house_id = ((i + 1) % 12) + 1
                orb = 8 if next_house_id in [1, 10] else 6
                if dist_next <= orb:
                    return next_house_id
                return nominal_house
        else:
            if planet_long >= cusp_start or planet_long < cusp_end:
                nominal_house = i + 1
                if planet_long >= cusp_start:
                    dist_next = (cusp_end + 360) - planet_long if cusp_end < planet_long else 0
                else:
                    dist_next = cusp_end - planet_long
                next_house_id = ((i + 1) % 12) + 1
                orb = 8 if next_house_id in [1, 10] else 6
                if 0 < dist_next <= orb:
                    return next_house_id
                return nominal_house
    return 1

def find_house_nominal(planet_long: float, houses: List[float]) -> int:
    """Usado para NóduloNorte e NóduloSul (sem orbe)."""
    for i in range(12):
        cusp_start = houses[i]
        cusp_end = houses[(i + 1) % 12]
        if cusp_start <= cusp_end:
            if cusp_start <= planet_long < cusp_end:
                return i + 1
        else:
            if planet_long >= cusp_start or planet_long < cusp_end:
                return i + 1
    return 1

def calculate_aspects(positions: List[PlanetPosition]) -> List[Aspect]:
    """
    Identifica aspectos com orbe diferenciada:
      - Conjunção, Quadratura, Oposição, Trígono: 8°
      - Sextil: 6°
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
    Conta elementos só para planetas 'normais' + Sol/Lua.
    - Sol, Lua, Asc, MC = 2
    - Demais planetas = 1
    - Exclui Quíron, Lilith, Nódulos
    """
    counts = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}
    dois_pontos = {"Sol", "Lua", "Ascendente", "MeioCéu"}

    for p in positions:
        if p.planet in ["Quíron", "Lilith", "NóduloNorte", "NóduloSul"]:
            continue
        elem = element_map[p.sign]
        peso = 2 if p.planet in dois_pontos else 1
        counts[elem] += peso
    return counts

def calculate_quadruplicities(positions: List[PlanetPosition]) -> Dict[str, int]:
    """
    Cardinal, Fixo, Mutável, mesma regra de pontuação:
    - Sol, Lua, Asc, MC = 2
    - Demais planetas = 1
    - Exclui Quíron, Lilith, Nódulos
    """
    counts = {"Cardinal": 0, "Fixo": 0, "Mutável": 0}
    dois_pontos = {"Sol", "Lua", "Ascendente", "MeioCéu"}

    for p in positions:
        if p.planet in ["Quíron", "Lilith", "NóduloNorte", "NóduloSul"]:
            continue
        quad_type = quad_map[p.sign]  # 'Cardinal', 'Fixo' ou 'Mutável'
        peso = 2 if p.planet in dois_pontos else 1
        counts[quad_type] += peso
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

    # 4) Casas (Placidus) e asc_mc
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
    positions = []
    for planet_name, code in PLANETS_SWEPH.items():
        pos, ret = swe.calc(jd, code)
        if ret < 0:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}")

        longitude = pos[0]
        speed_long = pos[3]
        is_retro = (speed_long < 0)

        # Nódulos sem orbe
        if planet_name == "NóduloNorte":
            planet_house = find_house_nominal(longitude, houses)
        else:
            planet_house = find_house_with_orb(longitude, houses)

        sign_idx = int(longitude // 30)
        sign = zodiac_signs[sign_idx]
        deg = longitude % 30

        positions.append(PlanetPosition(
            planet=planet_name,
            sign=sign,
            degree=round(deg, 2),
            house=planet_house,
            retrograde=is_retro
        ))

    # NóduloSul = NóduloNorte + 180°
    nodo_norte = next((p for p in positions if p.planet == "NóduloNorte"), None)
    if nodo_norte:
        nn_deg = zodiac_signs.index(nodo_norte.sign)*30 + nodo_norte.degree
        south_deg = (nn_deg + 180) % 360
        south_sign_idx = int(south_deg // 30)
        south_sign = zodiac_signs[south_sign_idx]
        south_deg_in_sign = south_deg % 30
        nodo_sul_house = find_house_nominal(south_deg, houses)

        positions.append(PlanetPosition(
            planet="NóduloSul",
            sign=south_sign,
            degree=round(south_deg_in_sign, 2),
            house=nodo_sul_house,
            retrograde=False
        ))

    # Ascendente
    asc_long = asc_mc[0]
    asc_sign_idx = int(asc_long // 30)
    asc_sign = zodiac_signs[asc_sign_idx]
    asc_deg = asc_long % 30
    positions.append(PlanetPosition(
        planet="Ascendente",
        sign=asc_sign,
        degree=round(asc_deg, 2),
        house=1,
        retrograde=False
    ))

    # MeioCéu
    mc_long = asc_mc[1]
    mc_sign_idx = int(mc_long // 30)
    mc_sign = zodiac_signs[mc_sign_idx]
    mc_deg = mc_long % 30
    positions.append(PlanetPosition(
        planet="MeioCéu",
        sign=mc_sign,
        degree=round(mc_deg, 2),
        house=10,
        retrograde=False
    ))

    # 6) Calcular aspectos
    aspects_list = calculate_aspects(positions)

    # 7) Elementos
    elements_count = calculate_elements(positions)

    # 8) Quadruplicidades
    quads_count = calculate_quadruplicities(positions)

    # Retorno final
    return MapResult(
        positions=positions,
        houses=house_list,
        aspects=aspects_list,
        elements=elements_count,
        quadruplicities=quads_count  # AQUI INCLUÍMOS QUADRUPLICITIES
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
