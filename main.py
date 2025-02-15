from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import swisseph as swe  # Certifique-se de instalar essa biblioteca depois

app = FastAPI(
    title="API de Mapa Astral",
    description="API para cálculo e interpretação de mapas astrológicos.",
    version="0.1"
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
    aspects: List[Dict] = []  # Aspectos (ângulos, orbes, etc.)
    houses: List[Dict] = []   # Casas astrológicas

class CorrectionData(BaseModel):
    corrections: Dict[str, Dict[str, Optional[str]]]

class InterpretationRequest(BaseModel):
    map_data: MapResult

class QuestionRequest(BaseModel):
    question: str
    map_data: MapResult

# ========= Função de Cálculo =========

def calculate_astrological_positions(birth_data: BirthData) -> List[PlanetPosition]:
    try:
        day, month, year = map(int, birth_data.date.split('/'))
        hour, minute = map(int, birth_data.time.split(':'))
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido.")

    ut = hour + minute / 60.0
    jd = swe.julday(year, month, day, ut)

    # Defina o caminho para os arquivos de efemérides (se necessário)
    swe.set_ephe_path('/path/to/ephemeris')  # Ajuste esse caminho se for preciso

    # Códigos dos planetas conforme pyswisseph
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
        pos, ret = swe.calc(jd, planet_code)
        if ret != swe.OK:
            raise HTTPException(status_code=500, detail=f"Erro ao calcular {planet_name}.")
        longitude = pos[0]
        sign_index = int(longitude // 30)
        sign = zodiac_signs[sign_index]
        degree = longitude % 30
        positions.append(PlanetPosition(planet=planet_name, sign=sign, degree=degree))
    
    return positions

# ========= Endpoints =========

@app.post("/calculate", response_model=MapResult)
async def calculate_map(birth_data: BirthData):
    positions = calculate_astrological_positions(birth_data)
    dummy_aspects = []  # Lógica para aspectos pode ser implementada futuramente
    dummy_houses = []   # Lógica para casas também
    return MapResult(positions=positions, aspects=dummy_aspects, houses=dummy_houses)

@app.post("/validate")
async def validate_map(correction: CorrectionData):
    return {"status": "Dados validados", "corrections": correction.corrections}

@app.post("/interpret")
async def interpret_map(interpret_req: InterpretationRequest):
    interpretation = (
        "A posição do Sol indica sua essência e identidade, enquanto a Lua revela suas emoções profundas. "
        "Essa combinação sugere um caminho de autoconhecimento e transformação pessoal."
    )
    return {"interpretation": interpretation}

@app.post("/ask")
async def ask_question(question_req: QuestionRequest):
    answer = (
        f"Em resposta à sua pergunta '{question_req.question}', "
        "os aspectos do seu mapa indicam a importância do equilíbrio entre ação e introspecção."
    )
    return {"answer": answer}

@app.post("/finalize")
async def finalize_map(interpret_req: InterpretationRequest):
    summary = (
        "Seu mapa revela uma configuração única, onde desafios e potencial de crescimento se encontram."
    )
    suggestions = (
        "Sugestão: Invista em práticas de autoconhecimento, como meditação e análise pessoal, "
        "para aproveitar melhor as energias indicadas pelo seu mapa."
    )
    return {"summary": summary, "suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
