import datetime
import logging
from typing import Any, Sequence

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate, Event, AgentRun


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_run(session: Session, status: str = "running") -> AgentRun:
    try:
        run = AgentRun(status=status)
        session.add(run)
        session.commit()
        session.refresh(run)
        return run
    except Exception as e:
        logging.error(f"Error: {e}")
        raise e


def create_event(session: Session, run_id: int, event_data: dict) -> Event:
    logging.warning(f"Creating event: {event_data}")
    event = Event(
        event_data=event_data,
        run_id=run_id,
        inserted_at=datetime.datetime.now()
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def get_run_events(session: Session, run_id: int) -> Sequence[Event]:
    statement = select(Event).where(Event.run_id == run_id)
    return session.exec(statement).all()


def set_run_status(session: Session, run_id: int, status: str) -> AgentRun:
    run = session.get(AgentRun, run_id)
    run.status = status
    session.add(run)
    session.commit()
    session.refresh(run)
    return run
