from passlib.context import CryptContext
import os
import shutil
from fastapi import HTTPException, status


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password_hash(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def save_file(file, directory):
    """
    Save the uploaded file to the server and return the file path.
    """
    try:
        file_path = os.path.join(directory, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file. Please try again.")
    finally:
        file.file.close()