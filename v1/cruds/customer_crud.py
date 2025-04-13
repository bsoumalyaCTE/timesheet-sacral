from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from configs.database import get_db
from configs.schemas.customer_schema import *
from configs.models import Customer, Project, ProjectTeamMember   Assuming these models exist
from datetime import datetime, date
import os
import requests   Import requests to handle HTTP requests for CRM integration
import logging   Import logging to log synchronization events
UPLOAD_DIR = "uploads/customers/"
PREDEFINED_CURRENCIES = ["USD", "EUR", "GBP", "INR"]   Example list of predefined currencies
def notify_customer_addition(customer):
This function should contain the logic to notify the client-side about the new customer addition.
For example, it could send a message to a WebSocket or trigger a server-sent event.
pass
def sync_with_crm(db: Session):
try:
Example CRM API endpoint
crm_api_url = "https://example-crm.com/api/customers"
response = requests.get(crm_api_url)
if response.status_code != 200:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch data from CRM")
crm_customers = response.json()
for crm_customer in crm_customers:
existing_customer = db.query(Customer).filter(Customer.name == crm_customer['name']).first()
if existing_customer:
Update existing customer
existing_customer.description = crm_customer['description']
existing_customer.logo = crm_customer['logo']
existing_customer.hourly_rate = crm_customer['hourly_rate']
existing_customer.currency = crm_customer['currency']
else:
Add new customer
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
Log synchronization success
logging.info("CRM synchronization completed successfully.")
return {"message": "CRM synchronization completed successfully"}
except Exception as e:
logging.error(f"CRM synchronization failed: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
def create_customer_crud(db: Session, customer):
try:
Check if the customer with the same name already exists
existing_customer = db.query(Customer).filter(Customer.name == customer.name).first()
if existing_customer:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists")
Validate currency
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
new_customer = Customer(
name=customer.name,
description=customer.description,
logo=customer.logo,
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=customer.hourly_rate,   New field for hourly rate
currency=customer.currency   New field for currency
)
db.add(new_customer)
db.commit()
db.refresh(new_customer)
Notify the client-side about the new customer addition
notify_customer_addition(new_customer)
Initiate synchronization with CRM
sync_with_crm(db)
return new_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def list_customers_crud(db: Session):
try:
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return customers
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_customer_crud(db: Session, customer_id: int):
try:
Ensure data is up-to-date by triggering synchronization if needed
sync_with_crm(db)
customer = db.query(Customer).filter(Customer.id == customer_id).first()
if not customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
return customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def update_customer_crud(db: Session, customer_id: int, customer):
try:
existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()
if not existing_customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
existing_customer.name = customer.name
existing_customer.description = customer.description
If logo is provided, update it
if customer.logo:
existing_customer.logo = customer.logo
Update hourly rate
if customer.hourly_rate is not None:
if customer.hourly_rate < 0 or customer.hourly_rate > 1000:   Example validation range
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hourly rate must be between 0 and 1000")
existing_customer.hourly_rate = customer.hourly_rate
Validate and update currency
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
existing_customer.currency = customer.currency
db.commit()
db.refresh(existing_customer)
return existing_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def delete_customer_crud(db: Session, customer_id: int):
try:
customer = db.query(Customer).filter(Customer.id == customer_id).first()
if customer.logo:
existing_logo_path = os.path.join(UPLOAD_DIR, customer.logo)
if os.path.exists(existing_logo_path):
os.remove(existing_logo_path)
if not customer:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
db.delete(customer)
db.commit()
return {"message": "Customer deleted successfully"}
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def list_customers_name(db: Session):
try:
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
customer_names = [{"id": customer.id, "name": customer.name} for customer in customers]
return customer_names
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def get_all_customers_crud(db: Session):
try:
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return customers
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
def add_customer_crud(db: Session, customer):
try:
Check if the customer with the same name already exists
existing_customer = db.query(Customer).filter(Customer.name == customer.name).first()
if existing_customer:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists")
Validate currency
if customer.currency not in PREDEFINED_CURRENCIES:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid currency selected")
new_customer = Customer(
name=customer.name,
description=customer.description,
logo=customer.logo,
create_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
hourly_rate=customer.hourly_rate,   New field for hourly rate
currency=customer.currency   New field for currency
)
db.add(new_customer)
db.commit()
db.refresh(new_customer)
Notify the client-side about the new customer addition
notify_customer_addition(new_customer)
return new_customer
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
New function to fetch customers for dropdown
def get_customers_for_dropdown(db: Session):
try:
customers = db.query(Customer).all()
if not customers:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
return [{"id": customer.id, "name": customer.name} for customer in customers]
except Exception as e:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
New function to assign project teams
def assign_project_team_crud(db: Session, project_id: int, team_members: list):
try:
Fetch the project
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
Validate and assign team members
total_allocation = 0
for member in team_members:
total_allocation += member['allocation_percentage']
if total_allocation > 100:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total allocation percentage exceeds 100%")
Add or update team member
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
New function to synchronize customers from CRM
def sync_customers_from_crm(db: Session):
try:
Example CRM API endpoint
crm_api_url = "https://example-crm.com/api/customers"
response = requests.get(crm_api_url)
if response.status_code != 200:
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch data from CRM")
crm_customers = response.json()
for crm_customer in crm_customers:
existing_customer = db.query(Customer).filter(Customer.name == crm_customer['name']).first()
if existing_customer:
Update existing customer
existing_customer.description = crm_customer['description']
existing_customer.logo = crm_customer['logo']
existing_customer.hourly_rate = crm_customer['hourly_rate']
existing_customer.currency = crm_customer['currency']
else:
Add new customer
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
Log synchronization success
logging.info("CRM synchronization completed successfully.")
return {"message": "CRM synchronization completed successfully"}
except Exception as e:
logging.error(f"CRM synchronization failed: {str(e)}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
New function to handle background synchronization
def synchronize_customer_data(db: Session, background_tasks: BackgroundTasks):
background_tasks.add_task(sync_with_crm, db)
return {"message": "Synchronization task has been scheduled."}