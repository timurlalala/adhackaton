from sqlalchemy import Column, BigInteger, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB # Используем UUID и JSONB для PostgreSQL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import datetime

# Создаем базовый класс для декларативных моделей
Base = declarative_base()

# --- Таблица users (Пользователи) ---
class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, unique=True, comment="Уникальный идентификатор пользователя Telegram")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False, comment="Дата и время регистрации пользователя")
    active_character = Column(UUID(as_uuid=True), nullable=True, default=None, comment="ID персонажа")

    # Отношения
    characters_created = relationship('Character', back_populates='creator')
    user_catalog_entries = relationship('UserCharacter', back_populates='user')
    dialog_messages = relationship('DialogHistory', back_populates='user')

    def __repr__(self):
        return f"<User(user_id={self.user_id}, created_at='{self.created_at}')>"

# --- Таблица characters (Персонажи) ---
class Character(Base):
    __tablename__ = 'characters'

    # Используем UUID для character_id, генерируем по умолчанию
    character_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, comment="Уникальный идентификатор персонажа")
    creator_user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, comment="ID пользователя, создавшего этого персонажа")
    name = Column(String(255), nullable=False, comment="Имя персонажа")
    params = Column(Text, comment="Параметры персонажа для настройки LLM (JSONB)")
    hello_message = Column(Text, comment="Приветственное сообщение от персонажа")
    is_shared = Column(Boolean, default=False, nullable=False, comment="Флаг, указывающий, доступен ли персонаж в глобальном каталоге")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False, comment="Дата и время создания персонажа")
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="Дата и время последнего обновления информации о персонаже")

    # Отношения
    creator = relationship('User', back_populates='characters_created')
    user_catalog_entries = relationship('UserCharacter', back_populates='character')
    dialog_messages = relationship('DialogHistory', back_populates='character')

    def __repr__(self):
        return f"<Character(character_id={self.character_id}, name='{self.name}', creator_user_id={self.creator_user_id})>"

# --- Таблица user_characters (Персонажи пользователей) ---
class UserCharacter(Base):
    __tablename__ = 'user_characters'

    user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True, comment="ID пользователя")
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.character_id'), primary_key=True, comment="ID персонажа")

    # Отношения
    user = relationship('User', back_populates='user_catalog_entries')
    character = relationship('Character', back_populates='user_catalog_entries')

    def __repr__(self):
        return f"<UserCharacter(user_id={self.user_id}, character_id={self.character_id})>"

# --- Таблица dialog_history (История диалогов) ---
class DialogHistory(Base):
    __tablename__ = 'dialog_history'

    message_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="Уникальный идентификатор сообщения")
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, comment="ID пользователя, отправившего сообщение")
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.character_id'), nullable=False, comment="ID персонажа, с которым ведется диалог")
    sender_type = Column(String(10), nullable=False, comment="Тип отправителя: 'user' или 'character'")
    message_text = Column(Text, nullable=False, comment="Текст сообщения")
    timestamp = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False, comment="Дата и время отправки сообщения", index=True)

    # Отношения
    user = relationship('User', back_populates='dialog_messages')
    character = relationship('Character', back_populates='dialog_messages')

    def __repr__(self):
        return f"<DialogHistory(message_id={self.message_id}, user_id={self.user_id}, character_id={self.character_id}, sender_type='{self.sender_type}')>"