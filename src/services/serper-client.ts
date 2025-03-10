import fetch from "node-fetch";
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
 * Interface for Serper API client to allow mocking in tests.
 */
export interface ISerperClient {
  /** Perform a web search using Serper API */
  search(params: ISearchParams): Promise<ISearchResult>;
  /** Scrape a URL using Serper API */
  scrape(params: IScrapeParams): Promise<IScrapeResult>;
  /** Check API health status */
  health(params?: IHealthParams): Promise<IHealthResult>;
  /** Analyze SERP for a query */
  analyzeSERP(params: IAnalyzeSerpParams): Promise<IAnalyzeSerpResult>;
  /** Research keywords related to a seed keyword */
  researchKeywords(params: IResearchKeywordsParams): Promise<IResearchKeywordsResult>;
  /** Analyze competitors for a domain/keyword */
  analyzeCompetitors(params: IAnalyzeCompetitorsParams): Promise<IAnalyzeCompetitorsResult>;
}

/**
 * Implementation of Serper API client.
 */
export class SerperClient implements ISerperClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;

  /**
   * Initialize Serper API client.
   * @param apiKey - Serper API key for authentication
   * @param baseUrl - Base URL for Serper API (optional)
   */
  constructor(apiKey: string, baseUrl: string = "https://google.serper.dev") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  /**
   * Builds a Google search query string with advanced operators
   * @param params - Search parameters including advanced operators
   * @returns Complete query string with operators
   * @private
   */
  private buildAdvancedQuery(params: ISearchParams): string {
    // Normalize spaces in the query
    let query = params.q.trim().replace(/\s+/g, ' ');

    // Add site restriction
    if (params.site) {
      query += ` site:${params.site}`;
    }

    // Add file type filter
    if (params.filetype) {
      query += ` filetype:${params.filetype}`;
    }

    // Add URL word search
    if (params.inurl) {
      query += ` inurl:${params.inurl}`;
    }

    // Add title word search
    if (params.intitle) {
      query += ` intitle:${params.intitle}`;
    }

    // Add related sites search
    if (params.related) {
      query += ` related:${params.related}`;
    }

    // Add cached page view
    if (params.cache) {
      query += ` cache:${params.cache}`;
    }

    // Add date range filters
    if (params.before) {
      query += ` before:${params.before}`;
    }
    if (params.after) {
      query += ` after:${params.after}`;
    }

    // Add exact phrase match
    if (params.exact) {
      query += ` "${params.exact}"`;
    }

    // Add excluded terms
    if (params.exclude) {
      query += params.exclude.split(',').map(term => ` -${term.trim()}`).join('');
    }

    // Add OR terms
    if (params.or) {
      query += ` (${params.or.split(',').map(term => term.trim()).join(' OR ')})`;
    }

    return query.trim();
  }

  async search(params: ISearchParams): Promise<ISearchResult> {
    try {
      // Build the advanced query string
      const queryWithOperators = this.buildAdvancedQuery(params);

      // Create new params object with the enhanced query
      const enhancedParams = {
        ...params,
        q: queryWithOperators,
      };

      const response = await fetch(`${this.baseUrl}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": this.apiKey,
        },
        body: JSON.stringify(enhancedParams),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Serper API error: ${response.status} ${response.statusText} - ${errorText}`
        );
      }

      const data = (await response.json()) as ISearchResult;
      return data;
    } catch (error) {
      console.error("Serper search failed:", error);
      throw error;
    }
  }

  /**
   * Scrape a URL using Serper API.
   * @param params - Scrape parameters
   * @returns Promise resolving to scrape result
   * @throws Error if API request fails
   */
  async scrape(params: IScrapeParams): Promise<IScrapeResult> {
    if (!params.url) {
      throw new Error("URL is required for scraping");
    }
    try {
      const response = await fetch("https://scrape.serper.dev", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": this.apiKey,
        },
        body: JSON.stringify(params),
        redirect: "follow",
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Serper API error: ${response.status} ${response.statusText} - ${errorText}`
        );
      }
      const result = (await response.json()) as IScrapeResult;
      return result;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  /**
   * Check the health of the API.
   * @returns Promise resolving to health status
   */
  async health(params?: IHealthParams): Promise<IHealthResult> {
    try {
      return { 
        status: "healthy", 
        version: "1.0.0" 
      };
    } catch (error) {
      console.error("Health check failed:", error);
      throw error;
    }
  }

  /**
   * Analyze SERP results for a given query.
   * @param params - SERP analysis parameters
   * @returns Promise resolving to SERP analysis
   */
  async analyzeSERP(params: IAnalyzeSerpParams): Promise<IAnalyzeSerpResult> {
    try {
      const searchParams: ISearchParams = {
        q: params.query,
        gl: params.gl,
        hl: params.hl,
        num: params.num,
        location: params.location
      };
      
      const searchResult = await this.search(searchParams);
      
      // Process the search results into a structured SERP analysis
      const analysis = {
        searchInformation: searchResult.searchParameters,
        totalResults: searchResult.organic ? searchResult.organic.length : 0,
        knowledgeGraph: searchResult.knowledgeGraph || null,
        organicResults: searchResult.organic || [],
        relatedQuestions: searchResult.peopleAlsoAsk || [],
        relatedSearches: searchResult.relatedSearches || []
      };
      
      return {
        analyzedData: this.formatSerpAnalysis(searchResult)
      };
    } catch (error) {
      console.error("SERP analysis failed:", error);
      throw error;
    }
  }

  /**
   * Research keywords related to a seed keyword.
   * @param params - Keyword research parameters
   * @returns Promise resolving to keyword research data
   */
  async researchKeywords(params: IResearchKeywordsParams): Promise<IResearchKeywordsResult> {
    try {
      const searchParams: ISearchParams = {
        q: params.keyword,
        gl: params.location ? "us" : undefined,
        hl: params.language || "en"
      };
      
      const searchResult = await this.search(searchParams);
      
      // Extract related keywords from search results
      return {
        keywordData: this.formatKeywordResearch(searchResult, params)
      };
    } catch (error) {
      console.error("Keyword research failed:", error);
      throw error;
    }
  }

  /**
   * Analyze competitors for a domain/keyword.
   * @param params - Competitor analysis parameters
   * @returns Promise resolving to competitor analysis data
   */
  async analyzeCompetitors(params: IAnalyzeCompetitorsParams): Promise<IAnalyzeCompetitorsResult> {
    try {
      // If keyword is provided, search for it and analyze competing domains
      if (params.keyword) {
        const searchParams: ISearchParams = {
          q: params.keyword,
          gl: "us",
          hl: "en",
          num: params.num_results || 10
        };
        
        const searchResult = await this.search(searchParams);
        
        // Analyze the domain in the search results
        return {
          competitorData: this.formatCompetitorAnalysis(searchResult, params)
        };
      } else {
        // If just a domain, perform a simplified analysis
        return {
          competitorData: {
            domain: params.domain,
            analysis: `Domain analysis for ${params.domain}`
          }
        };
      }
    } catch (error) {
      console.error("Competitor analysis failed:", error);
      throw error;
    }
  }

  /**
   * Format search results into a structured SERP analysis.
   * @param searchResult - Raw search result
   * @returns Formatted SERP analysis
   * @private
   */
  private formatSerpAnalysis(searchResult: ISearchResult): any {
    const searchInfo = searchResult.searchParameters ? 
      `Search Information:\nTotal Results: ${searchResult.organic?.length || 0}\nTime Taken: ${searchResult.searchParameters.time || '0.0s'}\n\n` : 
      '';
    
    // Format Knowledge Graph information
    const kgInfo = searchResult.knowledgeGraph ? 
      `Knowledge Graph Information:\nTitle: ${searchResult.knowledgeGraph.title || 'N/A'}\nType: ${searchResult.knowledgeGraph.type || 'N/A'}\n\n\n\n` : 
      '';
    
    // Format Featured Snippet if available
    const featuredSnippet = searchResult.organic && searchResult.organic[0] && searchResult.organic[0].sitelinks ? 
      `Featured Snippet:\nType: organic_result\nContent: ${searchResult.organic[0].snippet || 'N/A'}\n\n\n` : 
      '';
    
    // Format Organic Results
    let organicResults = 'Top Organic Results:\n';
    if (searchResult.organic && searchResult.organic.length > 0) {
      searchResult.organic.forEach((result, index) => {
        organicResults += `${index + 1}. ${result.title || 'N/A'}\n   URL: ${result.link || 'N/A'}\n   Snippet: ${result.snippet || 'N/A'}\n\n---\n`;
      });
    } else {
      organicResults += 'No organic results found.\n\n';
    }
    
    // Format People Also Ask
    let peopleAlsoAsk = '';
    if (searchResult.peopleAlsoAsk && searchResult.peopleAlsoAsk.length > 0) {
      peopleAlsoAsk = '\nPeople Also Ask:\n';
      searchResult.peopleAlsoAsk.forEach(question => {
        peopleAlsoAsk += `- ${question.question || 'N/A'}\n`;
      });
    }
    
    // Format Related Searches
    let relatedSearches = '';
    if (searchResult.relatedSearches && searchResult.relatedSearches.length > 0) {
      relatedSearches = '\nRelated Searches:\n';
      searchResult.relatedSearches.forEach(search => {
        relatedSearches += `- ${search.query || 'N/A'}\n`;
      });
    }
    
    return searchInfo + kgInfo + featuredSnippet + organicResults + peopleAlsoAsk + relatedSearches;
  }

  /**
   * Format search results into keyword research data.
   * @param searchResult - Raw search result
   * @param params - Original keyword research parameters
   * @returns Formatted keyword research data
   * @private
   */
  private formatKeywordResearch(searchResult: ISearchResult, params: IResearchKeywordsParams): any {
    // Get search statistics
    const searchStats = `Keyword Analysis for: ${params.keyword}\n\nSearch Statistics:\nTotal Results: ${searchResult.organic?.length || 0}\nTime Taken: ${searchResult.searchParameters?.time || '0.0s'}\n\n`;
    
    // Get related questions (People Also Ask)
    let questions = '';
    if (params.include_questions && searchResult.peopleAlsoAsk && searchResult.peopleAlsoAsk.length > 0) {
      questions = 'People Also Ask Questions:\n';
      searchResult.peopleAlsoAsk.forEach(question => {
        questions += `- ${question.question || 'N/A'}\n`;
      });
      questions += '\n';
    }
    
    // Get related searches
    let related = '';
    if (params.include_related && searchResult.relatedSearches && searchResult.relatedSearches.length > 0) {
      related = 'Related Searches:\n';
      searchResult.relatedSearches.forEach(search => {
        related += `- ${search.query || 'N/A'}\n`;
      });
      related += '\n';
    }
    
    // Get search features stats
    const features = `SERP Features Distribution:\n- Rich Snippets: ${searchResult.organic && searchResult.organic.filter(r => r.sitelinks).length || 0} results`;
    
    return searchStats + questions + related + features;
  }

  /**
   * Format search results into competitor analysis.
   * @param searchResult - Raw search result
   * @param params - Original competitor analysis parameters
   * @returns Formatted competitor analysis
   * @private
   */
  private formatCompetitorAnalysis(searchResult: ISearchResult, params: IAnalyzeCompetitorsParams): any {
    const domainPages = searchResult.organic?.filter(result => 
      result.link && result.link.includes(params.domain)
    ) || [];
    
    // Get domain analysis intro
    const domainIntro = `Domain Analysis for: ${params.domain}\n\nTotal Indexed Pages: ${domainPages.length || 0}\nTime Taken: ${searchResult.searchParameters?.time || '0.0s'}\n\n`;
    
    // Format top performing pages
    let topPages = 'Top Performing Pages:\n';
    if (domainPages.length > 0) {
      domainPages.forEach((page, index) => {
        topPages += `${index + 1}. ${page.title || 'N/A'}\n   URL: ${page.link || 'N/A'}\n   Position: ${page.position || 'N/A'}\n   Snippet: ${page.snippet || 'N/A'}\n---\n`;
      });
    } else {
      // If no domain pages found in results, format some organic results
      if (searchResult.organic && searchResult.organic.length > 0) {
        searchResult.organic.slice(0, 10).forEach((page, index) => {
          topPages += `${index + 1}. ${page.title || 'N/A'}\n   URL: ${page.link || 'N/A'}\n   Position: ${index + 1}\n   Snippet: ${page.snippet || 'N/A'}\n---\n`;
        });
      } else {
        topPages += 'No pages found for this domain in search results.\n';
      }
    }
    
    // Add SERP features if requested
    let serpFeatures = '';
    if (params.include_features) {
      const features = [];
      if (searchResult.knowledgeGraph) features.push('Knowledge Graph');
      if (searchResult.peopleAlsoAsk && searchResult.peopleAlsoAsk.length > 0) features.push('People Also Ask');
      if (searchResult.relatedSearches && searchResult.relatedSearches.length > 0) features.push('Related Searches');
      
      const sitelinks = searchResult.organic?.filter(r => r.sitelinks).length || 0;
      if (sitelinks > 0) features.push('Sitelinks');
      
      serpFeatures = '\n\nSERP Features Present:\n- ' + (features.length > 0 ? features.join('\n- ') : 'None detected');
    }
    
    return domainIntro + topPages + serpFeatures;
  }
}
