# Architecture Notes

- `apps/api` hosts the FastAPI backend with route, service and repository separation.
- `apps/web` hosts the Next.js App Router frontend with feature-oriented UI slices.
- `data/seeds` contains the current catalog seed and can evolve into ingestion outputs.
- `packages/*` reserves space for shared logic around types, prompts, retrieval and analysis.
