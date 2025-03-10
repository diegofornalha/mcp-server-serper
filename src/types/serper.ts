/**
 * Type definitions for Serper API requests and responses.
 */

/**
 * Search parameters for Serper API.
 */
export interface ISearchParams {
  /** The search query string */
  q: string;
  /** Geographical location for search results (e.g., "us") */
  gl?: string;
  /** Language for search results (e.g., "en") */
  hl?: string;
  /** Location for search results (e.g., "SoHo, New York, United States") */
  location?: string;
  /** Whether to autocorrect spelling in query */
  autocorrect?: boolean;
  /** Number of results per page */
  num?: number;
  /** Time-based search filter (e.g., "qdr:d" for past day) */
  tbs?: "qdr:h" | "qdr:d" | "qdr:w" | "qdr:m" | "qdr:y";
  /** Page number of results */
  page?: number;
  /** Limit results to specific domain */
  site?: string;
  /** Limit to specific file types (e.g., 'pdf', 'doc') */
  filetype?: string;
  /** Search for pages with word in URL */
  inurl?: string;
  /** Search for pages with word in title */
  intitle?: string;
  /** Find similar websites */
  related?: string;
  /** View Google's cached version */
  cache?: string;
  /** Date before in YYYY-MM-DD format */
  before?: string;
  /** Date after in YYYY-MM-DD format */
  after?: string;
  /** Exact phrase match */
  exact?: string;
  /** Terms to exclude (comma-separated) */
  exclude?: string;
  /** Alternative terms (OR operator) (comma-separated) */
  or?: string;
}

/**
 * Scrape parameters for Serper API.
 */
export interface IScrapeParams {
  url: string;
  includeMarkdown?: boolean;
}

/**
 * Knowledge graph entry in search results.
 */
export interface IKnowledgeGraph {
  title: string;
  type: string;
  website?: string;
  description?: string;
  /** Key attributes (e.g., CEO, Founded date) */
  attributes?: Record<string, string>;
}

/**
 * Individual organic search result.
 */
export interface IOrganicResult {
  title: string;
  link: string;
  snippet: string;
  position: number;
  /** Sitelinks for this result, if any */
  sitelinks?: any[];
}

/**
 * "People also ask" question and answer.
 */
export interface IPeopleAlsoAsk {
  question: string;
  snippet: string;
  link: string;
}

/**
 * Related search query suggestion.
 */
export interface IRelatedSearch {
  query: string;
}

/**
 * Complete search result from Serper API.
 */
export interface ISearchResult {
  /** Echo of search parameters */
  searchParameters: {
    q: string;
    gl?: string;
    hl?: string;
    location?: string;
    autocorrect?: boolean;
    type?: string;
    num?: number;
    page?: number;
    tbs?: "qdr:h" | "qdr:d" | "qdr:w" | "qdr:m" | "qdr:y";
    /** Time taken for the search */
    time?: string;
  };
  /** Knowledge graph data if available */
  knowledgeGraph?: IKnowledgeGraph;
  /** Organic search results */
  organic: IOrganicResult[];
  /** "People also ask" questions */
  peopleAlsoAsk?: IPeopleAlsoAsk[];
  /** Related search queries */
  relatedSearches?: IRelatedSearch[];
}

/**
 * Represents the result of a scrape operation from the Serper API.
 */
export interface IScrapeResult {
  text: string;
  markdown?: string;
  metadata?: Record<string, string>;
  jsonld?: Record<string, any>;
  credits?: number;
}

/** Parameters for health check */
export interface IHealthParams {
  /** Optional dummy parameter for health check */
  dummy?: string;
}

/** Health check response */
export interface IHealthResult {
  /** Status message */
  status: string;
  /** API version */
  version?: string;
}

/** Parameters for SERP analysis */
export interface IAnalyzeSerpParams {
  /** Search query to analyze */
  query: string;
  /** Geographical location for search results (e.g., "us") */
  gl?: string;
  /** Language for search results (e.g., "en") */
  hl?: string;
  /** Device type (desktop or mobile) */
  device?: "desktop" | "mobile";
  /** Google domain to use */
  google_domain?: string;
  /** Number of results to include */
  num?: number;
  /** Safe search setting */
  safe?: "active" | "off";
  /** Specific location */
  location?: string;
}

/** SERP analysis result */
export interface IAnalyzeSerpResult {
  /** Structured SERP analysis data */
  analyzedData: any;
}

/** Parameters for keyword research */
export interface IResearchKeywordsParams {
  /** Seed keyword to research */
  keyword: string;
  /** Language for results */
  language?: string;
  /** Location for results */
  location?: string;
  /** Whether to include questions in results */
  include_questions?: boolean;
  /** Whether to include related searches */
  include_related?: boolean;
  /** Whether to include suggestions */
  include_suggestions?: boolean;
}

/** Keyword research result */
export interface IResearchKeywordsResult {
  /** Structured keyword research data */
  keywordData: any;
}

/** Parameters for competitor analysis */
export interface IAnalyzeCompetitorsParams {
  /** Domain to analyze */
  domain: string;
  /** Keyword to analyze for (optional) */
  keyword?: string;
  /** Number of results to include */
  num_results?: number;
  /** Whether to include feature analysis */
  include_features?: boolean;
}

/** Competitor analysis result */
export interface IAnalyzeCompetitorsResult {
  /** Structured competitor analysis data */
  competitorData: any;
}
