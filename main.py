from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos.",
    version="1.0"
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
    house: Optional[int] = None

class MapResult(BaseModel):
    positions: List[PlanetPosition]
    aspects: List[Dict] = []
    houses: List[Dict] = []

# ========= Função de Cálculo =========

def calculate_astrological_positions(birth_data: BirthData) -> List[PlanetPosition]:
    try:
        # Converte a data e a hora para números inteiros
        day, month, year = map(int, birth_data.date.split('/'))
        hour, minute = map(int, birth_data.time.split(':'))
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido.")

    # Calcula o tempo universal (UT) e o dia juliano
    ut = hour + minute / 60.0
    jd = swe.julday(year, month, day, ut)

    # Define o caminho para os arquivos de efemérides (ajuste esse caminho corretamente!)
    swe.set_ephe_path('./ephemeris')

    # Lista de planetas e seus códigos na biblioteca pyswisseph
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

    # Lista dos signos do zodíaco
    zodiac_signs = [
        "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
        "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"
    ]

    positions = []
    for planet_name, planet_code in planets.items():
        pos, ret = swe.calc(jd, planet_code)
        if ret != swe.OK:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}.")
        longitude = pos[0]
        sign_index = int(longitude // 30)
        sign = zodiac_signs[sign_index]
        degree = longitude % 30
        positions.append(PlanetPosition(planet=planet_name, sign=sign, degree=degree))
    
    return positions

# ========= Endpoint =========

@app.post("/calculate", response_model=MapResult)
async def calculate_map(birth_data: BirthData):
    positions = calculate_astrological_positions(birth_data)
    return MapResult(positions=positions)

@app.get("/")
async def read_root():
    return {"message": "API de Mapa Astral ativa! Acesse /docs para testar."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
