
Проект демонстрирует разграничение прав доступа между ролями ADMIN, USER и GUEST.

### Основные возможности

Регистрация и аутентификация  пользователей с хешированием паролей
Управление профилем (просмотр, редактирование, мягкое удаление)
Система ролей (ADMIN, USER, GUEST)
Разграничение прав доступа  к ресурсам
CRUD операции для бизнес-объектов (товары)
Сессионная авторизация с защитой

# Права (permissions)
profile.read      - просмотр своего профиля (ADMIN, USER)
profile.write     - изменение своего профиля (ADMIN, USER)
profile.delete    - удаление своего аккаунта (ADMIN, USER)
users.list        - просмотр всех пользователей (ADMIN)
roles.manage      - управление ролями (ADMIN)
products.delete   - удаление товаров (ADMIN)
products.read     - просмотр товаров (ADMIN, USER)
products.write    - создание/изменение (ADMIN)




##  **Пользователи (Users)**

### Регистрация пользователя `POST /users/register`

**Request example:**
```json
{
  "first_name": "Самир",
  "last_name": "Хальметов",
  "email": "samir@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

**Response example (201 Created):**
```json
{
  "id": 0,
  "first_name": "Самир",
  "last_name": "Хальметов",
  "email": "samir@example.com",
  "role": "admin",
  "message": "Регистрация успешна"
}
```


### Вход в систему `POST /users/login`

**Request example:**
```json
{
  "email": "samir@example.com",
  "password": "password123"
}
```

**Response example (200 OK):**
```json
{
  "id": 0,
  "first_name": "Самир",
  "last_name": "Хальметов",
  "email": "samir@example.com",
  "role": "admin",
  "message": "Вошли в систему"
}
```


### Выход из системы `POST /users/logout`

**Request example:** (пустое тело)

**Response example (200 OK):**
```json
{
  "message": "Вы вышли из системы"
}
```



### Получение своего профиля `GET /users/profile`

**Response example (200 OK):**
```json
{
  "id": 0,
  "first_name": "Самир",
  "last_name": "Хальметов",
  "email": "samir@example.com",
  "role": "admin"
}
```


### Обновление своего профиля `PUT /users/profile`

**Request example:**
```json
{
  "first_name": "Самир Рамилевич",
  "password": "newpassword123"
}
```

**Response example (200 OK):**
```json
{
  "id": 0,
  "first_name": "Самир Рамилевич",
  "last_name": "Хальметов",
  "email": "samir@example.com",
  "role": "admin",
  "message": "Данные успешно обновлены"
}
```



### Удаление своего аккаунта (мягкое удаление) `DELETE /users/profile`

**Request example:** (пустое тело)

**Response example (200 OK):**
```json
{
  "message": "Аккаунт успешно удален"
}
```



### Получение всех пользователей (только ADMIN) `GET /users`

**Response example (200 OK):**
```json
{
  "users": [
    {
      "id": 0,
      "first_name": "Самир",
      "last_name": "Хальметов",
      "email": "samir@example.com",
      "role": "admin"
    },
    {
      "id": 1,
      "first_name": "Мария",
      "last_name": "Иванова",
      "email": "maria@example.com",
      "role": "user"
    }
  ],
  "count": 2
}
```


### Изменение роли пользователя (только ADMIN) `PUT /users/{user_id}/role`

**Request example:**
```json
{
  "role": "admin"
}
```

**Response example (200 OK):**
```json
{
  "message": "Роль изменена с user на admin",
  "user": {
    "id": 1,
    "first_name": "Мария",
    "last_name": "Иванова",
    "email": "maria@example.com",
    "role": "admin"
  }
}
```



##  **Товары (Products)**

### Получение всех товаров `GET /products`

**Response example (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Ноутбук",
      "price": 50000,
      "quantity": 10,
      "is_active": true
    },
    {
      "id": 2,
      "name": "Мышь",
      "price": 1000,
      "quantity": 50,
      "is_active": true
    }
  ],
  "count": 2
}
```



### Получение товара по ID `GET /products/{product_id}`

**Response example (200 OK):**
```json
{
  "message": "Вот ваш товар",
  "product": {
    "id": 1,
    "name": "Ноутбук",
    "price": 50000,
    "quantity": 10,
    "is_active": true
  }
}
```

**Response example (404 Not Found):**
```json
{
  "error": "Товар не найден"
}
```



### Создание товара (только ADMIN) `POST /products`

**Request example:**
```json
{
  "name": "Клавиатура",
  "price": 3000,
  "quantity": 15
}
```

**Response example (201 Created):**
```json
{
  "message": "Товар создан",
  "product": {
    "id": 3,
    "name": "Клавиатура",
    "price": 3000,
    "quantity": 15,
    "is_active": true
  }
}
```



### Обновление товара (только ADMIN) `PUT /products/{product_id}`

**Request example (частичное обновление):**
```json
{
  "price": 2500,
  "quantity": 20
}
```

**Response example (200 OK):**
```json
{
  "message": "Товар успешно обновлен",
  "product": {
    "id": 3,
    "name": "Клавиатура",
    "price": 2500,
    "quantity": 20,
    "is_active": true
  }
}
```



### Удаление товара (только ADMIN) `DELETE /products/{product_id}`

**Request example:** (пустое тело)

**Response example (200 OK):**
```json
{
  "message": "Товар удален"
}
