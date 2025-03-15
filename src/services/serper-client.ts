/**
 * Cliente para interagir com a API Serper.
 */

import fetch from 'node-fetch';
import { IHealthParams } from '../types/serper.js';

/**
 * Cliente para interação com a API Serper.
 */
export class SerperClient {
  private apiKey: string;
  private baseUrl: string;

  /**
   * Inicializa o cliente da API Serper.
   *
   * @param apiKey - Chave da API Serper para autenticação
   * @param baseUrl - URL base para a API Serper (opcional)
   */
  constructor(apiKey: string, baseUrl: string = 'google.serper.dev') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  /**
   * Faz uma requisição para a API Serper.
   *
   * @param method - Método HTTP (GET, POST, etc.)
   * @param endpoint - Endpoint da API
   * @param payload - Dados a serem enviados na requisição
   * @returns Resposta da API como um objeto
   */
  private async _makeRequest(method: string, endpoint: string, payload: any): Promise<any> {
    try {
      const url = `https://${this.baseUrl}${endpoint}`;
      const headers = {
        'X-API-KEY': this.apiKey,
        'Content-Type': 'application/json',
      };

      const response = await fetch(url, {
        method,
        headers,
        body: payload ? JSON.stringify(payload) : undefined,
      });

      const data = await response.json();

      if (!response.ok) {
        console.error(`Serper API error: ${response.status} ${JSON.stringify(data)}`);
        throw new Error(`Serper API error: ${response.status} ${JSON.stringify(data)}`);
      }

      return data;
    } catch (e) {
      console.error(`Error making request to Serper API: ${e}`);
      throw e;
    }
  }

  /**
   * Realiza uma busca web usando a API Serper.
   *
   * @param params - Parâmetros de busca
   * @returns Resultados da busca
   */
  async search(params: any): Promise<any> {
    try {
      // Prepara o payload para a API Serper
      const payload: any = {
        q: params.q,
        gl: params.gl || 'us',
        hl: params.hl || 'en',
        autocorrect: params.autocorrect ?? true,
      };

      // Adiciona parâmetros opcionais se fornecidos
      if ('location' in params) {
        payload.location = params.location;
      }
      if ('num' in params) {
        payload.num = params.num;
      }
      if ('page' in params) {
        payload.page = params.page;
      }

      // Processa operadores de busca avançada
      const operators = [
        'site', 'filetype', 'inurl', 'intitle', 'related',
        'cache', 'before', 'after', 'exact', 'exclude', 'or', 'tbs'
      ];
      
      for (const op of operators) {
        if (op in params && params[op]) {
          payload[op] = params[op];
        }
      }

      return this._makeRequest('POST', '/search', payload);
    } catch (e) {
      console.error(`Error in search: ${e}`);
      throw new Error(`Failed to search for '${params.q}': ${e}`);
    }
  }

  /**
   * Realiza uma operação de raspagem de web.
   *
   * @param params - Parâmetros de raspagem
   * @returns Resultado da raspagem
   */
  async scrape(params: any): Promise<any> {
    try {
      return this._makeRequest('POST', '/scrape', { url: params.url, includeMarkdown: params.includeMarkdown });
    } catch (e) {
      console.error(`Error in scrape: ${e}`);
      throw new Error(`Failed to scrape URL '${params.url}': ${e}`);
    }
  }

  /**
   * Realiza uma verificação de saúde da API.
   *
   * @param params - Parâmetros da verificação de saúde (opcional)
   * @returns Resultado da verificação de saúde
   */
  async health(_params: IHealthParams): Promise<any> {
    try {
      // Esta é uma chamada fictícia para verificar se a API está respondendo
      return this._makeRequest('GET', '/health', null);
    } catch (e: any) {
      // Se a chamada falhar, retornamos um status unhealthy
      return { status: 'unhealthy', error: e.message };
    }
  }
} 