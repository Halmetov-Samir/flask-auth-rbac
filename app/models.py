import re
from passlib.hash import pbkdf2_sha256
from abc import ABC, abstractmethod


class BasePermission(ABC):
    @classmethod
    @abstractmethod
    def get_permissions(cls):
        pass

    @classmethod
    @abstractmethod
    def get_role_permissions(cls):
        pass

    @classmethod
    def check_permission(cls, role, permission):
        role_permissions = cls.get_role_permissions()
        if role not in role_permissions:
            return False
        return permission in role_permissions[role]


class User:
    def __init__(self, id, first_name, last_name, email, password_hash, role="user"):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role,
        }


class PasswordService:
    @staticmethod
    def hash(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify(password, password_hash):
        return pbkdf2_sha256.verify(password, password_hash)


class PermissionService:
    @staticmethod
    def has_permission(user_role, permission):
        permission_classes = [UserPermission, ProductPermission]
        for perm_class in permission_classes:
            if perm_class.check_permission(user_role, permission):
                return True
        return False


class UserRepository:
    USERS = []

    @classmethod
    def save(cls, user: User):
        cls.USERS.append(user)

    @classmethod
    def find_by_id(cls, user_id: int):
        return next((u for u in cls.USERS if u.id == user_id), None)

    @classmethod
    def find_by_email(cls, email: str):
        return next((u for u in cls.USERS if u.email == email), None)

    @classmethod
    def get_all_active(cls):
        return [u for u in cls.USERS if u.is_active]


class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.is_active = True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "is_active": self.is_active,
        }


class ProductRepository:
    PRODUCTS = []

    @classmethod
    def save(cls, product: Product):
        cls.PRODUCTS.append(product)

    @classmethod
    def find_by_id(cls, product_id: int):
        return next((p for p in cls.PRODUCTS if p.id == product_id), None)

    @classmethod
    def get_all(cls):
        return cls.PRODUCTS

    @classmethod
    def delete(cls, product: Product):
        cls.PRODUCTS.remove(product)


class Role:
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

    @classmethod
    def get_role(cls):
        return [cls.ADMIN, cls.USER, cls.GUEST]


class UserPermission(BasePermission):
    PROFILE_READ = "profile.read"
    PROFILE_WRITE = "profile.write"
    PROFILE_DELETE = "profile.delete"
    USERS_LIST = "users.list"
    ROLES_MANAGE = "roles.manage"

    @classmethod
    def get_permissions(cls):
        return [
            cls.PROFILE_READ,
            cls.PROFILE_WRITE,
            cls.PROFILE_DELETE,
            cls.USERS_LIST,
            cls.ROLES_MANAGE,
        ]

    @classmethod
    def get_role_permissions(cls):
        return {
            Role.ADMIN: [
                cls.PROFILE_READ,
                cls.PROFILE_WRITE,
                cls.PROFILE_DELETE,
                cls.USERS_LIST,
                cls.ROLES_MANAGE,
            ],
            Role.USER: [cls.PROFILE_READ, cls.PROFILE_WRITE, cls.PROFILE_DELETE],
            Role.GUEST: [cls.PROFILE_READ],
        }


class ProductPermission(BasePermission):
    PRODUCTS_READ = "products.read"
    PRODUCTS_WRITE = "products.write"
    PRODUCTS_DELETE = "products.delete"

    @classmethod
    def get_permissions(cls):
        return [cls.PRODUCTS_READ, cls.PRODUCTS_WRITE, cls.PRODUCTS_DELETE]

    @classmethod
    def get_role_permissions(cls):
        return {
            Role.ADMIN: [cls.PRODUCTS_READ, cls.PRODUCTS_WRITE, cls.PRODUCTS_DELETE],
            Role.USER: [cls.PRODUCTS_READ],
            Role.GUEST: [],
        }


class Validate:
    MIN_PASSWORD_LENGTH = 8

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not isinstance(email, str):
            return False

        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    @classmethod
    def is_valid_password(cls, password: str) -> bool:
        if not isinstance(password, str):
            return False

        return len(password) >= cls.MIN_PASSWORD_LENGTH