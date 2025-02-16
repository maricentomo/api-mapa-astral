from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe
import requests
from timezonefinder import TimezoneFinder
import pytz

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos com aspectos.",
    version="1.1"
)

class BirthData(BaseModel):
    date: str
    time: str
    city: str
    country: str

class PlanetPosition(BaseModel):
    planet: str
    sign: str
    degree: float
    house: Optional[int] = None

class Aspect(BaseModel):
    planet1: str
    planet2: str
    angle: float
    aspect_type: str

class MapResult(BaseModel):
    positions: List[PlanetPosition]
    aspects: List[Aspect]
    houses: List[Dict]

def calculate_astrological_positions(birth_data: BirthData) -> List[PlanetPosition]:
    day, month, year = map(int, birth_data.date.split('/'))
    hour, minute = map(int, birth_data.time.split(':'))
    ut = hour + minute / 60.0
    jd = swe.julday(year, month, day, ut)
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

    positions = []
    for planet_name, planet_code in planets.items():
        pos, _ = swe.calc(jd, planet_code)
        longitude = pos[0]
        sign_index = int(longitude // 30)
        sign = zodiac_signs[sign_index]
        degree = longitude % 30
        positions.append(PlanetPosition(planet=planet_name, sign=sign, degree=degree))

    return positions

def calculate_aspects(positions: List[PlanetPosition]) -> List[Aspect]:
    aspects = []
    aspect_angles = {
        "Conjunção": 0,
        "Oposição": 180,
        "Quadratura": 90,
        "Trígono": 120,
        "Sextil": 60
    }

    for i, planet1 in enumerate(positions):
        for j, planet2 in enumerate(positions):
            if i < j:
                angle_diff = abs(planet1.degree - planet2.degree)
                angle_diff = min(angle_diff, 360 - angle_diff)

                for aspect_name, target_angle in aspect_angles.items():
                    if abs(angle_diff - target_angle) <= 6:
                        aspects.append(
                            Aspect(
                                planet1=planet1.planet,
                                planet2=planet2.planet,
                                angle=angle_diff,
                                aspect_type=aspect_name
                            )
                        )
    return aspects

@app.post("/calculate", response_model=MapResult)
def calculate_map(birth_data: BirthData):
    positions = calculate_astrological_positions(birth_data)
    aspects = calculate_aspects(positions)
    dummy_houses = []
    return MapResult(positions=positions, aspects=aspects, houses=dummy_houses)

@app.get("/")
def read_root():
    return {"message": "API de Mapa Astral com cálculo de aspectos ativa!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
