from services.user_service import UserService


def test_create_and_get_user():
    service = UserService()

    user = service.get_or_create_user(
        user_id=999,
        username="test_user",
    )

    saved_user = service.get_user(999)

    assert saved_user is not None
    assert saved_user.user_id == user.user_id
    assert saved_user.username == "test_user"


def test_username_update():
    service = UserService()

    service.get_or_create_user(
        user_id=888,
        username="old_name",
    )

    user = service.get_or_create_user(
        user_id=888,
        username="new_name",
    )

    assert user.user_id == 888
    assert user.username == "new_name"
