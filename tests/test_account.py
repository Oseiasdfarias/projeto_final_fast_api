from http import HTTPStatus

from fast_api_madr.schemas import AccountPublic


def test_create_account_username_existing(client, account):
    response = client.post(
        "/accounts/",
        json={
            "username": account.username,
            "email": "user@example.com",
            "password": "string",
        },
    )

    # Validar UserPublic
    assert response.status_code == HTTPStatus.BAD_REQUEST  # Assert (Afirmação)
    assert response.json() == {"detail": "Usermane already exists."}


def test_create_account_email_existing(client, account):
    response = client.post(  # UserScrema
        "/accounts/",
        json={
            "username": "teste",
            "email": account.email,
            "password": "string",
        },
    )

    # Validar UserPublic
    assert response.status_code == HTTPStatus.BAD_REQUEST  # Assert (Afirmação)
    assert response.json() == {"detail": "Email already exists."}


def test_create_account(client):
    response = client.post(  # AccountScrema
        "/accounts/",
        json={
            "username": "test_test",
            "email": "test_test@example.com",
            "password": "string",
        },
    )

    # Validar UserPublic
    assert response.status_code == HTTPStatus.CREATED  # Assert (Afirmação)
    assert response.json() == {
        "username": "test_test",
        "email": "test_test@example.com",
        "id": 1,
    }


def test_read_accounts(client):
    response = client.get("/accounts")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"accounts": []}


def test_read_accounts_with_account(client, account, other_account):
    account_schema = AccountPublic.model_validate(account).model_dump()
    other_account_schema = AccountPublic.model_validate(
        other_account
    ).model_dump()
    response = client.get("/accounts")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "accounts": [account_schema, other_account_schema]
    }


def test_read_account(client):
    response = client.get("/accounts/1")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found."}


def test_read_account_with_account(client, account):
    account_schema = AccountPublic.model_validate(account).model_dump()
    response = client.get(f"/accounts/{account.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == account_schema


def test_update_account(client, account, token):
    response = client.put(
        f"/accounts/{account.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password": "123",
            "username": "test_username",
            "email": "user@example.com",
            "id": account.id,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "test_username",
        "email": "user@example.com",
        "id": account.id,
    }


def test_update_account_not_found(client, other_account, token):
    response = client.put(
        f"/accounts/{other_account.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password": "123",
            "username": "test_username",
            "email": "user@example.com",
            "id": 2,
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permission."}


def test_delete_account(client, account, token):
    response = client.delete(
        f"/accounts/{account.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Account deleted!"}


def test_delete_account_not_permission(client, account, other_account, token):
    response = client.delete(
        f"/accounts/{other_account.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permission."}


def test_delete_account_not_found(client, other_account):
    response = client.delete(f"/accounts/{other_account.id}")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
