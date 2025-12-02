"""
Template HTML para geração de PDF do Mapa Astral
Portal Urano
"""

def generate_pdf_html(name: str, analysis: dict, map_data: dict) -> str:
    """
    Gera o HTML completo do PDF com análise astrológica
    
    Args:
        name: Nome do cliente
        analysis: Dicionário com as 9 seções da análise
        map_data: Dados do mapa astral calculado
    
    Returns:
        String com HTML completo
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Mapa Astral - {name}</title>
        <style>
            @page {{
                size: A4;
                margin: 0;
            }}
            
            body {{
                font-family: 'Georgia', serif;
                margin: 0;
                padding: 0;
                color: #1a1a1a;
            }}
            
            /* CAPA */
            .cover {{
                page-break-after: always;
                height: 297mm;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
                overflow: hidden;
            }}
            
            .cover::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 80px;
                background: url('assets/pdf/barra_topo.png') repeat-x center;
                background-size: contain;
            }}
            
            .cover::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 80px;
                background: url('assets/pdf/barra_rodape.png') repeat-x center;
                background-size: contain;
            }}
            
            .cover-title {{
                font-size: 48px;
                color: #f5e6d3;
                margin: 40px 0 20px 0;
                font-family: 'Didot', 'Bodoni MT', serif;
                letter-spacing: 2px;
            }}
            
            .cover-subtitle {{
                font-size: 24px;
                color: #f5e6d3;
                margin: 10px 0;
                opacity: 0.9;
            }}
            
            .zodiac-wheel {{
                width: 400px;
                height: 400px;
                margin: 30px 0;
            }}
            
            /* PÁGINAS INTERNAS */
            .page {{
                page-break-after: always;
                padding: 60px 80px;
                background: #f5e6d3;
                min-height: 297mm;
                position: relative;
            }}
            
            .page::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 60px;
                background: url('assets/pdf/barra_lateral.png') repeat-y left center;
                background-size: contain;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #8B5A9E;
            }}
            
            .logo {{
                width: 50px;
                height: 50px;
            }}
            
            .portal-name {{
                color: #8B5A9E;
                font-size: 14px;
                font-weight: bold;
            }}
            
            h1 {{
                color: #8B5A9E;
                font-size: 32px;
                margin: 30px 0 20px 0;
                font-family: 'Didot', serif;
                text-align: center;
            }}
            
            h2 {{
                color: #8B5A9E;
                font-size: 24px;
                margin: 30px 0 15px 0;
                font-family: 'Didot', serif;
            }}
            
            h3 {{
                color: #5DADE2;
                font-size: 18px;
                margin: 20px 0 10px 0;
            }}
            
            p {{
                line-height: 1.8;
                text-align: justify;
                margin: 15px 0;
                font-size: 11pt;
            }}
            
            .section {{
                margin: 30px 0;
            }}
            
            .footer {{
                position: absolute;
                bottom: 30px;
                left: 80px;
                right: 80px;
                text-align: center;
                font-size: 10px;
                color: #666;
                border-top: 1px solid #ccc;
                padding-top: 10px;
            }}
            
            .page-number {{
                float: right;
            }}
            
            ul {{
                margin: 10px 0;
                padding-left: 30px;
            }}
            
            li {{
                margin: 8px 0;
                line-height: 1.6;
            }}
            
            strong {{
                color: #8B5A9E;
            }}
        </style>
    </head>
    <body>
        <!-- CAPA -->
        <div class="cover">
            <img src="assets/pdf/roda_zodiacal.png" class="zodiac-wheel" alt="Roda Zodiacal">
            <h1 class="cover-title">Mapa Astral</h1>
            <p class="cover-subtitle">de {name}</p>
        </div>
        
        <!-- PÁGINA 1: VISÃO GERAL -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Visão Geral</h1>
            
            <div class="section">
                {analysis.get('visao_geral', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">1</span>
            </div>
        </div>
        
        <!-- PÁGINA 2: TRÍADE PRINCIPAL -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>A Tríade Principal</h1>
            
            <div class="section">
                {analysis.get('triade_principal', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">2</span>
            </div>
        </div>
        
        <!-- PÁGINA 3: PLANETAS PESSOAIS -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Planetas Pessoais</h1>
            
            <div class="section">
                {analysis.get('planetas_pessoais', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">3</span>
            </div>
        </div>
        
        <!-- PÁGINA 4: JÚPITER E SATURNO -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Júpiter e Saturno</h1>
            
            <div class="section">
                {analysis.get('jupiter_saturno', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">4</span>
            </div>
        </div>
        
        <!-- PÁGINA 5: MEIO-CÉU -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>O Meio-Céu: Chamado Vocacional</h1>
            
            <div class="section">
                {analysis.get('meio_ceu', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">5</span>
            </div>
        </div>
        
        <!-- PÁGINA 6: CASAS ASTROLÓGICAS -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Casas Astrológicas</h1>
            
            <div class="section">
                {analysis.get('casas', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">6</span>
            </div>
        </div>
        
        <!-- PÁGINA 7: ASPECTOS -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Principais Aspectos</h1>
            
            <div class="section">
                {analysis.get('aspectos', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">7</span>
            </div>
        </div>
        
        <!-- PÁGINA 8: PONTOS KÁRMICOS -->
        <div class="page">
            <div class="header">
                <img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano">
                <span class="portal-name">PORTAL URANO</span>
            </div>
            
            <h1>Pontos Kármicos</h1>
            
            <div class="section">
                {analysis.get('pontos_karmicos', '<p>Análise em processamento...</p>')}
            </div>
            
            <div class="footer">
                <span>portalurano.com.br</span>
                <span class="page-number">8</span>
            </div>
        </div>
        
        <!-- PÁGINA 9: RESPOSTA À PERGUNTA (se houver) -->
        {'<div class="page"><div class="header"><img src="assets/pdf/logo_olho.png" class="logo" alt="Portal Urano"><span class="portal-name">PORTAL URANO</span></div><h1>Sua Questão Pessoal</h1><div class="section">' + analysis.get('resposta_pergunta', '') + '</div><div class="footer"><span>portalurano.com.br</span><span class="page-number">9</span></div></div>' if analysis.get('resposta_pergunta') else ''}
        
    </body>
    </html>
    """
    
    return html
