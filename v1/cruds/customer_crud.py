from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from configs.database import get_db
from configs.schemas.customer_schema import *
from configs.models import Customer
from datetime import datetime, date
import os
UPLOAD_DIR = "uploads/customers/"
PREDEFINED_CURRENCIES = ["USD", "EUR", "GBP", "INR"]   Example list of predefined currencies
def notify_customer_addition(customer):
This function should contain the logic to notify the client-side about the new customer addition.
For example, it could send a message to a WebSocket or trigger a server-sent event.
pass
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