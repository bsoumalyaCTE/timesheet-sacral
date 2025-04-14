from fastapi import HTTPException, status
from configs.models import Project, ProjectTeam, User, Customer, Role   Assuming Role model is defined
from datetime import datetime
import requests
import logging
Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
logger.error(f"Error assigning project team: {str(e)}")
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
logger.error(f"Error updating project team: {str(e)}")
raise HTTPException(status_code=400, detail=str(e))
def get_user_financial_data(db, user_id):
try:
user = db.query(User).filter(User.id == user_id).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
Fetch financial data related to the user's projects
financial_data = fetch_financial_data_from_system(user_id)
if not financial_data:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial data not found")
return financial_data
except Exception as e:
logger.error(f"Error fetching user financial data: {str(e)}")
raise HTTPException(status_code=400, detail=str(e))
def fetch_financial_data_from_system(user_id):
Placeholder function to simulate fetching data from a financial system
In a real implementation, this would involve API calls to the financial system
return {
"user_id": user_id,
"billing_data": [],
"invoicing_data": []
}
def connect_to_hrm_system():
Simulate connection to HRM system
try:
This is a placeholder for the actual API call to the HRM system
response = requests.get("https://hrm-system.example.com/api/employees")
response.raise_for_status()
return response.json()
except requests.RequestException as e:
logger.error(f"Error connecting to HRM system: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to connect to HRM system")
def update_employee_data_in_project_system(db):
try:
employees = connect_to_hrm_system()
for employee in employees:
user = db.query(User).filter(User.id == employee['id']).first()
if user:
user.name = employee['name']
user.role = employee['role']
user.availability = employee['availability']
else:
If user does not exist, create a new user
new_user = User(
id=employee['id'],
name=employee['name'],
role=employee['role'],
availability=employee['availability']
)
db.add(new_user)
db.commit()
except Exception as e:
logger.error(f"Error updating employee data: {str(e)}")
raise HTTPException(status_code=400, detail=str(e))
def get_all_customers_crud(db):
try:
customers = db.query(Customer).all()
return customers
except Exception as e:
logger.error(f"Error fetching customers: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to fetch customers")
New function to get employee data from HRM
def get_employee_data_from_hrm():
try:
response = requests.get("https://hrm-system.example.com/api/employees", headers={"Authorization": "Bearer YOUR_TOKEN"})
response.raise_for_status()
return response.json()
except requests.RequestException as e:
logger.error(f"Error fetching employee data from HRM: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to fetch employee data from HRM")
Function to update user information based on HRM data
def update_user_information(db):
try:
employees = get_employee_data_from_hrm()
for employee in employees:
user = db.query(User).filter(User.id == employee['id']).first()
if user:
user.name = employee['name']
user.role = employee['role']
user.availability = employee['availability']
else:
new_user = User(
id=employee['id'],
name=employee['name'],
role=employee['role'],
availability=employee['availability']
)
db.add(new_user)
db.commit()
except Exception as e:
logger.error(f"Error updating user information: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to update user information")
Extend the User model to include preferences for time tracking tool integration
def signup_user_crud(db, user_data):
try:
Assuming user_data is a dictionary containing user details
new_user = User(
id=user_data['id'],
name=user_data['name'],
role=user_data['role'],
availability=user_data['availability'],
time_tracking_tool=user_data.get('time_tracking_tool')   New field for time tracking tool
)
db.add(new_user)
Assign default role to new user
default_role = db.query(Role).filter(Role.name == "default").first()
if default_role:
new_user.roles.append(default_role)
db.commit()
return {"message": "User signed up successfully"}
except Exception as e:
logger.error(f"Error signing up user: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to sign up user")
New function to handle login and support additional load from the new project module
def login_user_crud(db, user_credentials):
try:
user = db.query(User).filter(User.name == user_credentials['name']).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
Check password (assuming user_credentials contains a 'password' field)
if user.password != user_credentials['password']:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
Check if user is locked or disabled
if not user.is_enabled or user.is_locked:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is locked or disabled")
Check user roles and permissions
if not user.roles:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no roles assigned")
Log the access attempt
logger.info(f"User {user.name} logged in successfully with roles: {[role.name for role in user.roles]}")
Handle time tracking tool preferences
if user.time_tracking_tool:
Logic to integrate with the selected time tracking tool
pass
return {"message": "User logged in successfully"}
except Exception as e:
logger.error(f"Error logging in user: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to log in user")
New CRUD operations for time tracking integration
def set_time_tracking_integration(db, user_id, tool_name):
try:
user = db.query(User).filter(User.id == user_id).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
user.time_tracking_tool = tool_name
db.commit()
return {"message": "Time tracking tool set successfully"}
except Exception as e:
logger.error(f"Error setting time tracking integration: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to set time tracking integration")
def get_time_tracking_data_crud(db, user_id):
try:
user = db.query(User).filter(User.id == user_id).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
if not user.time_tracking_tool:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Time tracking tool not set")
Simulate fetching time tracking data
time_tracking_data = fetch_time_tracking_data(user.time_tracking_tool, user_id)
return time_tracking_data
except Exception as e:
logger.error(f"Error fetching time tracking data: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to fetch time tracking data")
def fetch_time_tracking_data(tool_name, user_id):
Placeholder function to simulate fetching data from a time tracking tool
In a real implementation, this would involve API calls to the time tracking tool
return {
"user_id": user_id,
"tool_name": tool_name,
"time_entries": []
}
New function to get user by ID with role and permission checks
def get_user_by_id_crud(db, user_id, requesting_user_id):
try:
requesting_user = db.query(User).filter(User.id == requesting_user_id).first()
if not requesting_user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requesting user not found")
Check if the requesting user has the necessary permissions
if not has_permission(requesting_user, 'view_user_data'):
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
user = db.query(User).filter(User.id == user_id).first()
if not user:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
Log the access attempt
logger.info(f"User {requesting_user.name} accessed data for user {user.name}")
return user
except Exception as e:
logger.error(f"Error fetching user by ID: {str(e)}")
raise HTTPException(status_code=400, detail="Failed to fetch user by ID")
def has_permission(user, permission):
Placeholder function to check if a user has a specific permission
In a real implementation, this would check the user's roles and permissions
return any(role.name == permission for role in user.roles)