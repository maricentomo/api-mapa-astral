"""
Módulo para geração de gráficos SVG de mapas astrais
Utiliza a biblioteca kerykeion para renderizar mandalas astrológicas customizáveis
"""

from kerykeion import AstrologicalSubject, KrInstance
from kerykeion.charts.kerykeion_chart_svg import KerykeionChartSVG
from typing import Dict, Optional
import os


class CustomChartColors:
    """
    Classe para definir cores customizadas do gráfico astral
    Você pode modificar estas cores conforme necessário
    """
    # Cores dos signos
    fire_color = "#FF6B6B"  # Fogo: Áries, Leão, Sagitário
    earth_color = "#8B4513"  # Terra: Touro, Virgem, Capricórnio
    air_color = "#87CEEB"   # Ar: Gêmeos, Libra, Aquário
    water_color = "#4682B4"  # Água: Câncer, Escorpião, Peixes
    
    # Cores dos planetas
    sun_color = "#FFD700"
    moon_color = "#C0C0C0"
    mercury_color = "#FFA500"
    venus_color = "#FF69B4"
    mars_color = "#DC143C"
    jupiter_color = "#9370DB"
    saturn_color = "#696969"
    uranus_color = "#00CED1"
    neptune_color = "#4169E1"
    pluto_color = "#8B008B"
    
    # Cores dos aspectos
    conjunction_color = "#000000"
    opposition_color = "#FF0000"
    trine_color = "#0000FF"
    square_color = "#FF4500"
    sextile_color = "#32CD32"
    
    # Cores de fundo e texto
    background_color = "#FFFFFF"
    zodiac_ring_color = "#893f89"  # Roxo do Portal Urano
    text_color = "#000000"
    house_line_color = "#666666"


def generate_chart_svg(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    nation: str = "BR",
    lng: Optional[float] = None,
    lat: Optional[float] = None,
    tz_str: Optional[str] = None,
    custom_colors: Optional[CustomChartColors] = None
) -> str:
    """
    Gera um gráfico SVG do mapa astral
    
    Args:
        name: Nome da pessoa
        year: Ano de nascimento
        month: Mês de nascimento (1-12)
        day: Dia de nascimento
        hour: Hora de nascimento (0-23)
        minute: Minuto de nascimento (0-59)
        city: Cidade de nascimento
        nation: Código do país (padrão: "BR" para Brasil)
        lng: Longitude (opcional, será calculada se não fornecida)
        lat: Latitude (opcional, será calculada se não fornecida)
        tz_str: Timezone string (opcional, será calculado se não fornecido)
        custom_colors: Objeto CustomChartColors com cores personalizadas
    
    Returns:
        String contendo o SVG do mapa astral
    """
    
    # Criar sujeito astrológico
    subject = AstrologicalSubject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        nation=nation,
        lng=lng,
        lat=lat,
        tz_str=tz_str
    )
    
    # Configurar cores customizadas se fornecidas
    chart_settings = {}
    if custom_colors:
        chart_settings = {
            "chart_colors_settings": {
                "fire": custom_colors.fire_color,
                "earth": custom_colors.earth_color,
                "air": custom_colors.air_color,
                "water": custom_colors.water_color,
                "background": custom_colors.background_color,
                "zodiac_radix_ring_3": custom_colors.zodiac_ring_color,
                "paper_0": custom_colors.background_color,
                "paper_1": custom_colors.background_color,
            }
        }
    
    # Criar instância do gráfico
    chart = KerykeionChartSVG(
        subject,
        chart_type="Natal",
        **chart_settings
    )
    
    # Gerar SVG
    svg_content = chart.makeSVG()
    
    return svg_content


def generate_chart_svg_from_birth_data(
    name: str,
    date: str,  # Formato: DD/MM/YYYY
    time: str,  # Formato: HH:MM
    city: str,
    country: str = "Brazil",
    custom_colors: Optional[CustomChartColors] = None
) -> str:
    """
    Gera SVG do mapa astral a partir de dados de nascimento no formato usado pela API
    
    Args:
        name: Nome da pessoa
        date: Data no formato DD/MM/YYYY
        time: Hora no formato HH:MM
        city: Cidade de nascimento
        country: País de nascimento
        custom_colors: Cores customizadas (opcional)
    
    Returns:
        String contendo o SVG do mapa astral
    """
    
    # Parse da data
    day, month, year = map(int, date.split('/'))
    
    # Parse da hora
    hour, minute = map(int, time.split(':'))
    
    # Mapear país para código
    country_codes = {
        "Brazil": "BR",
        "Brasil": "BR",
        "United States": "US",
        "Portugal": "PT",
        # Adicione mais países conforme necessário
    }
    nation = country_codes.get(country, "BR")
    
    return generate_chart_svg(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        nation=nation,
        custom_colors=custom_colors
    )


def save_chart_svg(svg_content: str, filename: str, output_dir: str = "./charts") -> str:
    """
    Salva o SVG em um arquivo
    
    Args:
        svg_content: Conteúdo SVG
        filename: Nome do arquivo (sem extensão)
        output_dir: Diretório de saída
    
    Returns:
        Caminho completo do arquivo salvo
    """
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Caminho completo
    filepath = os.path.join(output_dir, f"{filename}.svg")
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return filepath
