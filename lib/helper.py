from passlib.context import CryptContext
import os
import shutil
from fastapi import HTTPException, status, UploadFile
from cryptography.fernet import Fernet
import hashlib
import logging
Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Generate a key for encryption and decryption
In a real-world scenario, this key should be securely stored and managed
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)
Configure logging
logging.basicConfig(filename='file_uploads.log', level=logging.INFO, format='%(asctime)s - %(message)s')
Function to hash password
def get_password_hash(password):
return pwd_context.hash(password)
def verify_password_hash(plain_password, hashed_password):
return pwd_context.verify(plain_password, hashed_password)
def save_file(file: UploadFile, directory: str):
"""
Save the uploaded file to the server securely and return the file path.
"""
try:
Validate file type and size
if not file.content_type.startswith('application/'):
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type.")
if file.spool_max_size > 10 * 1024 * 1024:   10 MB limit
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds limit.")
Encrypt the file content
file_content = file.file.read()
encrypted_content = cipher_suite.encrypt(file_content)
Generate a hash for file integrity check
file_hash = hashlib.sha256(encrypted_content).hexdigest()
Ensure the directory exists
os.makedirs(directory, exist_ok=True)
Save the encrypted file
file_path = os.path.join(directory, file.filename)
with open(file_path, "wb") as buffer:
buffer.write(encrypted_content)
Save the hash for integrity verification
hash_path = file_path + ".hash"
with open(hash_path, "w") as hash_file:
hash_file.write(file_hash)
Log the file upload event
logging.info(f"File uploaded: {file.filename}, Path: {file_path}")
return file_path
except Exception as e:
logging.error(f"Error uploading file: {file.filename}, Error: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file. Please try again.")
finally:
file.file.close()
Example function for data anonymization/pseudonymization
def anonymize_data(data):
Implement anonymization logic here
This is a placeholder for demonstration purposes
return "anonymized_" + data
Example usage of anonymization
def process_file(file_path):
Read the file content
with open(file_path, "rb") as file:
content = file.read()
Anonymize the content
anonymized_content = anonymize_data(content.decode())
Save the anonymized content back to the file
with open(file_path, "wb") as file:
file.write(anonymized_content.encode())