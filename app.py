import streamlit as st
import auth
from views import (
    mapa_astral,
    revolucao_solar,
    vocacional,
    infantil,
    sinastria,
    transitos,
    matriz_destino,
    matriz_compatibilidade,
    matriz_infantil,
    videos,
    pdfs
)

# ==================================================
# CONFIGURAÇÃO INICIAL
# ==================================================
st.set_page_config(page_title="Portal Urano", page_icon="👁️", layout="wide")

# ==================================================
# ESTILO CUSTOMIZADO (CSS)
# ==================================================
def local_css():
    st.markdown("""
    <style>
        /* Importar fonte moderna */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Sidebar - Fundo Preto #211f1d */
        section[data-testid="stSidebar"] {
            background-color: #211f1d;
        }
        
        /* Textos da Sidebar - Branco/Cinza Claro */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] label, 
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {
            color: #ffffff !important;
        }

        /* Títulos Principais (Main Area) - Preto */
        .main h1, .main h2, .main h3 {
            color: #000000 !important;
        }
        
        /* Títulos Específicos em Roxo (se houver classe específica) ou destaques */
        .highlight-purple {
            color: #9a64ce !important;
        }

        /* Botões - Roxo #9a64ce */
        .stButton > button {
            background-color: #9a64ce;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #8040bf;
        }

        /* Aumentar a caixa de chat */
        .stChatInputContainer textarea {
            height: 100px !important;
            min-height: 100px !important;
        }

    </style>
    """, unsafe_allow_html=True)

local_css()

# ==================================================
# AUTENTICAÇÃO
# ==================================================
if not auth.login_page():
    st.stop()

# ==================================================
# BARRA LATERAL (NAVEGAÇÃO)
# ==================================================
# ==================================================
# BARRA LATERAL (NAVEGAÇÃO)
# ==================================================
PAGES = {
    "Mapa Astral": mapa_astral,
    "Revolução Solar": revolucao_solar,
    "Sinastria": sinastria,
    "Astrologia Vocacional": vocacional,
    "Astrologia Infantil": infantil,
    "Trânsitos": transitos,
    "Matriz Pessoal": matriz_destino,
    "Matriz Compatibilidade": matriz_compatibilidade,
    "Matriz Infantil": matriz_infantil,
    "Cursos": videos,
    "PDFs": pdfs
}

# Inicializar página atual se não existir
if "current_page" not in st.session_state:
    st.session_state.current_page = "Mapa Astral"

# Funções de callback para garantir seleção única
def update_astro():
    st.session_state.current_page = st.session_state.astro_selection
    st.session_state.matriz_selection = None
    st.session_state.aprendizado_selection = None

def update_matriz():
    st.session_state.current_page = st.session_state.matriz_selection
    st.session_state.astro_selection = None
    st.session_state.aprendizado_selection = None

def update_aprendizado():
    st.session_state.current_page = st.session_state.aprendizado_selection
    st.session_state.astro_selection = None
    st.session_state.matriz_selection = None

with st.sidebar:
    # Logo
    try:
        st.image("logo_olho.jpg", use_container_width=True)
    except:
        st.warning("Logo não encontrado (logo_olho.jpg)")
        
    st.markdown("<h2 style='text-align: center; color: #9a64ce !important;'>Portal Urano</h2>", unsafe_allow_html=True)
    st.write("") # Espaçamento

    # --- GRUPO 1: ASTROLOGIA ---
    st.markdown("<h3 style='color: #9a64ce !important; margin-bottom: 0px;'>🔮 ASTROLOGIA</h3>", unsafe_allow_html=True)
    st.radio(
        "Astrologia",
        ["Mapa Astral", "Revolução Solar", "Sinastria", "Astrologia Vocacional", "Astrologia Infantil", "Trânsitos"],
        key="astro_selection",
        index=0 if st.session_state.current_page in ["Mapa Astral", "Revolução Solar", "Sinastria", "Astrologia Vocacional", "Astrologia Infantil", "Trânsitos"] else None,
        on_change=update_astro,
        label_visibility="collapsed"
    )
    
    st.write("") # Espaçamento
    
    # --- GRUPO 2: MATRIZ DO DESTINO ---
    st.markdown("<h3 style='color: #9a64ce !important; margin-bottom: 0px;'>🔢 MATRIZ DO DESTINO</h3>", unsafe_allow_html=True)
    st.radio(
        "Matriz",
        ["Matriz Pessoal", "Matriz Compatibilidade", "Matriz Infantil"],
        key="matriz_selection",
        index=0 if st.session_state.current_page in ["Matriz Pessoal", "Matriz Compatibilidade", "Matriz Infantil"] else None,
        on_change=update_matriz,
        label_visibility="collapsed"
    )

    st.write("") # Espaçamento

    # --- GRUPO 3: APRENDIZADO ---
    st.markdown("<h3 style='color: #9a64ce !important; margin-bottom: 0px;'>📚 APRENDIZADO</h3>", unsafe_allow_html=True)
    st.radio(
        "Aprendizado",
        ["Cursos", "PDFs"],
        key="aprendizado_selection",
        index=0 if st.session_state.current_page in ["Cursos", "PDFs"] else None,
        on_change=update_aprendizado,
        label_visibility="collapsed"
    )
    
    st.divider()
    if st.button("Sair"):
        auth.logout()

# ==================================================
# ROTEAMENTO
# ==================================================
page = st.session_state.current_page
if page in PAGES:
    PAGES[page].render()
else:
    mapa_astral.render()
