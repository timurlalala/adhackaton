from logging import getLogger
from fastapi import APIRouter, status, Depends, HTTPException, Path
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, update, or_, and_
from database import get_async_session
from app.models import Character, UserCharacter, User, DialogHistory
from llm_openai import get_openai_client, get_llm_name
from openai import AsyncClient, OpenAIError


logger = getLogger('app_router')

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["API"],
)

@router.post('/hello_message', status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def get_hello_message(
        request: HelloMessageRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        openai_client: Annotated[AsyncClient, Depends(get_openai_client)],
        llm_name: Annotated[str, Depends(get_llm_name)]
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
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    if user.active_character is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Активный персонаж не выбран")

    else:
        result = await session.execute(select(Character.__table__.c.params).where(
            Character.__table__.c.character_id == user.active_character
        ))
        system_msg = result.scalar()

    user_id = request.user_id

    messages_for_openai = [{"role": "system", "content": system_msg + "\nПоприветствуй пользователя."}]

    # 4. Отправляем запрос в OpenAI API
    try:
        logger.info('connecting to openrouter')
        openai_response = await openai_client.chat.completions.create(
            model=llm_name,  # Или другую подходящую модель
            messages=messages_for_openai
        )
    except OpenAIError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка OpenAI API: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Произошла непредвиденная ошибка: {e}")

    ai_response_text = openai_response.choices[0].message.content

    # 5. Сохраняем ответ AI в историю
    ai_message = DialogHistory(
        user_id=user_id,
        character_id=user.active_character,
        sender_type='character',
        message_text=ai_response_text
    )

    try:
        session.add(ai_message)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Не удалось сохранить ответ модели {e}")

    # 6. Возвращаем ответ AI пользователю
    return MessageResponse(message=ai_response_text)


@router.post('/send_message', status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_message(
        request: MessageRequest,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        openai_client: Annotated[AsyncClient, Depends(get_openai_client)],
        llm_name: Annotated[str, Depends(get_llm_name)]
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
    ))

    result = await session.execute(select(User).where(User.__table__.c.user_id == request.user_id))
    user = result.one().User

    if user.active_character is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Активный персонаж не выбран")
    else:
        result = await session.execute(select(Character.__table__.c.params).where(
            Character.__table__.c.character_id == user.active_character
        ))
        system_msg = result.scalar()

    user_id = request.user_id
    user_message_text = request.message

    # 1. Сохраняем новое сообщение пользователя в историю
    new_message = DialogHistory(
        user_id=user_id,
        character_id=user.active_character,
        sender_type='user',
        message_text=user_message_text
    )
    try:
        session.add(new_message)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Не удалось сохранить историю {e}")

    history_query = select(DialogHistory).where(
        and_(
            DialogHistory.user_id == user_id,
            DialogHistory.character_id == user.active_character
        )
    ).order_by(DialogHistory.timestamp).limit(200)  # Можно настроить лимит или стратегию выборки

    history_result = await session.execute(history_query)
    dialog_history = history_result.all()

    # OpenAI API ожидает список словарей с 'role' и 'content'
    messages_for_openai = []
    for i in dialog_history:
        msg = i.DialogHistory
        role = 'user' if msg.sender_type == 'user' else 'assistant'  # 'character' маппится на 'assistant'
        messages_for_openai.append({"role": role, "content": msg.message_text})

    # Можно добавить системное сообщение для настройки поведения AI
    messages_for_openai.insert(0, {"role": "system", "content": system_msg})

    # 4. Отправляем запрос в OpenAI API
    try:
        logger.info('connecting to openrouter')
        openai_response = await openai_client.chat.completions.create(
            model=llm_name,  # Или другую подходящую модель
            messages=messages_for_openai
        )
    except OpenAIError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка OpenAI API: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Произошла непредвиденная ошибка: {e}")

    ai_response_text = openai_response.choices[0].message.content

    # 5. Сохраняем ответ AI в историю
    ai_message = DialogHistory(
        user_id=user_id,
        character_id=user.active_character,
        sender_type='character',
        message_text=ai_response_text
    )

    try:
        session.add(ai_message)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Не удалось сохранить ответ модели {e}")

    # 6. Возвращаем ответ AI пользователю
    return MessageResponse(message=ai_response_text)

