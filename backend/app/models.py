import os
import uuid
from datetime import datetime
from typing import List, Optional, Union

import pytz
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel

TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "Europe/Zurich"))

def get_current_time():
    return datetime.now(TIMEZONE)


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


class AgentRunBase(SQLModel):
    start_time: datetime = Field(default_factory=get_current_time)
    status: str


class EventBase(SQLModel):
    event_data: dict = Field(sa_column=Column(JSON), default={})
    inserted_at: datetime = Field(default_factory=get_current_time)
    run_id: Optional[uuid.UUID] = Field(default=None, foreign_key="agentrun.id")


class Event(EventBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    run: Optional["AgentRun"] = Relationship(back_populates="events")


class AgentRun(AgentRunBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    events: List[Event] = Relationship(back_populates="run")


class AgentRunAndEventsPublic(SQLModel):
    id: uuid.UUID
    start_time: datetime
    status: str
    events: List[Event]


class AgentRunPublic(SQLModel):
    id: uuid.UUID
    start_time: datetime
    status: str


class AgentRunsPublic(SQLModel):
    data: List[AgentRunPublic]
    count: int
