export type RetrievalDocument = {
  id: string;
  productSlug: string;
  source: string;
  content: string;
  metadata?: Record<string, unknown>;
};

export type ChatGroundingBundle = {
  summary: string;
  evidence: string[];
  issueReferences: string[];
};
