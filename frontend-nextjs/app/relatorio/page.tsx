'use client';

import { useState } from 'react';
import './relatorio.css';

interface BirthData {
    date: string;
    time: string;
    city: string;
    country: string;
}

interface AnalysisResponse {
    name: string;
    birth_data: BirthData;
    map_data: any;
    sections: {
        visao_geral: string;
        triade_principal: string;
        planetas_pessoais: string;
        jupiter_saturno: string;
        meio_ceu: string;
        casas: string;
        aspectos: string;
        pontos_karmicos: string;
        resposta_pergunta?: string;
    };
    question?: string;
}

export default function RelatorioPage() {
    const [formData, setFormData] = useState({
        name: '',
        date: '',
        time: '',
        city: '',
        country: '',
        question: ''
    });

    const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
    const [chartSVG, setChartSVG] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [loadingPDF, setLoadingPDF] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const dateObj = new Date(formData.date);
            const day = String(dateObj.getDate() + 1).padStart(2, '0');
            const month = String(dateObj.getMonth() + 1).padStart(2, '0');
            const year = dateObj.getFullYear();
            const formattedDate = `${day}/${month}/${year}`;

            const response = await fetch('http://localhost:8000/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...formData,
                    date: formattedDate,
                    question: formData.question || null
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao gerar análise');
            }

            const data = await response.json();
            setAnalysis(data);

            // Buscar gráfico SVG
            try {
                const svgResponse = await fetch('http://localhost:8000/generate-chart-svg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: formData.name,
                        date: formattedDate,
                        time: formData.time,
                        city: formData.city,
                        country: formData.country,
                        custom_colors: true
                    })
                });

                if (svgResponse.ok) {
                    const svgText = await svgResponse.text();
                    setChartSVG(svgText);
                }
            } catch (svgError) {
                console.error('Erro ao buscar SVG:', svgError);
                // Não bloquear o relatório se o SVG falhar
            }

        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async () => {
        setLoadingPDF(true);
        try {
            const reportElement = document.querySelector('.report-container');
            if (!reportElement) {
                throw new Error('Conteúdo do relatório não encontrado');
            }

            const clonedElement = reportElement.cloneNode(true) as HTMLElement;
            const controls = clonedElement.querySelector('.controls');
            if (controls) {
                controls.remove();
            }

            const styles = Array.from(document.styleSheets)
                .map(styleSheet => {
                    try {
                        return Array.from(styleSheet.cssRules)
                            .map(rule => rule.cssText)
                            .join('\n');
                    } catch (e) {
                        return '';
                    }
                })
                .join('\n');

            const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>${styles}</style>
        </head>
        <body>
          ${clonedElement.outerHTML}
        </body>
        </html>
      `;

            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ html: htmlContent })
            });

            if (!response.ok) {
                throw new Error('Erro ao gerar PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mapa_astral_${analysis?.name.replace(/\s+/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (err: any) {
            alert(`Erro ao gerar PDF: ${err.message}`);
        } finally {
            setLoadingPDF(false);
        }
    };

    if (analysis) {
        return (
            <div className="report-container">
                <div className="no-print controls">
                    <button onClick={() => setAnalysis(null)} className="btn-back">
                        ← Voltar
                    </button>
                    <button onClick={handleDownloadPDF} disabled={loadingPDF} className="btn-print">
                        {loadingPDF ? 'Gerando PDF...' : '📄 Baixar PDF'}
                    </button>
                </div>

                <div className="cover page-break">
                    <div className="cover-content">
                        <h1 className="cover-title">MAPA ASTRAL</h1>
                        <p className="cover-subtitle">de {analysis.name}</p>
                        <div className="cover-info">
                            <p>{analysis.birth_data.date} às {analysis.birth_data.time}</p>
                            <p>{analysis.birth_data.city}, {analysis.birth_data.country}</p>
                        </div>
                    </div>
                </div>

                {chartSVG && (
                    <div className="section-page page-break">
                        <h2 className="section-title">Mapa Astral</h2>
                        <div className="chart-container" dangerouslySetInnerHTML={{ __html: chartSVG }} />
                    </div>
                )}

                <div className="section-page page-break">
                    <h2 className="section-title">Visão Geral</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.visao_geral }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">A Tríade Principal</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.triade_principal }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">Planetas Pessoais</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.planetas_pessoais }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">Júpiter e Saturno</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.jupiter_saturno }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">O Meio-Céu</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.meio_ceu }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">Casas Astrológicas</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.casas }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">Principais Aspectos</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.aspectos }} />
                </div>

                <div className="section-page page-break">
                    <h2 className="section-title">Pontos Kármicos</h2>
                    <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.pontos_karmicos }} />
                </div>

                {analysis.question && analysis.sections.resposta_pergunta && (
                    <div className="section-page page-break">
                        <h2 className="section-title">Sua Questão Pessoal</h2>
                        <div className="question-box">
                            <p><strong>Pergunta:</strong> {analysis.question}</p>
                        </div>
                        <div className="section-content" dangerouslySetInnerHTML={{ __html: analysis.sections.resposta_pergunta }} />
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="form-container">
            <h1 className="form-title">🔮 Análise Astrológica Completa</h1>
            <p className="form-subtitle">Portal Urano</p>

            <form onSubmit={handleSubmit} className="report-form">
                <div className="form-group">
                    <label htmlFor="name">Nome Completo</label>
                    <input
                        type="text"
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="date">Data de Nascimento</label>
                    <input
                        type="date"
                        id="date"
                        value={formData.date}
                        onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="time">Hora de Nascimento</label>
                    <input
                        type="time"
                        id="time"
                        value={formData.time}
                        onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="city">Cidade</label>
                    <input
                        type="text"
                        id="city"
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        required
                        placeholder="Ex: São Paulo"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="country">País</label>
                    <input
                        type="text"
                        id="country"
                        value={formData.country}
                        onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                        required
                        placeholder="Ex: Brasil"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="question">
                        Pergunta Específica <span className="optional">(Opcional)</span>
                    </label>
                    <textarea
                        id="question"
                        value={formData.question}
                        onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                        placeholder="Existe alguma questão específica que você gostaria de explorar?"
                        rows={4}
                    />
                </div>

                <button type="submit" disabled={loading} className="btn-submit">
                    {loading ? 'Gerando análise...' : 'Gerar Análise'}
                </button>

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}
            </form>
        </div>
    );
}
