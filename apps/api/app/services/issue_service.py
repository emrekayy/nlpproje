from app.services.catalog_service import catalog_service


class IssueService:
    def get_issues(self, slug: str) -> dict:
        product = catalog_service.get_product(slug)
        return {
            "slug": product["slug"],
            "name": product["name"],
            "common_issues": product["analysis"]["common_issues"],
            "evidence_snippets": product["analysis"]["review_summary"]["evidence_snippets"],
        }


issue_service = IssueService()
