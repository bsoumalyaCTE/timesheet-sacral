from fastapi import APIRouter, HTTPException, Depends, status
from configs.database import get_db
from configs.schemas.user_schema import signUpModel
from configs.models import User
from lib.helper import get_password_hash


def signup_user_crud(db, user):
    try:
        # Check if the user with email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        # Check if the user with username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        new_user = User(
            username=user.username,
            password=get_password_hash(user.password),  # Hash the password here
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            fax=user.fax,
            mobile=user.mobile,
            other_contact=user.other_contact,
            workday_duration=user.workday_duration,
            hire_date=user.hire_date,
            created=user.created,
            is_enabled=user.is_enabled,
            is_locked=user.is_locked
        )
        db.add(new_user)
        db.commit()
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def login_user_crud(db, user, Authorize):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not db_user.verify_password(user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if db_user.is_locked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is locked")
        if not db_user.is_enabled:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled")
        # Generate JWT token here if needed
        access_token = Authorize.create_access_token(subject=db_user.username, fresh=True, expires_time=3600)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)
        db_user.access_token = access_token
        db_user.refresh_token = refresh_token
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_all_users_crud(db):
    try:
        users = db.query(User).all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_user_by_id_crud(db, user_id):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))