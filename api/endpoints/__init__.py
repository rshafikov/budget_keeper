from fastapi import APIRouter

from .auth import auth_router  # noqa
from .categories import category_router  # noqa
from .currency import currency_router  # noqa
from .index import index_router  # noqa
from .records import record_router  # noqa
from .users import user_router  # noqa

main_router = APIRouter()

main_router.include_router(auth_router, prefix="/auth", tags=["auth"])
main_router.include_router(category_router, prefix="/categories", tags=["categories"])
main_router.include_router(user_router, prefix="/users", tags=["users"])
main_router.include_router(record_router, prefix="/records", tags=["records"])
main_router.include_router(currency_router, prefix="/currency", tags=["currency"])
main_router.include_router(index_router)
