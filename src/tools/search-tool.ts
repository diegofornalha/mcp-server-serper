/**
 * Implementação das ferramentas de busca para o servidor MCP.
 */

import { SerperClient } from '../services/serper-client.js';
import { IHealthParams } from '../types/serper';

/**
 * Implementação das ferramentas de busca para o servidor MCP.
 */
export class SerperSearchTools {
  private serperClient: SerperClient;

  /**
   * Inicializa as ferramentas de busca com o cliente Serper.
   *
   * @param client - Instância do cliente da API Serper
   */
  constructor(client: SerperClient) {
    this.serperClient = client;
  }

  /**
   * Executa uma consulta de busca na web.
   *
   * @param params - Parâmetros da consulta
   * @returns Resultados da busca
   */
  async search(params: any): Promise<any> {
    try {
      return await this.serperClient.search(params);
    } catch (e) {
      throw new Error(`SearchTool: failed to search for '${params.q}'. ${e.message}`);
    }
  }

  /**
   * Executa uma operação de raspagem de web.
   *
   * @param params - Parâmetros de raspagem
   * @returns Resultado da raspagem
   */
  async scrape(params: any): Promise<any> {
    try {
      return await this.serperClient.scrape(params);
    } catch (e) {
      throw new Error(`SearchTool: failed to scrape. ${e.message}`);
    }
  }

  /**
   * Executa uma verificação de saúde da API.
   *
   * @param params - Parâmetros da verificação de saúde (opcional)
   * @returns Resultado da verificação de saúde
   */
  async health(params: IHealthParams): Promise<any> {
    try {
      return await this.serperClient.health(params);
    } catch (e) {
      return { status: 'unhealthy', error: e.message };
    }
  }
} 