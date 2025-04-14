```python
from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from configs.database import get_db
from configs.schemas.customer_schema import *
from v1.cruds.customer_crud import *
from v1.cruds.project_crud import *   Assuming this exists for project CRUD operations
from lib.helper import save_file
import os
import shutil
from celery import Celery
import logging
from typing import List, Optional
from some_mfa_library import verify_mfa   Assuming this is the MFA library
from cryptography.fernet import Fernet   For data encryption
Directory to save uploaded files
UPLOAD_DIR = "uploads/customers/"
Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
Initialize Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0')
Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
customer_router = APIRouter(prefix="/customer", tags=["Customers"])
project_router = APIRouter(prefix="/project", tags=["Projects"])
Predefined list of currencies
CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"]
Role-based access control
ROLES = ["Project Manager", "Team Member", "Viewer", "Admin"]
Function to check if the user has the required role
def check_user_role(required_role: str, Authorize: AuthJWT):
user_roles = Authorize.get_raw_jwt().get("roles", [])
if required_role not in user_roles:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions.")
Function to log actions for audit trail
def log_audit_trail(action: str, user_id: int, details: str):
logger.info(f"Audit Trail - Action: {action}, User ID: {user_id}, Details: {details}")
Encryption key for sensitive data
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)
Create a new customer
@customer_router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
name: str = Form(...),   Accept `name` as a form field
description: Optional[str] = Form(None),   Accept `description` as a form field
logo: UploadFile = File(None),   Accept `logo` as a file
mfa_token: str = Form(...),   Accept MFA token
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):   Verify the JWT token
try:
Authorize.jwt_required()
Verify MFA token
if not verify_mfa(mfa_token):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token.")
Check user role
check_user_role("Project Manager", Authorize)
except HTTPException as e:
raise e
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
Save the uploaded image file if provided
if logo:
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
crud_response = create_customer_crud(db, customer_data)
if crud_response:
Trigger synchronization with CRM after customer creation
sync_with_crm.delay(crud_response.id)
return {"status": status.HTTP_200_OK, "message": "Customer created successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")
Synchronize customer data with CRM
@celery_app.task
def sync_with_crm(customer_id: int):
Logic to synchronize customer data with CRM
This is a placeholder for the actual CRM integration logic
logger.info(f"Synchronizing customer data for customer ID: {customer_id}")
Simulate successful synchronization
logger.info(f"Customer data for customer ID: {customer_id} synchronized successfully.")
New function to fetch and sync customer data from CRM
def sync_customer_with_crm(customer_id: int, db: Session):
try:
Placeholder for CRM API call to fetch customer data
logger.info(f"Fetching customer data from CRM for customer ID: {customer_id}")
Simulate fetching data
crm_data = {"name": "CRM Customer", "description": "Fetched from CRM"}
Update local database with CRM data
update_customer_crud(db, customer_id, crm_data)
logger.info(f"Customer data for customer ID: {customer_id} updated with CRM data.")
except Exception as e:
logger.error(f"Error synchronizing customer data with CRM: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CRM synchronization failed.")
New function to import customers from CRM
def import_customers_from_crm(db: Session):
try:
Placeholder for CRM API call to import customer data
logger.info("Importing customers from CRM...")
Simulate importing data
crm_customers = [{"name": "CRM Customer 1", "description": "Imported from CRM"},
{"name": "CRM Customer 2", "description": "Imported from CRM"}]
for crm_customer in crm_customers:
customer_data = CustomerCreate(
name=crm_customer["name"],
description=crm_customer["description"]
)
create_customer_crud(db, customer_data)
logger.info("Customers imported from CRM successfully.")
except Exception as e:
logger.error(f"Error importing customers from CRM: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CRM import failed.")
Update a customer by ID
@customer_router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
customer_id: int,
name: str = Form(...),   Accept `name` as a form field
description: Optional[str] = Form(None),   Accept `description` as a form field
logo: UploadFile = File(None),   Accept `logo` as a file
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):   Verify the JWT token
try:
Authorize.jwt_required()
Check user role for update operation
check_user_role("Admin", Authorize)
except HTTPException as e:
raise e
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
Synchronize customer data with CRM before updating
sync_customer_with_crm(customer_id, db)
Save the uploaded image file if provided
if logo:
Remove the existing logo file if it exists
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
Log the update action for audit trail
log_audit_trail("Update Customer", Authorize.get_jwt_subject(), f"Updated customer ID: {customer_id}")
Call the synchronization function after updating the customer
synchronize_customer_data.delay(customer_id)
return {"status": status.HTTP_200_OK, "message": "Customer record updated successfully.", "data": crud_response}
Background task to periodically check for updates in the CRM
@celery_app.task
def periodic_crm_sync():
Logic to check for updates in the CRM and synchronize
logger.info("Checking for updates in CRM...")
Simulate CRM update check
logger.info("CRM updates checked and synchronized.")
Schedule the periodic CRM synchronization task
celery_app.conf.beat_schedule = {
'periodic-crm-sync': {
'task': 'periodic_crm_sync',
'schedule': 300.0,   Run every 5 minutes
},
}
Get a single customer by ID
@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
customer_id: int,
include_time_tracking: bool = Query(False),   New query parameter to include time tracking data
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Verify MFA token
mfa_token = "some_mfa_token"   This should be passed as a parameter or obtained from the request
if not verify_mfa(mfa_token):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
crud_response = get_customer_crud(db, customer_id)
if not crud_response:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
Encrypt sensitive data before returning
encrypted_name = cipher_suite.encrypt(crud_response.name.encode()).decode()
encrypted_description = cipher_suite.encrypt(crud_response.description.encode()).decode() if crud_response.description else None
Trigger synchronization with CRM in the background
sync_with_crm.delay(customer_id)
Fetch time tracking data if requested
time_tracking_data = None
if include_time_tracking:
time_tracking_data = get_customer_time_tracking_data(customer_id)
return {
"status": status.HTTP_200_OK,
"message": "Customer Information fetched.",
"data": {
"id": crud_response.id,
"name": encrypted_name,
"description": encrypted_description,
"logo": crud_response.logo,
"time_tracking_data": time_tracking_data   Include time tracking data if available
}
}
Get a list of all customers with filtering and pagination
@customer_router.get("/", response_model=AllCustomerResponse)
def list_customers(
page: int = Query(1, ge=1),   Page number, default is 1
page_size: int = Query(10, ge=1),   Page size, default is 10
anonymize: bool = Query(False),   Option to anonymize customer names
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
check_user_role("Project Manager", Authorize)
except HTTPException as e:
raise e
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
try:
Fetch and sync customer data from CRM
periodic_crm_sync()
crud_response = list_customers_crud(db, page, page_size)
customer_name_response = list_customers_name(db)
if not crud_response:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
Log the access attempt in the audit trail
log_audit_trail("List Customers", Authorize.get_jwt_subject(), "Accessed customer list")
Anonymize customer names if requested
if anonymize:
for customer in crud_response:
customer.name = "Anonymous"
Fetch financial data and merge with customer data
financial_data = fetch_financial_data_for_customers(crud_response)
for customer in crud_response:
customer.financial_data = financial_data.get(customer.id, {})
return {"status": status.HTTP_200_OK, "message": "All Customer Lists.", "data": crud_response, "customer_names": customer_name_response}
except Exception as e:
logger.error(f"Error listing customers: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing customers.")
Delete a customer by ID
@customer_router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
check_user_role("Project Manager", Authorize)   Ensure the user has the necessary role to delete a customer
except HTTPException as e:
raise e
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
crud_response = delete_customer_crud(db, customer_id)
if not crud_response:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
Log the deletion action for audit trail
log_audit_trail("Delete Customer", Authorize.get_jwt_subject(), f"Deleted customer ID: {customer_id}")
return {"status": status.HTTP_200_OK, "message": "Customer record deleted successfully.", "data": crud_response}
Create a new project
@project_router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
name: str = Form(...),
currency: str = Form(...),
customer_id: int = Form(...),   New field for customer selection
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
if currency not in CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected.")
Ensure customer selection is mandatory
if not customer_id:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer selection is mandatory.")
Logic to create a project with the selected currency and customer
Assuming a function `create_project_crud` exists
project_data = {
"name": name,
"currency": currency,
"customer_id": customer_id
}
crud_response = create_project_crud(db, project_data)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "Project created successfully with currency and customer.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project creation failed.")
Update a project by ID
@project_router.put("/{project_id}", status_code=status.HTTP_200_OK)
def update_project(
project_id: int,
name: str = Form(...),
currency: str = Form(...),
customer_id: int = Form(...),   New field for customer selection
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
if currency not in CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected.")
Ensure customer selection is mandatory
if not customer_id:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer selection is mandatory.")
Logic to update a project with the selected currency and customer
Assuming a function `update_project_crud` exists
project_data = {
"name": name,
"currency": currency,
"customer_id": customer_id
}
crud_response = update_project_crud(db, project_id, project_data)
if not crud_response:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
return {"status": status.HTTP_200_OK, "message": "Project updated successfully with currency and customer.", "data": crud_response}
New endpoint to fetch all customers for the dropdown
@customer_router.get("/dropdown", response_model=AllCustomerResponse)
def get_all_customers_for_dropdown(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
crud_response = list_customers_crud(db)
if not crud_response:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return {"status": status.HTTP_200_OK, "message": "All Customer Lists for Dropdown.", "data": crud_response}
New endpoint to add a customer from the 'Select Customer' dropdown
@customer_router.post("/add_from_dropdown", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def add_customer_from_dropdown(
name: str = Form(...),   Accept `name` as a form field
description: Optional[str] = Form(None),   Accept `description` as a form field
logo: UploadFile = File(None),   Accept `logo` as a file
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):   Verify the JWT token
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
Save the uploaded image file if provided
if logo:
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
crud_response = create_customer_crud(db, customer_data)
if crud_response:
Broadcast the update to all active sessions (pseudo-code, implement as needed)
broadcast_update_to_sessions()
return {"status": status.HTTP_200_OK, "message": "Customer added from dropdown successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer addition failed.")
New endpoint to add a project team
@project_router.post("/add_team", status_code=status.HTTP_201_CREATED)
def add_project_team(
project_id: int,
team_members: List[int] = Form(...),   List of team member IDs
allocations: List[float] = Form(...),   Corresponding allocation percentages
db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token