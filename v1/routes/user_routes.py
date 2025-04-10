from fastapi import APIRouter, HTTPException, Depends, status
from configs.database import get_db
from fastapi_jwt_auth import AuthJWT
from configs.schemas.user_schema import *
from v1.cruds.user_crud import *

user_router = APIRouter(prefix="/user", tags=["Users"])

# @user_router.get("/test")
# async def test_user():
#     return {"users": "This is a user route returning a test message."}

@AuthJWT.load_config
def get_config():
    return tokenSettings()


#/**
# * @api {post} /users/signup Signup User
# * @apiGroup Users
# */
@user_router.post("/signup", response_model=userSignUpResponse, status_code=status.HTTP_201_CREATED, 
    tags=["Users"], summary="User Signup", description="Create a new user.", 
        response_description="User created successfully.")
async def signup_user(user: signUpModel, db=Depends(get_db)):
    crud_response = signup_user_crud(db, user)
    if crud_response:
        return {"status": status.HTTP_200_OK, "message": "User created successfully.", "data": crud_response}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")

#/**
# * @api {post} /users/login Login User
# * @apiGroup Users
# */
@user_router.post("/signin", response_model=userLoginResponse, status_code=status.HTTP_200_OK,
    tags=["Users"], summary="User Signin", description="Authenticate a user.",
        response_description="User logged in successfully.")
async def login_user(user: loginModel, Authorize: AuthJWT = Depends(), db=Depends(get_db)):
    # Authenticate the user
    crud_response = login_user_crud(db, user, Authorize)
    if crud_response:
        return {"status": status.HTTP_200_OK, "message": "User logged in successfully.", "data": crud_response}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")


#/**
# * @api {post} /users/refresh Refresh Token
# * @apiGroup Users
# */
@user_router.post("/refresh", tags=["Users"], summary="Refresh Token", description="Generate a new access token using the refresh token.")
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        # Verify the refresh token
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        # Generate a new access token
        new_access_token = Authorize.create_access_token(subject=current_user, fresh=False)
        return {"status": status.HTTP_200_OK, "message": "Access token refreshed successfully.", "access_token": new_access_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")

#/**
# * @api {post} /users/logout Logout User
# * @apiGroup Users
# */
@user_router.post("/logout", tags=["Users"], summary="Logout User", description="Logout the user by invalidating tokens.")
async def logout_user(Authorize: AuthJWT = Depends()):
    try:
        # Verify the access token
        Authorize.jwt_required()
        # Optionally, you can blacklist the token here if you're using a token blacklist system
        # For now, just revoke the token
        Authorize.unset_jwt_cookies()
        return {"status": status.HTTP_200_OK, "message": "User logged out successfully."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

#/**
# * @api {get} /users/get_all_users Get All Users
# * @apiGroup Users
# */
# @apiSuccess {Object[]} users List of all users.
@user_router.get("/get_all", response_model=userAllResponse, status_code=status.HTTP_200_OK,
    tags=["Users"], summary="List of All Users", description="Retrieve all users.", 
        response_description="List of all users.")
async def get_all_users(db=Depends(get_db), Authorize: AuthJWT = Depends()):
    # Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
    crud_response = get_all_users_crud(db)
    if crud_response:
        return {"status": status.HTTP_200_OK, "message": "Users retrieved successfully.", "data": crud_response}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
    