import pytest
from fastapi import status

from api.core import settings


@pytest.mark.skipif(
    not settings.DB_TEST,
    reason='Setup test db instead of running production.'
)
class TestCategories:
    @pytest.mark.asyncio
    async def test_create_category(self, auth_client, default_user, db_manager):
        new_category = {'name': 'new_category'}
        categories_before = await db_manager.category.count_instances(user_id=default_user.id)
        response = await auth_client.post('/categories/', json=new_category)
        categories_after = await db_manager.category.count_instances(user_id=default_user.id)

        assert categories_after == categories_before + 1
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == new_category

    @pytest.mark.asyncio
    async def test_get_categories(self, auth_client, default_user, default_category, db_manager):
        categories = await db_manager.category.get_instances(user_id=default_user.id)
        response = await auth_client.get('/categories/')

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert response.json() == [{'name': c.name} for c in categories]

    @pytest.mark.asyncio
    async def test_get_category(self, auth_client, default_category):
        response = await auth_client.get(f'/categories/{default_category.name}')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['name'] == default_category.name

    @pytest.mark.asyncio
    async def test_categories_protected(self, client):
        get_response = await client.get('/categories/')
        post_response = await client.post('/categories/', json={'name': 'test_category'})

        assert get_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert post_response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_same_category(
            self, auth_client, default_user, default_category, db_manager
    ):
        new_category = {'name': default_category.name, 'user_id': default_user.id}
        categories_before = await db_manager.category.count_instances(user_id=default_user.id)
        response = await auth_client.post('/categories/', json=new_category)
        categories_after = await db_manager.category.count_instances(user_id=default_user.id)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert categories_after == categories_before
        assert response.json()['detail'] == (
            f'Category with name {default_category.name!r} already exists.')

    @pytest.mark.asyncio
    async def test_delete_empty_category(
            self, auth_client, default_user, random_category, db_manager
    ):
        categories_before = await db_manager.category.count_instances()
        response = await auth_client.delete(f'/categories/{random_category.name}')
        categories_after = await db_manager.category.count_instances()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert categories_before == categories_after + 1

    @pytest.mark.asyncio
    async def test_update_category(
            self, auth_client, random_category, default_record, db_manager
    ):
        changes = {'name': 'random_category_updated_name'}
        response = await auth_client.put(f'/categories/{random_category.name}', json=changes)
        category = await db_manager.category.get_instance(id=random_category.id)

        assert response.status_code == status.HTTP_200_OK
        assert category.name == changes['name']

    @pytest.mark.asyncio
    async def test_delete_category_with_record(
            self, auth_client, default_category, default_record, db_manager
    ):
        categories_before = await db_manager.category.count_instances(hidden=False)
        response = await auth_client.delete(f'/categories/{default_category.name}')
        categories_after = await db_manager.category.count_instances(hidden=False)
        hidden_category = await db_manager.category.get_instance(
            id=default_category.id, hidden=True
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert categories_before == categories_after + 1
        assert hidden_category is not None
        assert hidden_category.hidden

    @pytest.mark.asyncio
    async def test_create_category_if_it_hidden(
            self, auth_client, default_category, default_record, db_manager
    ):
        await auth_client.delete(f'/categories/{default_category.name}')
        category_before_recreate = await db_manager.category.get_instance(id=default_category.id)
        response = await auth_client.post('/categories/', json={'name': default_category.name})
        category_after = await db_manager.category.get_instance(id=default_category.id)

        assert response.status_code == status.HTTP_201_CREATED
        assert category_before_recreate.hidden
        assert not category_after.hidden
