### Документація Bookmark API

#### Вступ

Ця документація надає огляд Bookmark API, яке є веб-застосунком, створеним за допомогою Flask. API дозволяє користувачам створювати, керувати та доступатись до закладок. У наступних розділах описуються ключові моменти API: точки доступу, формати запитів/відповідей, авторизація та обробка помилок.

---

#### Зміст:
1. [Точки доступу API](#api-endpoints)
2. [Формати запитів/відповідей](#requestresponse-formats)
3. [Авторизація](#authentication)
4. [Обробка помилок](#error-handling)

---

### Точки доступу API

#### Реєстрація користувача

**Endpoint:** `POST /api/v1/auth/register`

**Опис:** Зарестровує нового користувача.

**Тіло запиту:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Тіло відповіді:**
```json
{
  "message": "User registered successfully."
}
```

---

#### Логін користувача

**Endpoint:** `POST /api/v1/auth/login`

**Опис:** Авторизує користувача та повертає JSON Web Token (JWT).

**Тіло запиту:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Тіло відповіді:**
```json
{
  "access_token": "string"
}
```

---

#### Створення закладки

**Endpoint:** `POST /api/v1/bookmarks`

**Опис:** Створює нову закладку для авторизованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

**Тіло запиту:**
```json
{
  "title": "string",
  "url": "string",
  "description": "string"
}
```

**Тіло відповіді:**
```json
{
  "bookmark_id": "integer",
  "title": "string",
  "url": "string",
  "description": "string",
  "created_at": "datetime"
}
```

---

### Створити Закладку

**Endpoint:** `POST /api/bookmarks`

**Опис:**  Створює нову закладку для автентифікованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

**Тіло запиту:**
```json
{
  "title": "string",
  "url": "string",
  "description": "string"
}
```

**Тіло відповіді:**
```json
{
  "bookmark_id": "integer",
  "title": "string",
  "url": "string",
  "description": "string",
  "created_at": "datetime"
}
```

### Отримати всі Закладки

**Endpoint:** `GET /api/bookmarks`

**Опис:**  Повертає всі закладки автентифікованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

**Тіло відповіді:**
```json
[
  {
    "bookmark_id": "integer",
    "title": "string",
    "url": "string",
    "description": "string",
    "created_at": "datetime"
  },
  ...
]
```

### Отримати Закладку за ID

**Endpoint:** `GET /api/bookmarks/<bookmark_id>`

**Опис:**  Повертає конкретну закладку за її ID для автентифікованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

Т**Тіло відповіді:**
```json
{
  "bookmark_id": "integer",
  "title": "string",
  "url": "string",
  "description": "string",
  "created_at": "datetime"
}
```

### Оновити Закладку

**Endpoint:** `PUT /api/bookmarks/<bookmark_id>`

**Опис:**  Оновлює конкретну закладку за її ID для автентифікованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

Тіло запиту:
```json
{
  "title": "string",
  "url": "string",
  "description": "string"
}
```

**Тіло відповіді:**
```json
{
  "message": "Bookmark updated successfully."
}
```

### Видалити Закладку

**Endpoint:** `DELETE /api/bookmarks/<bookmark_id>`

**Опис:**  Видаляє конкретну закладку за її ID для автентифікованого користувача.

**Заголовки запиту:**
```
Authorization: Bearer <access_token>
```

**Тіло відповіді:**
```json
{
  "message": "Bookmark deleted successfully."
}
```

## Формати Запитів/Відповідей

### Тіло Запиту

Тіло запиту має бути відформатоване як JSON.

### Тіло Відповіді

Тіло відповіді має бути відформатоване як JSON.

## Аутентифікація

API Закладок використовує JSON Web Tokens (JWT) для автентифікації. Щоб автентифікувати користувача, зробіть POST-запит на /api/auth/login з обліковими даними користувача. API поверне токен доступу, який потрібно включити в заголовок Authorization наступних запитів у форматі Bearer <access_token>.

## Обробка Помилок

API Закладок повертає помилки з тілом відповіді у форматі JSON і відповідним кодом статусу HTTP.

### Тіло Відповіді при Помилці

```json
{
  "message": "string"
}
```

### Коди Статусів Помилок

- 400 Bad Request: Запит є недійсним або містить відсутні обов’язкові параметри.
- 401 Unauthorized: Запит не автентифіковано або токен доступу є недійсним.
- 403 Forbidden: Автентифікований користувач не має дозволу на виконання запитаної дії.
- 404 Not Found: Запитуваний ресурс або кінцева точка не існує.
- 500 Internal Server Error: Неочікувана помилка на сервері.





