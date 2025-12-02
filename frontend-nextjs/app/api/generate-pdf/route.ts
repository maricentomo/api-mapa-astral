import { NextRequest, NextResponse } from 'next/server';
import puppeteer from 'puppeteer';

export async function POST(request: NextRequest) {
    try {
        const { html } = await request.json();

        if (!html) {
            return NextResponse.json(
                { error: 'HTML content is required' },
                { status: 400 }
            );
        }

        // Iniciar Puppeteer
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        // Configurar viewport
        await page.setViewport({
            width: 1200,
            height: 1600
        });

        // Carregar HTML
        await page.setContent(html, {
            waitUntil: 'networkidle0'
        });

        // Gerar PDF
        const pdfBuffer = await page.pdf({
            format: 'A4',
            printBackground: true,
            margin: {
                top: '0mm',
                right: '0mm',
                bottom: '0mm',
                left: '0mm'
            }
        });

        await browser.close();

        // Retornar PDF
        return new NextResponse(pdfBuffer, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': 'attachment; filename="mapa_astral.pdf"'
            }
        });

    } catch (error: any) {
        console.error('Erro ao gerar PDF:', error);
        return NextResponse.json(
            { error: 'Erro ao gerar PDF', details: error.message },
            { status: 500 }
        );
    }
}
