import time
import uuid
from dataclasses import dataclass

import pytest
from httpx import ASGITransport, AsyncClient

from api.core.security import create_token
from api.db.database import engine
from api.db.models import BaseModel
from api.endpoints.auth import check_token
from api.main import app
from api.schemas.category_schemas import Category, CategoryCreate
from api.schemas.currency_schemas import CurrencyBase
from api.schemas.record_schemas import RecordCreate
from api.schemas.user_schemas import User, UserCreate
from api.services.category_service import CategoryService, get_category_service
from api.services.currency_service import CurrencyService, get_currency_service
from api.services.record_service import RecordService, get_record_service
from api.services.user_service import UserService, get_user_service
from api.utils.uow import UnitOfWork


@dataclass(frozen=True)
class TestDBManager:
    user: UserService
    category: CategoryService
    currency: CurrencyService
    record: RecordService


@pytest.fixture(scope='module')
async def test_user() -> UserCreate:
    return UserCreate(
        telegram_id='test_user',
        password='pass',
        name='test_user_name',
        lastname='test_user_lastname'
    )


@pytest.fixture(scope='module')
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        yield
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture(scope='module')
async def db_manager(create_db):
    uow = UnitOfWork()
    user_service = await get_user_service(uow)
    category_service = await get_category_service(uow)
    currency_service = await get_currency_service(uow)
    record_service = await get_record_service(uow)

    return TestDBManager(
        user=user_service,
        category=category_service,
        currency=currency_service,
        record=record_service
    )


@pytest.fixture(scope='module')
async def default_user(db_manager: TestDBManager, test_user: UserCreate) -> User:
    user = await db_manager.user.add_user(test_user.model_copy(deep=True))
    yield user
    await db_manager.user.delete_instance(id=user.id)


@pytest.fixture(scope='module')
async def auth_client(default_user: User):
    token = create_token(default_user.telegram_id)
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',
            headers={'Authorization': f'Bearer {token}'}
    ) as authorized_client:
        yield authorized_client


@pytest.fixture(scope='module')
async def client(create_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def mock_token():
    admin_token = {
        'exp': int(time.time() + 60),
        'role': 'admin',
        'sub': 'test_user'
    }
    app.dependency_overrides[check_token] = lambda: admin_token
    yield admin_token
    app.dependency_overrides = {}


@pytest.fixture(scope='module')
async def default_currency(db_manager: TestDBManager):
    euro = await db_manager.currency.create_instance(
        CurrencyBase(name='EUR', symbol='€'))
    yield euro
    await db_manager.currency.delete_instance(id=euro.id)


@pytest.fixture(scope='module')
async def default_category(db_manager: TestDBManager, default_user: User) -> Category:
    new_category = await db_manager.category.create_instance(
        CategoryCreate(name='test_category', user_id=default_user.id)
    )
    yield new_category
    await db_manager.category.delete_instance(id=new_category.id)


@pytest.fixture(scope='function')
async def random_category(db_manager: TestDBManager, default_user: User) -> Category:
    new_category = await db_manager.category.create_instance(
        CategoryCreate(name=str(uuid.uuid4()), user_id=default_user.id)
    )
    yield new_category
    await db_manager.category.delete_instance(id=new_category.id)


@pytest.fixture(scope='module')
async def default_record(
        db_manager: TestDBManager,
        default_user: User,
        default_category: Category,
) -> Category:
    new_record = await db_manager.record.create_instance(
        RecordCreate(
            user_id=default_user.id,
            category_id=default_category.id,
            currency=default_user.currency,
            amount='777'
        )
    )
    yield new_record
    await db_manager.record.delete_instance(id=new_record.id)
