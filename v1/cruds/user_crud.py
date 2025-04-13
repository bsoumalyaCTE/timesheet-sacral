from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from configs.database import get_db
from configs.schemas.user_schema import signUpModel
from configs.models import User, Project, Customer, ProjectTeam   Assuming ProjectTeam model exists
from lib.helper import get_password_hash
from datetime import datetime, timedelta
Assuming CRM integration functions
def synchronize_crm_data(db, user):
try:
Placeholder for CRM synchronization logic
This function should handle the integration with the CRM system
and update the User model with synchronization status and timestamps
user.last_sync_time = datetime.utcnow()
user.sync_status = "Success"
db.commit()
except Exception as e:
user.sync_status = "Failed"
db.commit()
raise HTTPException(status_code=400, detail=f"CRM synchronization failed: {str(e)}")
def periodic_crm_sync(db):
try:
Placeholder for periodic CRM synchronization logic
This function should be run as a background task
users = db.query(User).all()
for user in users:
synchronize_crm_data(db, user)
except Exception as e:
raise HTTPException(status_code=400, detail=f"Periodic CRM synchronization failed: {str(e)}")
def signup_user_crud(db, user):
try:
existing_email = db.query(User).filter(User.email == user.email).first()
if existing_email:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
existing_user = db.query(User).filter(User.username == user.username).first()
if existing_user:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
new_user = User(
username=user.username,
password=get_password_hash(user.password),
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
is_locked=user.is_locked,
last_sync_time=None,
sync_status=None
)
db.add(new_user)
db.commit()
return new_user
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
def login_user_crud(db, user, Authorize, background_tasks: BackgroundTasks):
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
Synchronize CRM data after successful login
synchronize_crm_data(db, db_user)
Add background task for periodic CRM synchronization
background_tasks.add_task(periodic_crm_sync, db)
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
Fetch current allocation for each user
user_data = []
for user in users:
current_allocation = db.query(ProjectTeam).filter(ProjectTeam.user_id == user.id).all()
total_allocation = sum([team.allocation for team in current_allocation])
user_data.append({
"user": user,
"current_allocation": total_allocation
})
return user_data
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
def get_project_billing_option_crud(db, project_id):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
return project.billing_option
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
def update_project_billing_option_crud(db, project_id, billing_option):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
project.billing_option = billing_option
db.commit()
return project
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
def save_project_billing_option_crud(db, project):
try:
db.add(project)
db.commit()
return project
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
New CRUD functions for Project module
def add_project_crud(db, project_data, user):
try:
Check if user is authorized
if not user.is_authorized:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to add projects")
Create new project
new_project = Project(
name=project_data.name,
description=project_data.description,
customer_id=project_data.customer_id,
start_date=project_data.start_date,
end_date=project_data.end_date,
billing_option=project_data.billing_option
)
db.add(new_project)
db.commit()
return new_project
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
def update_customer_list_crud(db, new_customer_data):
try:
Add new customer
new_customer = Customer(
name=new_customer_data.name,
email=new_customer_data.email,
phone=new_customer_data.phone
)
db.add(new_customer)
db.commit()
Return updated customer list
customers = db.query(Customer).all()
return customers
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
New functions for project team management
def assign_project_team_crud(db, project_id, team_data):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
total_allocation = sum(member['allocation'] for member in team_data)
if total_allocation > 100:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total allocation exceeds 100%")
for member in team_data:
user = db.query(User).filter(User.id == member['user_id']).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {member['user_id']} not found")
project_team = ProjectTeam(
project_id=project_id,
user_id=member['user_id'],
allocation=member['allocation']
)
db.add(project_team)
db.commit()
return {"message": "Project team assigned successfully"}
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
def update_project_team_crud(db, project_id, team_data):
try:
project = db.query(Project).filter(Project.id == project_id).first()
if not project:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
total_allocation = sum(member['allocation'] for member in team_data)
if total_allocation > 100:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total allocation exceeds 100%")
Clear existing team assignments
db.query(ProjectTeam).filter(ProjectTeam.project_id == project_id).delete()
for member in team_data:
user = db.query(User).filter(User.id == member['user_id']).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {member['user_id']} not found")
project_team = ProjectTeam(
project_id=project_id,
user_id=member['user_id'],
allocation=member['allocation']
)
db.add(project_team)
db.commit()
return {"message": "Project team updated successfully"}
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))