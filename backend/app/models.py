from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str
    description: str | None = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


class ToolCall(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    function_name: str
    arguments: str
    ai_message_id: Optional[int] = Field(default=None, foreign_key="message.id")


class MessageBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_type: str = Field(index=True)
    content: str
    run_id: Optional[int] = Field(default=None, foreign_key="agentrun.id")
    run: Optional["AgentRun"] = Relationship(back_populates="messages")
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

    @declared_attr
    def __tablename__(cls):
        return "message"


class HumanMessage(MessageBase, table=True):
    __mapper_args__ = {'polymorphic_identity': 'human_message'}


class ToolMessage(MessageBase, table=True):
    __mapper_args__ = {'polymorphic_identity': 'tool_message'}


class AIMessage(MessageBase, table=True):
    __mapper_args__ = {'polymorphic_identity': 'ai_message'}
    tool_calls: List[ToolCall] = Relationship(back_populates="ai_message")


class AgentRunBase(SQLModel):
    start_time: datetime
    status: str


class AgentRun(AgentRunBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    messages: List[MessageBase] = Relationship(back_populates="run")


class AgentRunPublic(SQLModel):
    id: int
    start_time: datetime
    status: str
    messages: List[MessageBase]


class AgentRunsPublic(SQLModel):
    data: List[AgentRunPublic]
    count: int
