# Production-Grade JWT Refactoring & Best Practices Guide

## Why We Kept the Current Code Minimal (Not Production Version)
We deliberately kept the project code simple and skipped refactoring it to production-grade in the source code.
**Reason:** Injecting full database connections, migrations, configuration classes, and cookie settings adds heavy boilerplate that obscures the fundamental mechanics of the JWT security handshake (Encoding, Decoding, Hashing, and Token extraction). Keeping it local and mock-based allows us to focus strictly on the core logic without debugging setup issues.

---

## What Changes in a Production Environment?

### 1. Database Integration
Instead of keeping a static dictionary like `fake_user_db`, we query a real relational database (e.g., PostgreSQL) through an ORM (like SQLAlchemy).

* **Tutorial Code:**
  ```python
  def get_user(username: str):
      return fake_user_db.get(username)
  ```
* **Production Code:**
  ```python
  def get_user(db: Session, username: str):
      return db.query(DBUser).filter(DBUser.username == username).first()
  ```

### 2. Environment Variables & Settings
Never hardcode `SECRET_KEY` or config details. Load them securely from system variables or `.env` files using Pydantic.

* **Tutorial Code:**
  ```python
  SECRET_KEY = 'my_secret'
  ALGORITHM = 'HS256'
  ```
* **Production Code:**
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      secret_key: str
      algorithm: str = "HS256"
      access_token_expiry_minutes: int = 30

      class Config:
          env_file = ".env"

  settings = Settings()
  ```

### 3. Exposing Only Safe Data (Pydantic Filtering)
Avoid returning internal details like password hashes back to users. Filter out sensitive attributes using output schemas.

* **Production Schema:**
  ```python
  from pydantic import BaseModel, EmailStr

  class UserOut(BaseModel):
      username: str
      email: EmailStr
      is_active: bool
  ```
* **Production Endpoint:**
  ```python
  @app.get("/users/me", response_model=UserOut)
  def get_current_user_profile(user: DBUser = Depends(get_current_active_user)):
      return user  # Fields like hashed_password are automatically filtered out
  ```

### 4. HTTP-Only Cookies (Mitigating XSS)
In standard web apps, storing JWT tokens in Browser LocalStorage makes them vulnerable to Cross-Site Scripting (XSS) scripts. Storing them in `HTTP-Only` cookies prevents client-side JS from reading them.

* **Production Cookie Setup (FastAPI Response):**
  ```python
  @app.post("/token")
  def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
      ...
      token = create_access_token(data={"sub": username})
      response.set_cookie(
          key="access_token",
          value=f"Bearer {token}",
          httponly=True,   # JS cannot access
          secure=True,     # Sent over HTTPS only
          samesite="lax"   # Protection against CSRF
      )
      return {"message": "Logged in successfully"}
  ```

### 5. Token Revocation & Refresh Tokens
* **Access Tokens** should be short-lived (15 minutes).
* **Refresh Tokens** (stored in a secure database/Redis cache) allow users to regenerate access tokens without entering passwords repeatedly.
* A **Redis Blacklist** is used to instantly revoke/de-authorize active tokens (e.g., when a user clicks 'Logout').
