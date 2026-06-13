from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.user_model import UserResponse, UserCreate, User
from app.database.duckdb_database import get_db
from app.utils.passwords import get_password_hash

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(credentials: LoginRequest):
    # Mock authentication for Step 1
    if credentials.email == "admin@test.com" and credentials.password == "admin123":
        # In the future, this will be a real JWT token
        return {"access_token": "fake-jwt-token-12345", "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )


@router.post(
    "/sighup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = (
        db.query(models.User)
        .filter(
            (models.User.email == user.email) | (models.User.username == user.username)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email or Username already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create the database object
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Retrieves the newly generated ID

    return new_user
