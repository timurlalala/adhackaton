from logging import getLogger
from fastapi import APIRouter, status, Depends, HTTPException, Path
from starlette.status import HTTP_404_NOT_FOUND

from app.schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, update, or_, and_
from database import get_async_session
from app.models import Character, UserCharacter, User, DialogHistory


logger = getLogger('app_router')

router = APIRouter(
    prefix="/api/v1",
    tags=["API"],
)

@router.post('/create_character', status_code=status.HTTP_201_CREATED, response_model=CharacterCreationResponse)
async def create_character(
        request: CharacterCreationRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Создает персонажа для общения
    :param request: Тело запроса
    :param session: Сессия БД
    :return: character_id
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ).returning(User))

    character = Character(
        creator_user_id=request.user_id,
        name=request.name,
        params=request.params,
        hello_message=request.hello_message
    )
    session.add(character)

    try:
        await session.commit()
        await session.refresh(character)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при создании персонажа: {e}")

    user_character = UserCharacter(
        character_id=character.character_id,
        user_id=request.user_id
    )
    session.add(user_character)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при добавлении персонажа в каталог: {e}")

    return CharacterCreationResponse(character_id=character.character_id)


@router.post('/update_character', status_code=status.HTTP_200_OK)
async def update_character(
        request: CharacterUpdateRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Обновляет информацию о персонаже
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ).returning(User))

    result = await session.execute(
        select(Character).where(
            and_(
                Character.__table__.c.character_id == request.character_id,
                Character.__table__.c.creator_user_id == request.user_id
            )
        )
    )
    character_to_update = result.one_or_none().Character

    if character_to_update is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                             detail=f"Пользователь не создавал бота с id == {request.character_id}")
    if val := request.params:
        character_to_update.params = val
    if val := request.hello_message:
        character_to_update.hello_message = val
    if val := request.name:
        character_to_update.name = val
    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при обновлении персонажа: {e}")

@router.post('/select_character', status_code=status.HTTP_200_OK)
async def select_character(
        request: CharacterSelectionRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Выбирает персонажа
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    result = await session.execute(
        select(UserCharacter.__table__.c.user_id).where(and_(
            UserCharacter.__table__.c.user_id == request.user_id,
            UserCharacter.__table__.c.character_id == request.character_id
        ))
    )

    if result.scalar_one_or_none() is not None:
        user.active_character = request.character_id
        try:
            await session.commit()
            return None
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Ошибка при выборе персонажа: {e}")
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                             detail=f"У пользователя в каталоге нет бота с id == {request.character_id}")

@router.post('/remove_character', status_code=status.HTTP_200_OK)
async def remove_character(
        request: CharacterSelectionRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Удаляет персонажа из приватного каталога пользователя
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    result = await session.execute(
        select(Character.__table__.c.character_id).where(and_(
            Character.__table__.c.creator_user_id == request.user_id,
            Character.__table__.c.character_id == request.character_id
        ))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Попытка скрыть собственного персонажа из каталога")

    if user.active_character == request.character_id:
        user.active_character = None


    await session.execute(
        delete(UserCharacter).where(and_(
            UserCharacter.__table__.c.user_id == request.user_id,
            UserCharacter.__table__.c.character_id == request.character_id
        ))
    )

    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при удалении персонажа из каталога: {e}")


@router.post('/delete_character', status_code=status.HTTP_200_OK)
async def delete_character(
        request: CharacterDeletionRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Удаляет персонажа, созданного пользователем, из всех каталогов
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    result = await session.execute(
        select(Character).where(and_(
            Character.__table__.c.creator_user_id == request.user_id,
            Character.__table__.c.character_id == request.character_id
        ))
    )
    if (character := result.one_or_none()) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Пользователь не владеет данным персонажем")

    await session.execute(delete(character))

    if user.active_character == request.character_id:
        user.active_character = None

    await session.execute(
        delete(UserCharacter).where(
            UserCharacter.__table__.c.character_id == request.character_id
        )
    )

    await session.execute(
        update(User).where(
            User.__table__.c.active_character == request.character_id
        ).values(active_character=None)
    )

    await session.execute(
        delete(DialogHistory).where(
            DialogHistory.__table__.c.character_id == request.character_id
        )
    )

    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при удалении персонажа из БД: {e}")

@router.post('/add_character', status_code=status.HTTP_200_OK)
async def add_character(
        request: CharacterAddRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Добавляет персонажа в личный каталог
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    result = await session.execute(
        select(Character.__table__.c.is_shared).where(
            Character.__table__.c.character_id == request.character_id
        )
    )
    if result.scalar_one_or_none() in {False, None}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Данного персонажа нельзя добавить в каталог")

    user.active_character = request.character_id

    session.add(UserCharacter(user_id=request.user_id, character_id=request.character_id))

    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при добавлении персонажа в каталог: {e}")

@router.post('/share_character', status_code=status.HTTP_200_OK)
async def share_character(
        request: CharacterShareRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Обновляет информацию о персонаже
    :param request:
    :param session:
    :return:
    """
    await session.execute(insert(User).values(
        user_id=request.user_id,
    ).on_conflict_do_nothing(
        index_elements=['user_id']  # Указываем уникальный индекс/столбец для конфликта
    ).returning(User))

    result = await session.execute(
        select(Character).where(
            and_(
                Character.__table__.c.character_id == request.character_id,
                Character.__table__.c.creator_user_id == request.user_id
            )
        )
    )
    character_to_update = result.one_or_none().Character

    if character_to_update is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                             detail=f"Пользователь не создавал бота с id == {request.character_id}")
    character_to_update.is_shared = request.share
    try:
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Ошибка при публикации персонажа: {e}")

@router.get('/catalog/global', status_code=status.HTTP_200_OK)
async def get_global_catalog(
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Возвращает глобальный каталог
    :param session:
    :return:
    """
    result = await session.execute(
        select(Character.__table__.c.character_id, Character.__table__.c.name).where(
            Character.__table__.c.is_shared
        )
    )
    return [CharacterShortItem(character_id=i.character_id, name=i.name) for i in result]

@router.get('/catalog/{user_id}}', status_code=status.HTTP_200_OK)
async def get_global_catalog(
        user_id: Annotated[int, Path()],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Возвращает глобальный каталог
    :param session:
    :return:
    """
    result = await session.execute(
        select(Character.character_id, Character.name) # Выбираем character_id и name из таблицы Character
        .join(UserCharacter, UserCharacter.character_id == Character.character_id) # Делаем JOIN по character_id
        .where(UserCharacter.user_id == user_id) # Фильтруем по user_id из UserCharacter
    )
    return [CharacterShortItem(character_id=i.character_id, name=i.name) for i in result]