# Services 📁

📋 **Sumário**

* [🔍 Visão Geral](#-visão-geral)
* [🧱 Arquitetura](#-arquitetura)
* [🧪 Testes Unitários - `serper-client.test.ts`](#-testes-unitários---serper-clienttestts)
    * [Funcionalidade `buildAdvancedQuery`](#funcionalidade-buildadvancedquery)
    * [Exemplos de Uso](#exemplos-de-uso)
* [🚀 Instalação](#-instalação)
* [💻 Utilização](#-utilização)


🔍 **Visão Geral**

Este diretório contém serviços e utilitários, com foco principal na interação com a API da Serper.  O arquivo `serper-client.test.ts` fornece testes unitários para garantir a funcionalidade correta da construção de consultas avançadas para a API.

🧱 **Arquitetura**

A arquitetura deste componente é simples e focada em fornecer uma interface robusta para construir consultas complexas. A classe `SerperClient` (não incluída neste diretório, mas testada aqui) é responsável por interagir com a API da Serper, e o método `buildAdvancedQuery` é crucial para a construção flexível de strings de consulta.

🧪 **Testes Unitários - `serper-client.test.ts`**

Este arquivo contém testes unitários utilizando um framework de testes (provavelmente Jest) para garantir a qualidade e a funcionalidade do método `buildAdvancedQuery` da classe `SerperClient`.

### Funcionalidade `buildAdvancedQuery`

O método `buildAdvancedQuery` permite a construção de strings de consulta complexas para a API da Serper, suportando diferentes parâmetros, incluindo:

* **Operadores de Busca:** Permite o uso de operadores booleanos (AND, OR, NOT) para refinar as buscas.
* **Frases Exatas:** Permite buscar por frases exatas utilizando aspas.
* **Casos Especiais:** Lida com caracteres especiais e codificação de URL para garantir a integridade das consultas.

### Exemplos de Uso

```typescript
// Exemplo 1: Busca simples
const query = serperClient.buildAdvancedQuery('minha busca');

// Exemplo 2: Busca com operador AND
const query = serperClient.buildAdvancedQuery('termo1 AND termo2');

// Exemplo 3: Busca com frase exata
const query = serperClient.buildAdvancedQuery('"frase exata"');

// Exemplo 4: Busca combinada
const query = serperClient.buildAdvancedQuery('(termo1 OR termo2) AND "frase exata"');
```

Os testes em `serper-client.test.ts` cobrem esses e outros cenários, incluindo casos extremos e tratamento de erros, para garantir a robustez da função.


🚀 **Instalação**

Para utilizar este código, você precisa ter o Node.js e npm (ou yarn) instalados.  Assumindo que a classe `SerperClient` está em um pacote separado, você precisará instalá-lo, provavelmente via npm:

```bash
npm install nome-do-pacote-da-serper-client
```

Também é necessário instalar as dependências de desenvolvimento, incluindo o framework de testes:

```bash
npm install --save-dev jest
```

💻 **Utilização**

Após a instalação, você pode executar os testes unitários com o seguinte comando:

```bash
npm test
```

Para utilizar o método `buildAdvancedQuery` em seu próprio código, importe a classe `SerperClient` e instancie-a:

```typescript
import { SerperClient } from 'nome-do-pacote-da-serper-client';

const serperClient = new SerperClient(apiKey); // Substitua apiKey pela sua chave de API

const queryString = serperClient.buildAdvancedQuery('sua consulta');

// Utilize a queryString para fazer a requisição à API da Serper.
```


Este README fornece uma visão geral e instruções para utilizar os testes e a função `buildAdvancedQuery`. Consulte a documentação da API da Serper para mais detalhes sobre a construção de consultas e as opções disponíveis.