from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.schemas.category_schemas import CategoryBase, CategoryCreate
from api.utils.dependencies import (CategoryServiceDeps, CurrentUserDeps,
                                    RecordServiceDeps)

category_router = APIRouter()


@category_router.get(
    '/',
    response_model=list[CategoryBase],
)
async def get_user_categories(
        user: CurrentUserDeps,
        category_service: CategoryServiceDeps,
        hidden: Annotated[bool | None, Query()] = False,
):
    return await category_service.get_instances(user_id=user.id, hidden=hidden)


@category_router.get(
    '/{category_name}',
    response_model=CategoryBase,
)
async def get_category_by_name(
        category_name: str,
        category_service: CategoryServiceDeps,
        hidden: Annotated[bool | None, Query()] = False,
):
    return await category_service.get_instance_or_404(name=category_name, hidden=hidden)


@category_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryBase
)
async def create_category_for_user(
        current_user: CurrentUserDeps,
        category: CategoryBase,
        manager: CategoryServiceDeps,
):
    same_category = await manager.get_instance(name=category.name, user_id=current_user.id)

    if same_category:
        if same_category.hidden:
            return await manager.update_instance(
                instance_id=same_category.id,
                data={'hidden': False, **category.model_dump()},
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Category with name {category.name!r} already exists.'
        )

    return await manager.create_instance(
        instance=CategoryCreate(user_id=current_user.id, name=category.name)
    )


@category_router.put(
    '/{category_name}',
    status_code=status.HTTP_200_OK,
    response_model=CategoryBase,
)
async def update_category(
        category_name: str,
        updated_category: CategoryBase,
        user: CurrentUserDeps,
        manager: CategoryServiceDeps,
):
    category = await manager.get_instance_or_404(
        name=category_name, user_id=user.id, hidden=False
    )
    return await manager.update_instance(
        category.id, updated_category.model_dump()
    )


@category_router.delete(
    '/{category_name}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
        category_name: str,
        user: CurrentUserDeps,
        category_manager: CategoryServiceDeps,
        record_manager: RecordServiceDeps
) -> None:
    category = await category_manager.get_instance_or_404(
        name=category_name, user_id=user.id, hidden=False
    )
    category_records = await record_manager.get_instances(
        category_id=category.id
    )
    if category_records:
        await category_manager.update_instance(
            instance_id=category.id, data={'hidden': True}
        )
    else:
        await category_manager.delete_instance(id=category.id)
