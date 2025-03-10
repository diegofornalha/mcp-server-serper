// Script para testar a SerpAPI como alternativa à Serper API
const SerpApi = require('google-search-results-nodejs');
const search = new SerpApi.GoogleSearch();

// IMPORTANTE: Você precisará obter uma chave de API em https://serpapi.com/users/sign_up
const API_KEY = "sua_chave_api_aqui"; // Substitua pela sua chave SerpAPI

// Função para realizar uma busca no Google
async function testGoogleSearch() {
  try {
    const params = {
      q: "agentes de inteligência artificial",
      location: "Brazil",
      hl: "pt",
      gl: "br",
      google_domain: "google.com.br",
      api_key: API_KEY
    };

    // Retorna uma Promise
    const response = await new Promise((resolve, reject) => {
      search.json(params, (data) => {
        resolve(data);
      });
    });

    console.log("Busca realizada com sucesso!");
    console.log("Título da página:", response.search_metadata?.title);
    console.log("Total de resultados:", response.search_information?.total_results);
    
    if (response.organic_results && response.organic_results.length > 0) {
      console.log("\nPrimeiros 3 resultados orgânicos:");
      response.organic_results.slice(0, 3).forEach((result, index) => {
        console.log(`\n[${index + 1}] ${result.title}`);
        console.log(`Link: ${result.link}`);
        console.log(`Snippet: ${result.snippet}`);
      });
    }
    
    if (response.knowledge_graph) {
      console.log("\nKnowledge Graph:");
      console.log(`Título: ${response.knowledge_graph.title}`);
      console.log(`Descrição: ${response.knowledge_graph.description}`);
    }

  } catch (error) {
    console.error("Erro ao realizar busca:", error);
  }
}

// Função para realizar scraping de uma página web
async function testScraping(url) {
  try {
    const params = {
      api_key: API_KEY,
      url: url,
      // Parâmetros adicionais para scraping
      render: true, // Renderiza JavaScript
      output: "json" // Formato de saída
    };

    // Retorna uma Promise
    const response = await new Promise((resolve, reject) => {
      // Usando o endpoint html da SerpAPI
      search.html(params, (data) => {
        resolve(data);
      });
    });

    console.log("Scraping realizado com sucesso!");
    console.log("Conteúdo HTML:", response.substring(0, 300) + "..."); // Exibe apenas o início
    
  } catch (error) {
    console.error("Erro ao realizar scraping:", error);
  }
}

// Executar os testes
async function runTests() {
  console.log("=== Teste de Busca Google ===");
  await testGoogleSearch();
  
  console.log("\n\n=== Teste de Scraping ===");
  await testScraping("https://pt.wikipedia.org/wiki/Agente_inteligente_(inteligência_artificial)");
}

// Verificar se a chave API foi configurada
if (API_KEY === "sua_chave_api_aqui") {
  console.error("ERRO: Você precisa configurar sua chave API da SerpAPI antes de executar este script.");
  console.error("Obtenha uma chave em https://serpapi.com/users/sign_up");
} else {
  runTests();
} 