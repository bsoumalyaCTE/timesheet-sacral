from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from configs.database import get_db
from configs.schemas.user_schema import signUpModel
from configs.models import User, Project, Customer, ProjectTeam, AuditTrail   Assuming ProjectTeam and AuditTrail models exist
from lib.helper import get_password_hash, verify_mfa, encrypt_data, decrypt_data   Assuming these functions exist
from datetime import datetime, timedelta
import asyncio   Import asyncio for asynchronous tasks
Assuming CRM integration functions
async def synchronize_user_with_crm(db, user):
try:
CRM synchronization logic
This function should handle the integration with the CRM system
and update the User model with synchronization status and timestamps
user.last_sync_time = datetime.utcnow()
user.sync_status = "Success"
db.commit()
Log successful synchronization
print(f"User {user.username} synchronized successfully at {user.last_sync_time}")
except Exception as e:
user.sync_status = "Failed"
db.commit()
raise HTTPException(status_code=400, detail=f"CRM synchronization failed: {str(e)}")
async def periodic_crm_sync(db):
try:
Periodic CRM synchronization logic
This function should be run as a background task
users = db.query(User).all()
for user in users:
await synchronize_user_with_crm(db, user)
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
sync_status=None,
role='Viewer'   Default role
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
Check if MFA is enabled and verify
if db_user.mfa_enabled:
if not verify_mfa(user.mfa_token):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA verification failed")
Synchronize CRM data after successful login
asyncio.run(synchronize_user_with_crm(db, db_user))
Add background task for periodic CRM synchronization
background_tasks.add_task(periodic_crm_sync, db)
Create and encrypt access and refresh tokens
access_token = Authorize.create_access_token(subject=db_user.username, fresh=True, expires_time=3600)
refresh_token = Authorize.create_refresh_token(subject=db_user.username)
db_user.access_token = encrypt_data(access_token)
db_user.refresh_token = encrypt_data(refresh_token)
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
New function for role assignment
def assign_role_to_user_crud(db, project_manager_id, user_id, role):
try:
Verify if the user is a project manager
project_manager = db.query(User).filter(User.id == project_manager_id).first()
if not project_manager or project_manager.role != 'Project Manager':
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project managers can assign roles")
Assign role to user
user = db.query(User).filter(User.id == user_id).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
user.role = role
db.commit()
Create an entry in the audit trail
Assuming an AuditTrail model exists
audit_entry = AuditTrail(
user_id=user_id,
action=f"Role assigned: {role}",
timestamp=datetime.utcnow()
)
db.add(audit_entry)
db.commit()
return {"message": "Role assigned successfully"}
except Exception as e:
raise HTTPException(status_code=400, detail=str(e))
New function to get available roles
def get_user_roles():
return ['Project Manager', 'Team Member', 'Viewer']