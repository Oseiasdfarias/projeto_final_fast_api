from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_api_madr.database import get_session
from fast_api_madr.models import Account
from fast_api_madr.schemas import (
    AccountList,
    AccountPublic,
    AccountSchema,
    Message,
)
from fast_api_madr.security import (
    get_current_account,
    get_password_hash,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=AccountPublic)
def create_account(account: AccountSchema, session: T_Session):
    db_account = session.scalar(
        select(Account).where(
            (Account.username == account.username)
            | (Account.email == account.email)
        )
    )
    if db_account:
        if db_account.username == account.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Usermane already exists.",
            )
        elif db_account.email == account.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already exists.",
            )
    db_account = Account(
        username=account.username,
        email=account.email,
        password=get_password_hash(account.password),
    )
    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    return db_account


@router.get("/", response_model=AccountList)
def read_accounts(session: T_Session, limit: int = 10, skip: int = 0):
    accounts = session.scalars(select(Account).limit(limit).offset(skip))

    return {"accounts": accounts}


@router.get("/{account_id}", response_model=AccountPublic)
def read_account(account_id: int, session: T_Session):
    db_account = session.scalar(
        select(Account).where(Account.id == account_id)
    )
    if not db_account:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found."
        )

    return db_account


@router.put("/{account_id}", response_model=AccountPublic)
def update_account(
    account_id: int,
    account: AccountSchema,
    session: T_Session,
    current_account: T_CurrentAccount,
):
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permission."
        )

    current_account.email = account.email
    current_account.username = account.username
    current_account.password = get_password_hash(account.password)

    session.add(current_account)
    session.commit()
    session.refresh(current_account)

    return current_account


@router.delete("/{account_id}", response_model=Message)
def delete_account(
    account_id: int,
    session: T_Session,
    current_account: T_CurrentAccount,
):
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permission."
        )

    session.delete(current_account)
    session.commit()

    return {"message": "Account deleted!"}
