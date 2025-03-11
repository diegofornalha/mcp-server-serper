# 🔍 Ferramentas de Busca com Serper (tools)

Este repositório contém a ferramenta `search-tool.ts` que facilita a interação com a API Serper para realizar buscas, raspagem de dados, análise de SERP, pesquisa de palavras-chave e análise de concorrentes.

📋 **Sumário**

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Tratamento de Erros](#-tratamento-de-erros)


## 🔍 Visão Geral

A classe `SerperSearchTools` encapsula um cliente da API Serper, simplificando o processo de realizar diversas operações relacionadas a mecanismos de busca. Ela oferece métodos para realizar buscas na web, extrair dados de páginas web (raspagem), analisar resultados de pesquisa (SERP), pesquisar palavras-chave e analisar concorrentes.

## ✨ Funcionalidades

A classe `SerperSearchTools` fornece as seguintes funcionalidades:

- **Busca na Web:** Realiza buscas na web usando a API Serper.
- **Raspagem de Dados:** Extrai dados específicos de páginas web.
- **Análise de SERP:** Analisa os resultados da página de resultados do mecanismo de busca (SERP).
- **Pesquisa de Palavras-Chave:** Realiza pesquisa de palavras-chave relevantes.
- **Análise de Concorrentes:** Analisa os concorrentes em relação a determinadas palavras-chave.

## 🧩 Requisitos

- Node.js e npm (ou yarn) instalados.
- Uma chave de API válida para a Serper.
- TypeScript instalado (recomendado).

## 💾 Instalação

1. Clone este repositório:

```bash
git clone <URL_DO_REPOSITÓRIO>
```

2. Navegue até o diretório `tools`:

```bash
cd tools
```

3. Instale as dependências:

```bash
npm install
# ou
yarn install
```

## 🚀 Uso

1. Importe a classe `SerperSearchTools` no seu projeto:

```typescript
import { SerperSearchTools } from './search-tool';
```

2. Crie uma instância da classe, fornecendo sua chave de API Serper:

```typescript
const serper = new SerperSearchTools('SUA_CHAVE_API_SERPER');
```

3. Utilize os métodos da classe para realizar as operações desejadas (veja exemplos na seção [Exemplos de Uso](#-exemplos-de-uso)).


## ⌨️ Exemplos de Uso

```typescript
// Realizar uma busca na web
const results = await serper.search('Como fazer bolo de chocolate');
console.log(results);

// Raspar dados de uma URL específica (requer configuração adicional na API Serper)
const scrapedData = await serper.scrape('https://www.exemplo.com.br', {
  // ... opções de raspagem
});
console.log(scrapedData);

// Analisar a SERP para uma palavra-chave
const serpAnalysis = await serper.analyzeSerp('bolo de chocolate');
console.log(serpAnalysis);


// Pesquisa de palavras-chave (requer funcionalidades específicas na API Serper)
const keywords = await serper.keywordResearch('receita');
console.log(keywords);


// Análise de concorrentes (requer funcionalidades específicas na API Serper)
const competitors = await serper.analyzeCompetitors('bolo de chocolate', ['concorrente1.com', 'concorrente2.com']);
console.log(competitors);
```

## ⚠️ Tratamento de Erros

A classe `SerperSearchTools` inclui tratamento de erros básico para lidar com problemas na comunicação com a API Serper.  Em caso de erro, um objeto de erro será lançado.  É importante capturar esses erros e tratá-los adequadamente em sua aplicação:

```typescript
try {
  const results = await serper.search('alguma query');
  console.log(results);
} catch (error) {
  console.error('Ocorreu um erro:', error);
  // Implemente a lógica de tratamento de erros aqui
}

```