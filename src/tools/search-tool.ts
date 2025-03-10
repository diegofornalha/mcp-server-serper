import { ISerperClient } from "../services/serper-client.js";
import {
  ISearchParams,
  ISearchResult,
  IScrapeParams,
  IScrapeResult,
  IHealthParams,
  IHealthResult,
  IAnalyzeSerpParams, 
  IAnalyzeSerpResult,
  IResearchKeywordsParams,
  IResearchKeywordsResult,
  IAnalyzeCompetitorsParams,
  IAnalyzeCompetitorsResult
} from "../types/serper.js";

/**
 * Search tool implementation for MCP server.
 */
export class SerperSearchTools {
  private serperClient: ISerperClient;

  /**
   * Initialize search tool with Serper client.
   * @param client - Serper API client instance
   */
  constructor(client: ISerperClient) {
    this.serperClient = client;
  }

  /**
   * Execute a web search query.
   * @param query - Search query string
   * @param location - Optional region code for search results
   * @param language - Optional language code for search results
   * @returns Promise resolving to search results
   */
  async search(params: ISearchParams): Promise<ISearchResult> {
    try {
      const result = await this.serperClient.search(params);
      return result;
    } catch (error) {
      throw new Error(
        `SearchTool: failed to search for "${params.q}". ${error}`
      );
    }
  }

  /**
   * Execute a web scrape operation.
   * @param params - Scrape parameters
   * @returns Promise resolving to scrape result
   */
  async scrape(params: IScrapeParams): Promise<IScrapeResult> {
    try {
      const result = await this.serperClient.scrape(params);
      return result;
    } catch (error) {
      throw new Error(`SearchTool: failed to scrape. ${error}`);
    }
  }

  /**
   * Execute a health check.
   * @returns Promise resolving to health status
   */
  async health(params?: IHealthParams): Promise<IHealthResult> {
    try {
      const result = await this.serperClient.health(params);
      return result;
    } catch (error) {
      throw new Error(`SearchTool: health check failed. ${error}`);
    }
  }

  /**
   * Analyze SERP for a query.
   * @param params - SERP analysis parameters
   * @returns Promise resolving to SERP analysis
   */
  async analyzeSERP(params: IAnalyzeSerpParams): Promise<IAnalyzeSerpResult> {
    try {
      const result = await this.serperClient.analyzeSERP(params);
      return result;
    } catch (error) {
      throw new Error(`SearchTool: failed to analyze SERP for "${params.query}". ${error}`);
    }
  }

  /**
   * Research keywords related to a seed keyword.
   * @param params - Keyword research parameters
   * @returns Promise resolving to keyword research data
   */
  async researchKeywords(params: IResearchKeywordsParams): Promise<IResearchKeywordsResult> {
    try {
      const result = await this.serperClient.researchKeywords(params);
      return result;
    } catch (error) {
      throw new Error(`SearchTool: failed to research keywords for "${params.keyword}". ${error}`);
    }
  }

  /**
   * Analyze competitors for a domain/keyword.
   * @param params - Competitor analysis parameters
   * @returns Promise resolving to competitor analysis data
   */
  async analyzeCompetitors(params: IAnalyzeCompetitorsParams): Promise<IAnalyzeCompetitorsResult> {
    try {
      const result = await this.serperClient.analyzeCompetitors(params);
      return result;
    } catch (error) {
      throw new Error(`SearchTool: failed to analyze competitors for "${params.domain}". ${error}`);
    }
  }
}
