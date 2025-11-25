# Portal Urano - Versão HTML Pura

Esta é a versão HTML/CSS/JavaScript pura do Portal Urano, **sem nenhuma dependência do Streamlit**.

## 📁 Estrutura de Arquivos

```
frontend/
├── index.html       # Estrutura HTML principal
├── styles.css       # Estilos CSS
├── script.js        # JavaScript para interatividade
└── README.md        # Este arquivo
```

## 🚀 Como Usar

### Opção 1: Abrir Diretamente no Navegador

1. Navegue até a pasta `frontend`:
   ```bash
   cd c:\Users\maric\OneDrive\docs_2021\projeto_astro\api-mapa-astral\frontend
   ```

2. Clique duas vezes em `index.html` ou abra com seu navegador favorito

### Opção 2: Usar um Servidor Local

Para melhor desenvolvimento, use um servidor local:

```bash
# Usando Python
python -m http.server 8080

# Ou usando Node.js (se tiver npx instalado)
npx serve .
```

Depois acesse: `http://localhost:8080`

## 🎨 Recursos Implementados

### ✅ O que está funcionando:

- Layout completo com sidebar
- Navegação entre páginas (estrutura pronta)
- Banner com textura no topo
- Imagem da elfa
- Botões de ação rápida
- Campo de mensagem
- Design responsivo
- Efeitos hover e transições
- Menu mobile (hamburger menu em telas pequenas)

### 📝 O que precisa ser adicionado:

- Integração com backend/API
- Conteúdo das outras páginas (Mapa Astral, Trânsitos, etc.)
- Sistema de autenticação
- Processamento de mensagens via IA

## 🔄 Migração para Next.js

### Passo 1: Criar projeto Next.js

```bash
npx create-next-app@latest portal-urano-nextjs
cd portal-urano-nextjs
```

### Passo 2: Estrutura de pastas recomendada

```
portal-urano-nextjs/
├── app/
│   ├── layout.tsx           # Layout principal (sidebar)
│   ├── page.tsx             # Home page
│   ├── mapa-astral/
│   │   └── page.tsx
│   ├── transitos/
│   │   └── page.tsx
│   └── ...outras páginas
├── components/
│   ├── Sidebar.tsx
│   ├── MessageInput.tsx
│   └── ...outros componentes
├── public/
│   ├── elfa_corpo.png
│   ├── textura.png
│   └── logo_olho_final.jpg
└── styles/
    └── globals.css
```

### Passo 3: Converter HTML para React Components

#### Exemplo: Sidebar Component

```typescript
// components/Sidebar.tsx
'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function Sidebar() {
  const [activePage, setActivePage] = useState('mapa-astral');

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Image
          src="/logo_olho_final.jpg"
          alt="Portal Urano"
          width={120}
          height={120}
        />
      </div>
      {/* ...resto do código */}
    </aside>
  );
}
```

#### Exemplo: Home Page

```typescript
// app/page.tsx
import Image from 'next/image';
import MessageInput from '@/components/MessageInput';

export default function Home() {
  return (
    <div className="home-page">
      <div className="texture-banner">
        <Image
          src="/textura.png"
          alt="Textura"
          fill
          style={{ objectFit: 'cover' }}
        />
      </div>
      {/* ...resto do conteúdo */}
    </div>
  );
}
```

### Passo 4: Copiar estilos

1. Copie o conteúdo de `styles.css` para `styles/globals.css`
2. Ou use CSS Modules / Tailwind CSS para melhor organização

### Passo 5: Adicionar funcionalidades Next.js

- **API Routes**: Para backend (`app/api/`)
- **Server Components**: Para dados estáticos
- **Client Components**: Para interatividade (`'use client'`)
- **Images**: Otimização automática com `next/image`
- **Routing**: Sistema de rotas baseado em arquivos

## 🌐 Diferenças Principais: HTML Puro vs Next.js

| Recurso | HTML Puro | Next.js |
|---------|-----------|---------|
| Navegação | JavaScript manual | File-based routing |
| Imagens | `<img>` tag | `<Image>` otimizado |
| Estado | JavaScript vanilla | React Hooks |
| API | Fetch direto | API Routes + Server Actions |
| SEO | Básico | SSR/SSG otimizado |
| Performance | Depende do código | Otimizado automaticamente |

## 🔧 Próximos Passos Recomendados

1. **Testar a versão HTML** - Abra `index.html` e verifique se tudo funciona
2. **Adicionar mais páginas** - Crie o conteúdo das outras seções
3. **Conectar com backend** - Integre com sua API Python existente
4. **Migrar para Next.js** - Quando estiver satisfeito com o design
5. **Deploy** - Vercel, Netlify, ou qualquer hosting

## 📸 Assets Necessários

Certifique-se de que estes arquivos existem na pasta pai:

- `../elfa_corpo.png`
- `../textura.png`
- `../logo_olho_final.jpg`

Se não existirem, ajuste os caminhos no `index.html`.

## 💡 Dicas

- Use **Ctrl + Shift + I** no navegador para abrir as DevTools
- Teste em diferentes tamanhos de tela (responsivo)
- O console mostrará logs das interações
- Modifique `script.js` para customizar comportamentos

---

**Pronto para Next.js!** 🚀 Todos os componentes estão prontos para serem convertidos em React Components.
