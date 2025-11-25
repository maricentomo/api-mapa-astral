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
    pdfs,
    home,
    artes
)

# ==================================================
# CONFIGURAÇÃO INICIAL
# ==================================================
st.set_page_config(page_title="Portal Urano", page_icon="logo_olho_final.jpg", layout="wide")

# ==================================================
# ESTILO CUSTOMIZADO (CSS REVISADO)
# ==================================================
def local_css():
    st.markdown("""
    <style>
        /* Importar fontes */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=MuseoModerno:wght@400;700&display=swap');

        /* === 1. FUNDO GERAL DA APLICAÇÃO === */
        /* Updated at 2025-11-23 20:02 */
        .stApp {
            background-color: #0e0b16;
            background-image: linear-gradient(to bottom right, #0e0b16, #1a1528);
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
        }

        /* ============================================================
           ESTILOS DA SIDEBAR (BARRA LATERAL)
           ============================================================ */

        /* --- 1. CONFIGURAÇÃO GERAL DA SIDEBAR --- */
        /* Define a cor de fundo e borda da barra lateral */
        section[data-testid="stSidebar"] {
            background-color: #211f1d !important;
            border-right: 1px solid #333;
        }

        /* Define a cor padrão dos textos na sidebar */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] label {
            color: #c7a7eb !important;
        }

        /* --- 2. TÍTULOS DAS CATEGORIAS (Ex: ASTROLOGIA) --- */
        .sidebar-category-title {
            padding: 0 16px;
            margin-bottom: 12px;  /* Espaço abaixo do título */
            margin-top: 30px;     /* Espaço acima do título */
            font-size: 18px;
            font-family: 'MuseoModerno', sans-serif !important; /* Fonte Nova */
            font-weight: 700;
            color: #c7a7eb !important; /* Cor Lilás */
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Remove margem superior apenas do primeiro título */
        .sidebar-category-title:first-of-type {
            margin-top: 10px;
        }

        /* --- 3. REMOÇÃO DE ESPAÇAMENTOS PADRÃO DO STREAMLIT --- */
        /* Remove margens, paddings e gaps dos containers internos para controle total */
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] > div > div,
        section[data-testid="stSidebar"] .element-container,
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0px !important;
        }

        /* --- 4. ESTILO DOS BOTÕES DO MENU --- */
        
        /* Container do botão */
        div[data-testid="stSidebar"] .stButton {
            margin: 0 !important;
            transform: translateY(-50%);
            height: 70%;
            width: 3px;
            background-color: #000000;
            border-radius: 0 3px 3px 0;
            transition: background-color 0.2s ease;
        }

        div[data-testid="stSidebar"] .stButton > button:hover::before {
            background-color: #c7a7eb; /* Cor da barra no hover */
        }

        /* --- 5. SUBMENU (Indentação) --- */
        div[data-testid="stSidebar"] .submenu-button > button {
            font-size: 13px !important;
            padding-left: 32px !important; /* Mais recuado */
            color: #6b7280 !important;
        }

        div[data-testid="stSidebar"] .submenu-button > button:hover {
            color: #c7a7eb !important;
            background-color: #000000 !important;
        }

        /* === 5. ÁREA PRINCIPAL === */
        /* Títulos Cinzel */
        h1, h2, h3, .mystic-title {
            font-family: 'Cinzel', serif !important;
            color: #ffffff !important;
            font-weight: 700;
        }

        /* Subtítulos */
        p, .mystic-subtitle {
            color: #b0b0b0;
            font-size: 18px; /* Convertido de 1.1rem */
        }

        /* Input de Chat */
        .stTextInput > div > div > input,
        .stChatInputContainer textarea {
            background-color: #1c1826 !important;
            color: white !important;
            border: 1px solid #3d3d3d !important;
            border-radius: 12px !important;
        }

        .stTextInput > div > div > input:focus,
        .stChatInputContainer textarea:focus {
            border-color: #c7a7eb !important;
            box-shadow: 0 0 5px #c7a7eb80 !important; /* Convertido de rgba */
        }

        /* Botões de Ação Rápida */
        .action-btn {
            background-color: #ffffff0d; /* Convertido de rgba(255,255,255,0.05) */
            border: 1px solid #444;
            color: #ddd;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px; /* Convertido de 0.9rem */
            margin-right: 8px;
            text-decoration: none;
            display: inline-block;
            transition: 0.3s;
        }

        .action-btn:hover {
            border-color: #c7a7eb;
            color: #c7a7eb;
            background-color: #c7a7eb1a; /* Convertido de rgba(199, 167, 235, 0.1) */
        }

        /* Header do Portal */
        .portal-header {
            font-family: 'Cinzel', serif;
            font-size: 40px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
            letter-spacing: -0.02em;
        }

        .portal-sub {
            font-size: 10px;
            color: #c7a7eb;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 500;
        }

        .status-dot {
            height: 6px;
            width: 6px;
            background-color: #4ade80;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 5px #4ade80;
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
# BARRA LATERAL
# ==================================================
if "menu_category" not in st.session_state:
    st.session_state.menu_category = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

with st.sidebar:
    # --- HEADER ---
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True) # Espaço topo
    # Logo centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo_olho_final.jpg", use_container_width=True)
        except:
            st.markdown('<div style="text-align: center; font-size: 40px;">👁️</div>', unsafe_allow_html=True)
    
    st.divider()

    # --- MENU (Com Títulos de Categoria) ---
    
    # CATEGORIA: ASTROLOGIA
    st.markdown('<div class="sidebar-category-title">✦ ASTROLOGIA</div>', unsafe_allow_html=True)
    
    if st.button("☉ Mapa Astral", key="sub_mapa"): 
        st.session_state.current_page = "Mapa Astral"
        st.session_state.menu_category = None
    if st.button("⊙ Revolução Solar", key="sub_rev"): 
        st.session_state.current_page = "Revolução Solar"
        st.session_state.menu_category = None
    if st.button("♡ Sinastria", key="sub_sinastria"): 
        st.session_state.current_page = "Sinastria"
        st.session_state.menu_category = None
    if st.button("⚙ Vocacional", key="sub_vocacional"): 
        st.session_state.current_page = "Astrologia Vocacional"
        st.session_state.menu_category = None
    if st.button("○ Infantil", key="sub_infantil"): 
        st.session_state.current_page = "Astrologia Infantil"
        st.session_state.menu_category = None
    if st.button("⊕ Trânsitos", key="sub_transitos"): 
        st.session_state.current_page = "Trânsitos"
        st.session_state.menu_category = None

    # CATEGORIA: MATRIZ DO DESTINO
    st.markdown('<div class="sidebar-category-title">◇ MATRIZ DO DESTINO</div>', unsafe_allow_html=True)
    
    if st.button("◎ Matriz Pessoal", key="sub_matriz_p"): 
        st.session_state.current_page = "Matriz Pessoal"
        st.session_state.menu_category = None
    if st.button("⬡ Matriz Compatibilidade", key="sub_matriz_c"): 
        st.session_state.current_page = "Matriz Compatibilidade"
        st.session_state.menu_category = None
    if st.button("○ Matriz Infantil", key="sub_matriz_i"): 
        st.session_state.current_page = "Matriz Infantil"
        st.session_state.menu_category = None

    # CATEGORIA: TUTORIAIS
    st.markdown('<div class="sidebar-category-title">◈ TUTORIAIS</div>', unsafe_allow_html=True)
    
    if st.button("▷ Vídeos", key="sub_videos"): 
        st.session_state.current_page = "Cursos"
        st.session_state.menu_category = None
    if st.button("□ PDFs", key="sub_pdfs"): 
        st.session_state.current_page = "PDFs"
        st.session_state.menu_category = None

    # CATEGORIA: ARTES
    st.markdown('<div class="sidebar-category-title">◈ ARTES</div>', unsafe_allow_html=True)
    
    if st.button("▢ Galeria", key="btn_artes"):
        st.session_state.current_page = "Artes"
        st.session_state.menu_category = None

    # Footer
    st.write("")
    st.write("")
    with st.container():
        st.markdown(f"""
        <div style="background-color: #1a1816; padding: 12px; border-radius: 8px; border: 1px solid #333; display: flex; align-items: center; gap: 10px;">
            <div style="background-color: #c7a7eb; color: #211f1d; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">US</div>
            <div>
                <div style="color: white; font-weight: bold; font-size: 13px;">Membro Iniciado</div>
                <div style="color: #c7a7eb; font-size: 10px;">Plano Astral Premium</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    if st.button("🚪 Sair"):
        auth.logout()

# ==================================================
# ROTEAMENTO
# ==================================================
PAGES = {
    "Home": home,
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
    "PDFs": pdfs,
    "Artes": artes
}

page = st.session_state.current_page
if page in PAGES:
    PAGES[page].render()
else:
    home.render()
