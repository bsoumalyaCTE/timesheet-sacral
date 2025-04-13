from passlib.context import CryptContext
import os
import shutil
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
import hashlib
Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Generate a key for encryption and decryption
In a real-world scenario, this key should be securely stored and managed
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)
Function to hash password
def get_password_hash(password):
return pwd_context.hash(password)
def verify_password_hash(plain_password, hashed_password):
return pwd_context.verify(plain_password, hashed_password)
def save_file(file, directory):
"""
Save the uploaded file to the server securely and return the file path.
"""
try:
Encrypt the file content
file_content = file.file.read()
encrypted_content = cipher_suite.encrypt(file_content)
Generate a hash for file integrity check
file_hash = hashlib.sha256(encrypted_content).hexdigest()
Save the encrypted file
file_path = os.path.join(directory, file.filename)
with open(file_path, "wb") as buffer:
buffer.write(encrypted_content)
Save the hash for integrity verification
hash_path = file_path + ".hash"
with open(hash_path, "w") as hash_file:
hash_file.write(file_hash)
return file_path
except Exception as e:
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