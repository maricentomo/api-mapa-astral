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
st.set_page_config(page_title="Portal Astro IA", page_icon="🔮", layout="wide")

# ==================================================
# AUTENTICAÇÃO
# ==================================================
if not auth.login_page():
    st.stop()

# ==================================================
# BARRA LATERAL (NAVEGAÇÃO)
# ==================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2647/2647282.png", width=100)
    st.title("Portal Astro IA")
    st.write(f"Bem-vindo(a)!")
    
    st.divider()
    
    st.subheader("🔮 Astrologia")
    page_astrologia = st.radio(
        "Selecione uma ferramenta:",
        [
            "Mapa Astral", 
            "Revolução Solar", 
            "Astrologia Vocacional", 
            "Astrologia Infantil", 
            "Sinastria", 
            "Trânsitos"
        ],
        index=0,
        key="nav_astrologia"
    )
    
    st.divider()
    
    st.subheader("🔢 Matriz do Destino")
    page_matriz = st.radio(
        "Selecione uma ferramenta:",
        [
            "Matriz do Destino", 
            "Matriz Compatibilidade", 
            "Matriz Infantil"
        ],
        index=0,
        key="nav_matriz"
    )
    
    st.divider()
    
    st.subheader("📚 Conteúdos")
    page_conteudo = st.radio(
        "Selecione uma área:",
        ["Vídeos", "PDFs"],
        index=0,
        key="nav_conteudo"
    )
    
    st.divider()
    if st.button("Sair"):
        auth.logout()

# ==================================================
# ROTEAMENTO
# ==================================================

# Lógica simples de roteamento: O último radio clicado define a página?
# O Streamlit re-executa o script inteiro a cada interação.
# Precisamos saber qual foi o ÚLTIMO radio alterado ou usar um selectbox único se possível.
# Mas o usuário pediu "na lateral tera o agente pra mapa astral... e também para matriz... alem das areas de videos".
# Para simplificar e evitar conflitos de radios, vamos usar um menu único ou lógica de prioridade.
# Uma abordagem melhor para sidebar complexa é usar st.navigation (novo no Streamlit) ou um único radio/selectbox se possível.
# Mas para atender o pedido visualmente separado, vamos tentar inferir a navegação.

# Vamos usar um Session State para controlar a página ativa, atualizada pelos callbacks dos radios?
# Ou simplesmente um único st.radio com headers simulados? 
# Vamos tentar uma abordagem com st.sidebar.selectbox para "Categoria" e depois "Ferramenta"?
# O usuário pediu "na lateral tera...".
# Vamos fazer um menu único com categorias visuais.

# Refazendo a sidebar para ser mais funcional e menos confusa:

# Limpar a sidebar anterior (visualmente, no código acima eu vou substituir)
pass

# ==================================================
# BARRA LATERAL (NAVEGAÇÃO REVISADA)
# ==================================================
# Vamos usar um selectbox principal ou botões.
# Botões são bons para "Abas".
# Vamos usar st.sidebar.radio mas com todas as opções, formatadas.

# Opções
PAGES = {
    "Mapa Astral": mapa_astral,
    "Revolução Solar": revolucao_solar,
    "Astrologia Vocacional": vocacional,
    "Astrologia Infantil": infantil,
    "Sinastria": sinastria,
    "Trânsitos": transitos,
    "Matriz do Destino": matriz_destino,
    "Matriz Compatibilidade": matriz_compatibilidade,
    "Matriz Infantil": matriz_infantil,
    "Vídeos": videos,
    "PDFs": pdfs
}

with st.sidebar:
    # st.image("https://cdn-icons-png.flaticon.com/512/2647/2647282.png", width=100)
    st.title("Navegação")
    
    st.markdown("### 🔮 Astrologia")
    selection_astro = st.selectbox(
        "Ferramentas Astrológicas",
        ["Mapa Astral", "Revolução Solar", "Astrologia Vocacional", "Astrologia Infantil", "Sinastria", "Trânsitos"],
        index=0
    )

    st.markdown("### 🔢 Matriz do Destino")
    selection_matriz = st.selectbox(
        "Ferramentas Matriz",
        ["Matriz do Destino", "Matriz Compatibilidade", "Matriz Infantil"],
        index=0
    )

    st.markdown("### 📚 Conteúdos")
    selection_conteudo = st.selectbox(
        "Materiais",
        ["Vídeos", "PDFs"],
        index=0
    )
    
    # O problema de 3 selectboxes é: qual deles está ativo?
    # Vamos usar um radio único com headers simulados usando captions ou markdown, mas o radio não suporta headers no meio das opções nativamente.
    # Solução: Um único radio com todas as opções.
    
    st.divider()
    # Resetando para usar um único menu para evitar confusão de estado
    
    menu_selection = st.radio(
        "Ir para:",
        [
            "--- ASTROLOGIA ---",
            "Mapa Astral",
            "Revolução Solar",
            "Astrologia Vocacional",
            "Astrologia Infantil",
            "Sinastria",
            "Trânsitos",
            "--- MATRIZ DO DESTINO ---",
            "Matriz do Destino",
            "Matriz Compatibilidade",
            "Matriz Infantil",
            "--- CONTEÚDOS ---",
            "Vídeos",
            "PDFs"
        ]
    )
    
    if st.button("Sair"):
        auth.logout()

# Lógica de renderização baseada no menu único
if menu_selection in PAGES:
    PAGES[menu_selection].render()
elif menu_selection.startswith("---"):
    st.info("Selecione uma opção no menu lateral.")
else:
    # Fallback
    mapa_astral.render()
