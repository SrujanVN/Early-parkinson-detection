# Authentication API Documentation

## Overview
The authentication system provides secure user registration, login, and session management for the Parkinson's Detection application.

## Database Schema
The SQLite database (`lungvision.db`) contains a `users` table with the following structure:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Patient', 'Researcher')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Endpoints

### 1. Register User
**Endpoint:** `POST /api/register`

**Description:** Register a new user account

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "role": "Patient"  // or "Researcher"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user_id": 1,
    "email": "user@example.com",
    "role": "Patient"
}
```

**Error Responses:**
- `400 Bad Request`: Missing email or password
- `409 Conflict`: Email already registered
- `500 Internal Server Error`: Server error

---

### 2. Login
**Endpoint:** `POST /api/login`

**Description:** Authenticate user and create session

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "role": "Patient"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Missing email or password
- `401 Unauthorized`: Invalid email or password

**Note:** Session cookie is automatically set on successful login.

---

### 3. Get Current User
**Endpoint:** `GET /api/me`

**Description:** Get information about the currently authenticated user

**Headers:**
- Session cookie must be included (automatically handled by browser)

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "role": "Patient"
    }
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

### 4. Logout
**Endpoint:** `POST /api/logout`

**Description:** Logout user and clear session

**Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

---

## Password Security

The system uses `werkzeug.security` for password hashing:
- **Function:** `generate_password_hash(password)` - Used during registration
- **Function:** `check_password_hash(stored_hash, submitted_password)` - Used during login

Passwords are:
- Hashed using PBKDF2 with SHA-256
- Never stored in plain text
- Minimum 6 characters required

## Session Management

- Sessions are managed using Flask-Session
- Session data stored in filesystem
- Session cookies are:
  - HttpOnly (prevents XSS attacks)
  - SameSite=Lax (CSRF protection)
  - Secure in production (HTTPS required)

## Protected Routes

Routes can be protected using decorators:

```python
@login_required  # Requires authentication
def protected_route():
    # Access user info via session
    user_id = session.get('user_id')
    role = session.get('role')
    ...

@role_required('Researcher')  # Requires specific role
def researcher_only_route():
    ...
```

## Testing

### Using the Test Script
```bash
cd backend
python test_auth.py
```

### Using the HTML Test Page
1. Open `test_auth.html` in your browser
2. Register a new user or login with existing credentials
3. Test protected endpoints

### Using cURL

**Register:**
```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"Patient"}'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Get Current User:**
```bash
curl -X GET http://127.0.0.1:5000/api/me \
  -b cookies.txt
```

## Security Best Practices

1. ✅ Passwords are hashed using PBKDF2
2. ✅ Session cookies are HttpOnly
3. ✅ SQL injection protection (parameterized queries)
4. ✅ Email uniqueness enforced
5. ✅ Role-based access control ready
6. ⚠️ In production, enable HTTPS and set `SESSION_COOKIE_SECURE = True`
7. ⚠️ Consider rate limiting for login/register endpoints
8. ⚠️ Add email verification for production use
