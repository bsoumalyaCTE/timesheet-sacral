from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from configs.database import get_db
from configs.schemas.customer_schema import *
from v1.cruds.customer_crud import *

from lib.helper import save_file
import os
import shutil

# Directory to save uploaded files
UPLOAD_DIR = "uploads/customers/"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

customer_router = APIRouter(prefix="/customer", tags=["Customers"])


# Create a new customer
@customer_router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    name: str = Form(...),  # Accept `name` as a form field
    description: Optional[str] = Form(None),  # Accept `description` as a form field
    logo: UploadFile = File(None),  # Accept `logo` as a file
    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):# Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")

    # Save the uploaded image file if provided
    if logo:
        logo_path = save_file(logo, UPLOAD_DIR)

    customer_data = CustomerCreate(
        name=name,
        description=description,
        logo=logo_path
    )
    crud_response = create_customer_crud(db, customer_data)
    if crud_response:
        return {"status": status.HTTP_200_OK, "message": "Customer created successfully.", "data": crud_response}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")

# Update a customer by ID
@customer_router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int, 
    name: str = Form(...),  # Accept `name` as a form field
    description: Optional[str] = Form(None),  # Accept `description` as a form field
    logo: UploadFile = File(None),  # Accept `logo` as a file
    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")

    # Save the uploaded image file if provided
    if logo:
        # Remove the existing logo file if it exists
        existing_customer = get_customer_crud(db, customer_id)
        if existing_customer and existing_customer.logo:
            existing_logo_path = os.path.join(UPLOAD_DIR, existing_customer.logo)
            if os.path.exists(existing_logo_path):
                os.remove(existing_logo_path)
        
        logo_path = save_file(logo, UPLOAD_DIR)
        customer_data = CustomerCreate(
            name=name,
            description=description,
            logo=logo_path
        )
    else:
        customer_data = CustomerCreate(
            name=name,
            description=description
        )
    
    crud_response = update_customer_crud(db, customer_id, customer_data)
    if not crud_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return {"status": status.HTTP_200_OK, "message": "Customer record updated successfully.", "data": crud_response}

# Get a single customer by ID
@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
    crud_response = get_customer_crud(db, customer_id)
    if not crud_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return {"status": status.HTTP_200_OK, "message": "Customer Information fetched.", "data": crud_response}

# Get a list of all customers
@customer_router.get("/", response_model=AllCustomerResponse)
def list_customers(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
    crud_response = list_customers_crud(db)
    customer_name_response = list_customers_name(db)
    if not crud_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
    return {"status": status.HTTP_200_OK, "message": "All Customer Lists.", "data": crud_response, "customer_names": customer_name_response}

# Delete a customer by ID
@customer_router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Verify the JWT token
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
    crud_response = delete_customer_crud(db, customer_id)
    if not crud_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return {"status": status.HTTP_200_OK, "message": "Customer record deleted successfully.", "data": crud_response}