from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import UUID
from typing_extensions import Annotated
from typing import List, Dict

class CharacterCreationRequest(BaseModel):
    user_id: int
    name: str
    params: str | None = Field(None)
    hello_message: str | None = Field(None)

class CharacterCreationResponse(BaseModel):
    character_id: UUID

class CharacterUpdateRequest(BaseModel):
    user_id: int
    character_id: UUID
    name: str | None = Field(None)
    params: str | None = Field(None)
    hello_message: str | None = Field(None)

class CharacterSelectionRequest(BaseModel):
    user_id: int
    character_id: UUID

class CharacterRemoveRequest(BaseModel):
    user_id: int
    character_id: UUID

class CharacterDeletionRequest(BaseModel):
    user_id: int
    character_id: UUID

class CharacterAddRequest(BaseModel):
    user_id: int
    character_id: UUID

class CharacterShareRequest(BaseModel):
    user_id: int
    character_id: UUID
    share: bool

class CharacterShortItem(BaseModel):
    character_id: UUID
    name: str

class CatalogResponse(BaseModel):
    characters: List[CharacterShortItem]

class UserDataDeletionRequest(BaseModel):
    user_id: int

class HelloMessageRequest(BaseModel):
    user_id: int
    character_id: UUID

class HelloMessageResponse(BaseModel):
    message: str

class MessageRequest(BaseModel):
    user_id: str
    character_id: str
    message: str

class MessageResponse(BaseModel):
    message: str

class ResetHistoryRequest(BaseModel):
    user_id: int