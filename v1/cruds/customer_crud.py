from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from configs.database import get_db
from configs.schemas.customer_schema import *
from configs.models import Customer, Project, ProjectTeamMember, ProjectRole, AuditTrail
from datetime import datetime, date
import os
import requests
import logging
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from cryptography.fernet import Fernet
from functools import lru_cache
UPLOAD_DIR = "uploads/customers/"
PREDEFINED_CURRENCIES = ["USD", "EUR", "GBP", "INR"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ENCRYPTION_KEY = b'your-encryption-key-here'   Replace with your actual key
cipher = Fernet(ENCRYPTION_KEY)
def encrypt_data(data: str) -> str:
return cipher.encrypt(data.encode()).decode()
def decrypt_data(data: str) -> str:
return cipher.decrypt(data.encode()).decode()
def get_current_user_role(token: str = Depends(oauth2_scheme)):
This function should return the role of the current user based on the token
For example, it could return 'Project Manager', 'Team Member', or 'Viewer'
return "Project Manager"   Placeholder for demonstration
def notify_customer_addition(customer):
This function should contain the logic to notify the client-side about the new customer addition.
For example, it could send a message to a WebSocket or trigger a server-sent event.
pass
def sync_with_crm(db: Session):
try:
crm_api_url = "https://example-crm.com/api/customers"
response = requests.get(crm_api_url)
if response.status_code != 200:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch data from CRM")
crm_customers = response.json()
for crm_customer in crm_customers:
existing_customer = db.query(Customer).filter(Customer.name == crm_customer['name']).first()
if existing_customer:
existing_customer.description = crm_customer['description']
existing_customer.logo = crm_customer['logo']
existing_customer.hourly_rate = crm_customer['hourly_rate']
existing_customer.currency = crm_customer['currency']
else:
new_customer = Customer(
name=crm_customer['name'],
description=crm_customer['description'],
logo=crm_customer['logo'],
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=crm_customer['hourly_rate'],
currency=crm_customer['currency']
)
db.add(new_customer)
db.commit()
logging.info("CRM synchronization completed successfully.")
return {"message": "CRM synchronization completed successfully"}
except Exception as e:
logging.error(f"CRM synchronization failed: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
def check_customer_in_crm(customer_name: str) -> Optional[dict]:
try:
crm_api_url = "https://example-crm.com/api/customers"
response = requests.get(crm_api_url)
if response.status_code != 200:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch data from CRM")
crm_customers = response.json()
for crm_customer in crm_customers:
if crm_customer['name'] == customer_name:
return crm_customer
return None
except Exception as e:
logging.error(f"Failed to check customer in CRM: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
def create_customer_crud(db: Session, customer):
try:
existing_customer = db.query(Customer).filter(Customer.name == customer.name).first()
if existing_customer:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists in local database")
crm_customer = check_customer_in_crm(customer.name)
if crm_customer:
Update local record with CRM data
existing_customer = db.query(Customer).filter(Customer.name == crm_customer['name']).first()
if existing_customer:
existing_customer.description = crm_customer['description']
existing_customer.logo = crm_customer['logo']
existing_customer.hourly_rate = crm_customer['hourly_rate']
existing_customer.currency = crm_customer['currency']
db.commit()
db.refresh(existing_customer)
return existing_customer
else:
new_customer = Customer(
name=encrypt_data(crm_customer['name']),
description=encrypt_data(crm_customer['description']),
logo=crm_customer['logo'],
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=crm_customer['hourly_rate'],
currency=crm_customer['currency']
)
db.add(new_customer)
db.commit()
db.refresh(new_customer)
notify_customer_addition(new_customer)
return new_customer
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
new_customer = Customer(
name=encrypt_data(customer.name),
description=encrypt_data(customer.description),
logo=customer.logo,
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=customer.hourly_rate,
currency=customer.currency
)
db.add(new_customer)
db.commit()
db.refresh(new_customer)
notify_customer_addition(new_customer)
sync_with_crm(db)
return new_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@lru_cache(maxsize=128)
def list_customers_crud(db: Session, page: int = 1, page_size: int = 10, filter: Optional[str] = None, anonymize: bool = False):
try:
sync_with_crm(db)   Synchronize with CRM before listing
query = db.query(Customer)
if filter:
query = query.filter(or_(Customer.name.ilike(f"%{filter}%"), Customer.description.ilike(f"%{filter}%")))
total_customers = query.count()
customers = query.offset((page - 1) * page_size).limit(page_size).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
def anonymize_data(data):
return "Anonymized" if anonymize else decrypt_data(data)
return {
"total": total_customers,
"page": page,
"page_size": page_size,
"customers": [{"id": c.id, "name": anonymize_data(c.name), "description": anonymize_data(c.description)} for c in customers]
}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_customer_crud(db: Session, customer_id: int):
try:
sync_with_crm(db)
customer = db.query(Customer).filter(Customer.id == customer_id).first()
if not customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
customer.name = decrypt_data(customer.name)
customer.description = decrypt_data(customer.description)
return customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def update_customer_crud(db: Session, customer_id: int, customer, current_user_role: str = Depends(get_current_user_role)):
try:
if current_user_role not in ['Project Manager']:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update customer")
existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()
if not existing_customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
existing_customer.name = encrypt_data(customer.name)
existing_customer.description = encrypt_data(customer.description)
if customer.logo:
existing_customer.logo = customer.logo
if customer.hourly_rate is not None:
if customer.hourly_rate < 0 or customer.hourly_rate > 1000:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hourly rate must be between 0 and 1000")
existing_customer.hourly_rate = customer.hourly_rate
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
existing_customer.currency = customer.currency
db.commit()
db.refresh(existing_customer)
logging.info(f"Customer {customer_id} updated by {current_user_role}")
return existing_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def delete_customer_crud(db: Session, customer_id: int):
try:
customer = db.query(Customer).filter(Customer.id == customer_id).first()
if not customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
Securely delete the logo file if it exists
if customer.logo:
existing_logo_path = os.path.join(UPLOAD_DIR, customer.logo)
if os.path.exists(existing_logo_path):
try:
os.remove(existing_logo_path)
except Exception as e:
logging.error(f"Failed to delete logo file: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete logo file")
db.delete(customer)
db.commit()
return {"message": "Customer deleted successfully"}
except Exception as e:
logging.error(f"Failed to delete customer: {str(e)}")
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def list_customers_name(db: Session, page: int = 1, page_size: int = 10, anonymize: bool = False):
try:
sync_with_crm(db)   Synchronize with CRM before listing
query = db.query(Customer)
total_customers = query.count()
customers = query.offset((page - 1) * page_size).limit(page_size).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
def anonymize_data(data):
return "Anonymized" if anonymize else decrypt_data(data)
customer_names = [{"id": customer.id, "name": anonymize_data(customer.name)} for customer in customers]
return {
"total": total_customers,
"page": page,
"page_size": page_size,
"customers": customer_names
}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_all_customers_crud(db: Session):
try:
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return [{"id": c.id, "name": decrypt_data(c.name), "description": decrypt_data(c.description)} for c in customers]
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def add_customer_crud(db: Session, customer):
try:
existing_customer = db.query(Customer).filter(Customer.name == customer.name).first()
if existing_customer:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists")
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
new_customer = Customer(
name=encrypt_data(customer.name),
description=encrypt_data(customer.description),
logo=customer.logo,
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=customer.hourly_rate,
currency=customer.currency
)
db.add(new_customer)
db.commit()
db.refresh(new_customer)
notify_customer_addition(new_customer)
return new_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_customers_for_dropdown(db: Session):
try:
sync_with_crm(db)   Synchronize with CRM before listing
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return [{"id": customer.id, "name": decrypt_data(customer.name)} for customer in customers]
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def assign_project_team_crud(db: Session, project_id: int, team_members: List[dict]):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
total_allocation = 0
for member in team_members:
total_allocation += member['allocation_percentage']
if total_allocation > 100:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total allocation percentage exceeds 100%")
existing_member = db.query(ProjectTeamMember).filter(
ProjectTeamMember.project_id == project_id,
ProjectTeamMember.user_id == member['user_id']
).first()
if existing_member:
existing_member.allocation_percentage = member['allocation_percentage']
else:
new_member = ProjectTeamMember(
project_id=project_id,
user_id=member['user_id'],
allocation_percentage=member['allocation_percentage']
)
db.add(new_member)
db.commit()
return {"message": "Project team assigned successfully"}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def sync_customers_from_crm(db: Session):
try:
crm_api_url = "https://example-crm.com/api/customers"
response = requests.get(crm_api_url)
if response.status_code != 200:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch data from CRM")
crm_customers = response.json()
for crm_customer in crm_customers:
existing_customer = db.query(Customer).filter(Customer.name == crm_customer['name']).first()
if existing_customer:
existing_customer.description = crm_customer['description']
existing_customer.logo = crm_customer['logo']
existing_customer.hourly_rate = crm_customer['hourly_rate']
existing_customer.currency = crm_customer['currency']
else:
new_customer = Customer(
name=crm_customer['name'],
description=crm_customer['description'],
logo=crm_customer['logo'],
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=crm_customer['hourly_rate'],
currency=crm_customer['currency']
)
db.add(new_customer)
db.commit()
logging.info("CRM synchronization completed successfully.")
return {"message": "CRM synchronization completed successfully"}
except Exception as e:
logging.error(f"CRM synchronization failed: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
def synchronize_customer_data(db: Session, background_tasks: BackgroundTasks):
background_tasks.add_task(sync_with_crm, db)
return {"message": "Synchronization task has been scheduled."}
def create_project_crud(db: Session, project):
try:
if not project.name or not project.description or not project.customer_id:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
if project.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
new_project = Project(
name=project.name,
description=project.description,
customer_id=project.customer_id,
billing_option=project.billing_option,
currency=project.currency,
start_date=project.start_date,
end_date=project.end_date
)
db.add(new_project)
db.commit()
db.refresh(new_project)
return new_project
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_project_crud(db: Session, project_id: int):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
return project
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def update_project_crud(db: Session, project_id: int, project, current_user_role: str = Depends(get_current_user_role)):
try:
if current_user_role not in ['Project Manager']:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update project")
existing_project = db.query(Project).filter(Project.id == project_id).first()
if not existing_project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
existing_project.name = project.name
existing_project.description = project.description
existing_project.customer_id = project.customer_id
existing_project.billing_option = project.billing_option
existing_project.currency = project.currency
existing_project.start_date = project.start_date
existing_project.end_date = project.end_date
db.commit()
db.refresh(existing_project)
return existing_project
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def delete_project_crud(db: Session, project_id: int):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
db.delete(project)
db.commit()
return {"message": "Project deleted successfully"}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def create_project_role_crud(db: Session, project_id: int, user_id: int, role: str, current_user_role: str = Depends(get_current_user_role)):
try:
if current_user_role not in ['Project Manager']:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to assign roles")
new_role = ProjectRole(
project_id=project_id,
user_id=user_id,
role=role
)
db.add(new_role)
db.commit()
log_audit_trail(db, project_id, user_id, role, "Assigned")
return {"message": "Role assigned successfully"}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))