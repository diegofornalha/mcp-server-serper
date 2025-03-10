// Script para testar a chave da API Serper
import fetch from 'node-fetch';

const SERPER_API_KEY = '8fab4b24ee718778ea9f17114a5cf02781bca5767fe493c3ce772e54327fe514';

async function testSerperAPI() {
  try {
    const response = await fetch('https://google.serper.dev/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': SERPER_API_KEY
      },
      body: JSON.stringify({
        q: 'teste api serper',
        gl: 'br',
        hl: 'pt-br'
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Erro na API Serper: ${response.status} ${response.statusText} - ${errorText}`);
      return;
    }

    const data = await response.json();
    console.log('API Serper funcionando corretamente!');
    console.log('Primeiros resultados:', data.organic ? data.organic.slice(0, 2) : 'Sem resultados orgânicos');
  } catch (error) {
    console.error('Falha ao testar a API Serper:', error);
  }
}

testSerperAPI(); 