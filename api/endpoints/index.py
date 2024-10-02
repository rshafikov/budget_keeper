from fastapi import APIRouter
from fastapi.responses import RedirectResponse

index_router = APIRouter()


@index_router.get('/')
async def index() -> RedirectResponse:
    return RedirectResponse('/docs')
