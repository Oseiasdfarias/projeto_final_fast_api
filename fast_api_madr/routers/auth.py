from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_api_madr.database import get_session
from fast_api_madr.models import Account
from fast_api_madr.schemas import Token
from fast_api_madr.security import (
    create_access_token,
    get_current_account,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
T_Session = Annotated[Session, Depends(get_session)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=Token)
def login_for_access_token(
    session: T_Session,
    form_data: T_OAuthForm,
):
    account = session.scalar(
        select(Account).where(Account.email == form_data.username)
    )

    if not account or not verify_password(
        form_data.password, account.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect email or password.",
        )

    access_token = create_access_token(data={"sub": account.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
def refresh_access_token(
    account: Account = Depends(get_current_account),
):
    new_access_token = create_access_token(data={"sub": account.email})

    return {"access_token": new_access_token, "token_type": "bearer"}
