from fastapi import APIRouter

from app.routes.analytics import router as analytics_router
from app.routes.chat import router as chat_router
from app.routes.products import router as products_router
from app.routes.reviews import router as reviews_router
from app.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(analytics_router)
api_router.include_router(products_router)
api_router.include_router(reviews_router)
api_router.include_router(search_router)
api_router.include_router(chat_router)
