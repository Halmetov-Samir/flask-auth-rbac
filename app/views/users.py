from app import app
from flask import request, Response, session
from app.models import (
    PasswordService,
    PermissionService,
    UserPermission,
    Validate,
    User,
    UserRepository,

)

from functools import wraps
import json
from http import HTTPStatus


def json_response(data, status=HTTPStatus.OK):
    return Response(json.dumps(data), status=status, mimetype="application/json")


def check_authentication():
    user_id = session.get('user_id')
    if user_id is None:
        return None, json_response(
            {'error': 'Вы не вошли в систему'},
            HTTPStatus.UNAUTHORIZED
        )
    return user_id, None


def find_user_by_id(user_id):
    user = UserRepository.find_by_id(user_id)
    if user is None:
        return None, json_response(
            {'error': 'Пользователь не найден'},
            HTTPStatus.NOT_FOUND
        )
    return user, None


def check_user_active(user):
    if not user.is_active:
        return json_response(
            {'error': 'Учетная запись деактивирована'},
            HTTPStatus.FORBIDDEN
        )
    return None


def get_current_user():
    user_id, error = check_authentication()
    if error:
        return None, error

    user, error = find_user_by_id(user_id)
    if error:
        return None, error

    error = check_user_active(user)
    if error:
        return None, error

    return user, None


def get_valid_json(request):
    data = request.get_json()
    if not data:
        return None, json_response(
            {"error": "JSON обязателен"},
            HTTPStatus.BAD_REQUEST
        )
    return data, None


def login_re(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user, error = get_current_user()
        if error:
            return error
        return func(user, *args, **kwargs)
    return wrapper


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if not PermissionService.has_permission(user.role, permission):
                return json_response(
                    {"error": "Нет прав доступа"},
                    HTTPStatus.FORBIDDEN
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def index():
    return json_response({"message": "hello world"})


@app.post("/users/register")
def users_register():
    data, error = get_valid_json(request)
    if error:
        return error

    required_fields = ["first_name", "last_name", "email", "password", "password_confirm"]
    if not all(field in data for field in required_fields):
        return json_response(
            {"error": "Нужно заполнить все поля"},
            HTTPStatus.BAD_REQUEST
        )

    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    password = data["password"]
    password_confirm = data["password_confirm"]

    if not Validate.is_valid_email(email):
        return json_response(
            {"error": "Неправильный ввод email"},
            HTTPStatus.BAD_REQUEST
        )

    if not Validate.is_valid_password(password):
        return json_response(
            {"error": "Пароль должен содержать минимум 8 символов"},
            HTTPStatus.BAD_REQUEST
        )

    if UserRepository.find_by_email(email):
        return json_response(
            {"error": "email уже зарегистрирован"},
            HTTPStatus.CONFLICT
        )

    if password != password_confirm:
        return json_response(
            {"error": "пароли не совпадают"},
            HTTPStatus.BAD_REQUEST
        )

    user_id = len(UserRepository.USERS)
    password_hash = PasswordService.hash(password)
    role = "admin" if len(UserRepository.USERS) == 0 else "user"

    user = User(user_id, first_name, last_name, email, password_hash,role=role)
    UserRepository.save(user)

    session["user_id"] = user.id

    response_data = user.to_dict()
    response_data["message"] = "Регистрация успешна"

    return json_response(response_data, HTTPStatus.CREATED)


@app.post("/users/login")
def users_login():
    data, error = get_valid_json(request)
    if error:
        return error

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return json_response(
            {"error": "Email и пароль обязательны"},
            HTTPStatus.BAD_REQUEST
        )

    user = UserRepository.find_by_email(email)

    if user is None:
        return json_response(
            {"error": "Пользователь не найден"},
            HTTPStatus.UNAUTHORIZED
        )

    if not PasswordService.verify(password, user.password_hash):
        return json_response(
            {"error": "Неверный пароль"},
            HTTPStatus.UNAUTHORIZED
        )

    if not user.is_active:
        return json_response(
            {"error": "Учетная запись деактивирована"},
            HTTPStatus.FORBIDDEN
        )

    session["user_id"] = user.id

    response_data = user.to_dict()
    response_data["message"] = "Вошли в систему"

    return json_response(response_data)


@app.post("/users/logout")
def users_logout():
    session.pop("user_id", None)
    return json_response({"message": "Вы вышли из системы"})


@app.get("/users/profile")
@login_re
def get_users_profile(user):
    return json_response(user.to_dict(), HTTPStatus.OK)


@app.put("/users/profile")
@login_re
@permission_required(UserPermission.PROFILE_WRITE)
def update_users_profile(user):
    data, error = get_valid_json(request)
    if error:
        return error

    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "password" in data:
        if not Validate.is_valid_password(data["password"]):
            return json_response(
                {"error": "Пароль должен содержать минимум 8 символов"},
                HTTPStatus.BAD_REQUEST
            )
        user.password_hash = PasswordService.hash(data["password"])

    response_data = user.to_dict()
    response_data["message"] = "Данные успешно обновлены"

    return json_response(response_data)


@app.delete("/users/profile")
@login_re
@permission_required(UserPermission.PROFILE_DELETE)
def delete_users_profile(user):
    user.is_active = False
    session.pop("user_id", None)
    return json_response({"message": "Аккаунт успешно удален"})


@app.get("/users")
@login_re
@permission_required(UserPermission.USERS_LIST)
def get_all_users(user):
    users_list = [u.to_dict() for u in UserRepository.get_all_active()]
    return json_response({"users": users_list, "count": len(users_list)}, HTTPStatus.OK)


@app.put("/users/<int:user_id>/role")
@login_re
@permission_required(UserPermission.ROLES_MANAGE)
def change_user_role(user,user_id):
    target_user = UserRepository.find_by_id(user_id)
    if not target_user or not target_user.is_active:
        return json_response(
            {"error": "Пользователь не найден"},
            HTTPStatus.NOT_FOUND
        )

    data, error = get_valid_json(request)
    if error:
        return error

    role = data.get("role")
    valid_roles = ["admin", "user", "guest"]

    if role not in valid_roles:
        return json_response(
            {"error": f"Недопустимая роль. Допустимо: {valid_roles}"},
            HTTPStatus.BAD_REQUEST
        )

    old_role = target_user.role
    target_user.role = role

    return json_response(
        {"message": f"Роль изменена с {old_role} на {role}", "user": target_user.to_dict()},
        HTTPStatus.OK
    )
