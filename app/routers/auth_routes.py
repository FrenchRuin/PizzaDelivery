from fastapi import APIRouter, HTTPException, status, Depends, Request
from ..db.database import Session, engine
from ..db.schemas import SignUpModel, LoginModel
from ..model.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

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
async def signup(user: SignUpModel):
    """
    ## This Sign Up User
    It requires belong parameters
    - username : "user"
    - password : "password"
    """
    db_email = session.query(User).filter(User.email == user.email).first()

    if db_email is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username = session.query(User).filter(User.username == user.username).first()

    if db_username is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the username already exists"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(new_user)
    session.commit()

    return new_user


# login route
@auth_router.post("/login", status_code=200)
async def login(user: LoginModel, authorize: AuthJWT = Depends()):

    print(user)
    # da = await request.form()
    # print(da.get("username"))

    """
    ## This User Login Service
    It requires belong parameters
    - username : "username"
    - password : "password"
    """
    # db_user = session.query(User).filter(User.username == user.username).first()
    #
    # if db_user and check_password_hash(db_user.password, user.password):
    #     access_token = authorize.create_access_token(subject=db_user.username)
    #     refresh_token = authorize.create_refresh_token(subject=db_user.username)
    #
    #     response = {
    #         "access": access_token,
    #         "refresh": refresh_token
    #     }
    #
    #     return jsonable_encoder(response)
    #
    # raise HTTPException(
    #     status_code=status.HTTP_400_BAD_REQUEST,
    #     detail="Invalid Username or Password"
    # )


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
