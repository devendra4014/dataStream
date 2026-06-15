from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

# from app.database.duckdb_database import get_db
# from app.utils.passwords import get_password_hash

router = APIRouter()


@router.post("/token")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    return await request.app.state.auth_service.login(
        form_data.username,
        form_data.password,
    )


# @router.post(
#     "/sighup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
# )
# async def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     # Check if user already exists
#     existing_user = (
#         db.query(models.User)
#         .filter(
#             (models.User.email == user.email) | (models.User.username == user.username)
#         )
#         .first()
#     )

#     if existing_user:
#         raise HTTPException(
#             status_code=400, detail="Email or Username already registered"
#         )

#     # Hash the password
#     hashed_password = get_password_hash(user.password)

#     # Create the database object
#     new_user = User(
#         username=user.username, email=user.email, hashed_password=hashed_password
#     )

#     # Save to database
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)  # Retrieves the newly generated ID

#     return new_user
