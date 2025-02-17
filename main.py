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
    description="API para cálculo e interpretação de mapas astrológicos com Quíron, Lilith, Nodos e contagem custom de elementos.",
    version="8.0",
    servers=[
        {"url": "https://api-mapa-astral.onrender.com", "description": "Servidor de Produção"}
    ]
)

# ========= Modelos =========

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

# ========= Configuração de Signos e Elementos =========

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

# Observação: O Sul é calculado como Norte + 180° (mod 360)
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
    "NóduloNorte": swe.TRUE_NODE  # Ou swe.NORTH_NODE se preferir
    # NóduloSul será calculado manualmente
}

# ========= Funções de Geocodificação e Fuso Horário =========

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

def get_timezone(latitude: float, longitude: float):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    if timezone_str:
        return timezone_str
    else:
        raise HTTPException(status_code=500, detail="Não foi possível determinar o fuso horário.")

def convert_to_ut(date_str: str, time_str: str, timezone_str: str):
    """Converte o horário local para UT usando pytz."""
    try:
        local_tz = pytz.timezone(timezone_str)
        # Date e time no formato DD/MM/AAAA HH:MM
        local_time = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        local_time = local_tz.localize(local_time)
        ut_time = local_time.astimezone(pytz.utc)
        return ut_time
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao converter horário: {e}")

# ========= Funções de Cálculo de Mapas, Casas, Elementos, Aspectos =========

def calc_houses_and_ascmc(jd, lat, lon):
    """Retorna as cúspides das casas e asc_mc (Asc, MC, etc.) no sistema Placidus."""
    houses, asc_mc = swe.houses(jd, lat, lon, b'P')
    # asc_mc[0] = Ascendente, asc_mc[1] = Meio do Céu
    return houses, asc_mc

def find_house(longitude, houses):
    """Determina em qual casa está o corpo, dada sua longitude e as cúspides."""
    for i in range(12):
        cusp_start = houses[i]
        cusp_end = houses[(i + 1) % 12]
        if cusp_start <= cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1
    return 1

def calculate_elements(positions: List[PlanetPosition]) -> Dict[str, int]:
    """
    Conta quantos pontos em cada elemento (Fogo, Terra, Ar, Água).
    - Sol, Lua, Ascendente, MC valem 2 pontos.
    - Demais planetas valem 1 ponto.
    - Quíron, Lilith, Nodos não entram nessa contagem.
    """
    counts = {"Fogo": 0, "Terra": 0, "Ar": 0, "Água": 0}
    dois_pontos = {"Sol", "Lua", "Ascendente", "MeioCéu"}

    for p in positions:
        if p.planet in ["Quíron", "Lilith", "NóduloNorte", "NóduloSul"]:
            continue  # Não conta no elemento
        # Verificar elemento
        elem = element_map[p.sign]
        weight = 2 if p.planet in dois_pontos else 1
        counts[elem] += weight
    return counts

def calculate_aspects(positions: List[PlanetPosition]) -> List[Aspect]:
    """
    Identifica aspectos com:
    - Conjunção, Quadratura, Oposição, Trígono: orbe = 8°
    - Sextil: orbe = 6°
    """
    aspect_defs = [
        ("Conjunção", 0, 8),
        ("Oposição", 180, 8),
        ("Quadratura", 90, 8),
        ("Trígono", 120, 8),
        ("Sextil", 60, 6),
    ]

    # Converter planetas para graus de 0 a 360
    def to_360(p: PlanetPosition) -> float:
        # Índice do signo * 30 + grau
        sign_idx = zodiac_signs.index(p.sign)
        return sign_idx*30 + p.degree

    # Vamos criar uma lista temporária
    new_positions = []
    for p in positions:
        full_deg = to_360(p)
        new_positions.append((p.planet, full_deg))

    aspects = []
    n = len(new_positions)
    for i in range(n):
        for j in range(i+1, n):
            planet1, deg1 = new_positions[i]
            planet2, deg2 = new_positions[j]
            diff = abs(deg1 - deg2)
            diff = min(diff, 360 - diff)
            for (asp_name, asp_angle, orb) in aspect_defs:
                if abs(diff - asp_angle) <= orb:
                    aspects.append(Aspect(
                        planet1=planet1,
                        planet2=planet2,
                        aspect_type=asp_name,
                        angle=round(diff, 2),
                        orb=round(abs(diff - asp_angle), 2)
                    ))
    return aspects

# ========= Função Principal =========

def calculate_map(birth_data: BirthData) -> MapResult:
    # 1) Obter coordenadas e fuso
    lat, lon = get_coordinates(birth_data.city, birth_data.country)
    tz = get_timezone(lat, lon)

    # 2) Converter data/hora local para UT
    dt_ut = convert_to_ut(birth_data.date, birth_data.time, tz)
    day, month, year = dt_ut.day, dt_ut.month, dt_ut.year
    ut_hour = dt_ut.hour + dt_ut.minute/60.0

    # 3) Calcular dia juliano
    jd = swe.julday(year, month, day, ut_hour)

    # 4) Carregar efemérides e calcular casas
    swe.set_ephe_path('./ephemeris')
    houses, asc_mc = calc_houses_and_ascmc(jd, lat, lon)

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

    # 5) Calcular posições dos corpos
    planets_positions = []
    for planet_name, code in PLANETS_SWEPH.items():
        pos, ret = swe.calc(jd, code)
        if ret < 0:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}")
        longit = pos[0]
        sign_idx = int(longit // 30)
        sign = zodiac_signs[sign_idx]
        deg = longit % 30
        planet_house = find_house(longit, houses)

        planets_positions.append(PlanetPosition(
            planet=planet_name,
            sign=sign,
            degree=round(deg, 2),
            house=planet_house
        ))

    # Calcular Nodo Sul (NóduloSul = NóduloNorte + 180°)
    # obs: valor é mod 360
    nodo_norte = next((p for p in planets_positions if p.planet == "NóduloNorte"), None)
    if nodo_norte:
        south_deg = ( (zodiac_signs.index(nodo_norte.sign)*30 + nodo_norte.degree) + 180 ) % 360
        south_sign_idx = int(south_deg // 30)
        south_sign = zodiac_signs[south_sign_idx]
        south_deg_in_sign = south_deg % 30
        # Determinar casa do nodo sul
        nodo_sul_house = find_house(south_deg, houses)
        nodo_sul = PlanetPosition(
            planet="NóduloSul",
            sign=south_sign,
            degree=round(south_deg_in_sign, 2),
            house=nodo_sul_house
        )
        planets_positions.append(nodo_sul)

    # 6) Incluir Ascendente e MeioCéu como “planetas” para contagem e aspectos
    # asc_mc[0] = ASC, asc_mc[1] = MC
    asc_long = asc_mc[0]
    asc_sign_idx = int(asc_long // 30)
    asc_sign = zodiac_signs[asc_sign_idx]
    asc_deg = asc_long % 30
    # Ascendente está sempre na casa 1 “na teoria”
    planets_positions.append(PlanetPosition(
        planet="Ascendente",
        sign=asc_sign,
        degree=round(asc_deg, 2),
        house=1
    ))

    mc_long = asc_mc[1]
    mc_sign_idx = int(mc_long // 30)
    mc_sign = zodiac_signs[mc_sign_idx]
    mc_deg = mc_long % 30
    # MC está sempre na casa 10 “na teoria”
    planets_positions.append(PlanetPosition(
        planet="MeioCéu",
        sign=mc_sign,
        degree=round(mc_deg, 2),
        house=10
    ))

    # 7) Calcular aspectos
    aspects_list = calculate_aspects(planets_positions)

    # 8) Calcular distribuição dos elementos
    elements_count = calculate_elements(planets_positions)

    return MapResult(
        positions=planets_positions,
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
