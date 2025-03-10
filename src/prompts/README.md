```markdown
# 🗄️ Gerenciador de Prompts para Pesquisa (prompts)

📋 **Sumário**

- [🔍 Visão Geral](#visão-geral)
- [🚀 Funcionalidades](#funcionalidades)
- [🧱 Estrutura do Código](#estrutura-do-código)
- [⚙️ Instalação](#instalação)
- [💡 Utilização](#utilização)
- [📝 Exemplos de Uso](#exemplos-de-uso)


🔍 **Visão Geral**

Este projeto fornece uma classe `SerperPrompts` em TypeScript para gerenciar e formatar prompts para pesquisa, otimizados para uso com modelos de linguagem.  A classe oferece uma interface simples para acessar e customizar prompts pré-definidos, como "research-topic" e "fact-check", permitindo ajustar parâmetros como tópico, profundidade e foco da pesquisa.

🚀 **Funcionalidades**

- **Gerenciamento de Prompts:** Armazena e organiza prompts para diferentes tipos de pesquisa.
- **Formatação de Prompts:** Formata os prompts com os argumentos fornecidos, preparando-os para envio a um modelo de linguagem.
- **Customização de Pesquisas:** Permite customizar a pesquisa através de argumentos como tópico, profundidade e foco.
- **Expansão Futura:** Design modular que facilita a adição de novos prompts.

🧱 **Estrutura do Código**

O código principal reside no arquivo `index.ts` e define a classe `SerperPrompts`.

- **Classe `SerperPrompts`:**
    - Contém um objeto interno com os prompts pré-definidos.
    - O método `getPrompt(promptKey, args)` recupera e formata o prompt especificado por `promptKey` usando os argumentos fornecidos em `args`.

⚙️ **Instalação**

1. Certifique-se de ter o Node.js e npm (ou yarn) instalados.
2. Navegue até o diretório do projeto no terminal.
3. Instale as dependências:

```bash
npm install
# ou
yarn install
```

💡 **Utilização**

1. Importe a classe `SerperPrompts` no seu código:

```typescript
import { SerperPrompts } from './index';
```

2. Crie uma instância da classe:

```typescript
const prompts = new SerperPrompts();
```

3. Utilize o método `getPrompt` para obter o prompt formatado:

```typescript
const researchPrompt = prompts.getPrompt('research-topic', { topic: 'Inteligência Artificial', depth: 'avançado', focus: 'ética' });
console.log(researchPrompt);

const factCheckPrompt = prompts.getPrompt('fact-check', { statement: 'A Terra é plana.', sources: 'científicos' });
console.log(factCheckPrompt);
```

📝 **Exemplos de Uso**

**Exemplo 1: Pesquisa de Tópico:**

```typescript
const prompts = new SerperPrompts();
const prompt = prompts.getPrompt('research-topic', { topic: 'JavaScript', depth: 'básico', focus: 'sintaxe' });

// Exemplo de saída (o prompt real depende da implementação em index.ts):
// "Pesquise sobre JavaScript em nível básico, com foco na sintaxe."
console.log(prompt); 
```

**Exemplo 2: Verificação de Fatos:**

```typescript
const prompts = new SerperPrompts();
const prompt = prompts.getPrompt('fact-check', { statement: 'O café previne o câncer.', sources: 'médicos' });

// Exemplo de saída (o prompt real depende da implementação em index.ts):
// "Verifique a afirmação: 'O café previne o câncer.' usando fontes médicas."
console.log(prompt);
```


Este README fornece uma visão geral e instruções para usar o Gerenciador de Prompts. Explore os exemplos e adapte-os às suas necessidades.
```