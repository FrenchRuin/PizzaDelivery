from fastapi import APIRouter, HTTPException, status, Depends, Request
from ..db.database import Session, engine
from ..db.schemas import SignUpModel, LoginModel
from ..model.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

session = Session(bind=engine)


@auth_router.get("/")
async def hello(authorize: AuthJWT = Depends()):
    """
    ## This just return Hello world
    It requires JWT Auth
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return {"message": "Hello World"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: Request):
    """
    ## This Sign Up User
    It requires belong parameters
    - username : "username"
    - password : "password"
    """
    signup_info = await request.form()
    print(signup_info)
    username = signup_info.get("username")
    email = signup_info.get("email")
    password = signup_info.get("password")

    db_email = session.query(User).filter(User.email == email).first()

    if db_email is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username = session.query(User).filter(User.username == username).first()

    if db_username is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the username already exists"
        )

    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        is_active=True,
        is_staff=False,
    )

    session.add(new_user)
    session.commit()

    return new_user


# login route
@auth_router.post("/login", status_code=200)
async def login(request: Request, authorize: AuthJWT = Depends()):
    """
    ## This User Login Service
    It requires belong parameters
    - username : "username"
    - password : "password"
    """
    login_info = await request.form()
    username = login_info.get("username")
    password = login_info.get("password")

    db_user = session.query(User).filter(User.username == username).first()

    if db_user and check_password_hash(db_user.password, password):
        access_token = authorize.create_access_token(subject=db_user.username)
        refresh_token = authorize.create_refresh_token(subject=db_user.username)

        tokens = {
            "access": access_token,
            "refresh": refresh_token,
        }

        response = JSONResponse(tokens)
        response.set_cookie(
            "refreshToken",
            refresh_token,
            secure=True,
            httponly=True
        )  # To protect Danger

        return response

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid Username or Password"
    )


# refreshing Token
@auth_router.get("/refresh")
async def refresh_token(authorize: AuthJWT = Depends()):
    """
    ## This is Token Refresh Service
    It requires JWT Auth
    """
    try:
        authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token"
        )

    current_user = authorize.get_jwt_subject()

    access_token = authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access": access_token})
