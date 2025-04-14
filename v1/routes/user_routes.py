from fastapi import APIRouter, HTTPException, Depends, status
from configs.database import get_db
from fastapi_jwt_auth import AuthJWT
from configs.schemas.user_schema import *
from v1.cruds.user_crud import *
from v1.cruds.project_crud import *
from v1.cruds.crm_integration import *
from v1.services.role_service import RoleService
from v1.models.audit_log import AuditLog
from v1.services.mfa_service import MFAService   Assuming there's an MFA service
import os
user_router = APIRouter(prefix="/user", tags=["Users"])
@AuthJWT.load_config
def get_config():
class Settings:
authjwt_secret_key: str = "your_secret_key"
authjwt_denylist_enabled: bool = True
authjwt_token_location: set = {"headers", "cookies"}
authjwt_cookie_csrf_protect: bool = True
Add role-based access control configurations
authjwt_roles: dict = {
"admin": ["create", "read", "update", "delete"],
"user": ["read"]
}
Add multi-factor authentication options if needed
authjwt_mfa_enabled: bool = True
Financial system API connection settings
financial_api_url: str = os.getenv("FINANCIAL_API_URL", "https://api.financialsystem.com")
financial_api_key: str = os.getenv("FINANCIAL_API_KEY", "your_financial_api_key")
financial_api_timeout: int = int(os.getenv("FINANCIAL_API_TIMEOUT", 30))
return Settings()
Error handling middleware for financial system integration
async def financial_system_error_handler(request, call_next):
try:
response = await call_next(request)
return response
except Exception as e:
Log the error and return a generic error message
Ensure compliance with data protection and privacy regulations
return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Financial system integration error.")
@user_router.post("/signup", response_model=userSignUpResponse, status_code=status.HTTP_201_CREATED,
tags=["Users"], summary="User Signup", description="Create a new user.",
response_description="User created successfully.")
async def signup_user(user: signUpModel, db=Depends(get_db)):
crud_response = signup_user_crud(db, user)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "User created successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed.")
@user_router.post("/signin", response_model=userLoginResponse, status_code=status.HTTP_200_OK,
tags=["Users"], summary="User Signin", description="Authenticate a user.",
response_description="User logged in successfully.")
async def login_user(user: loginModel, Authorize: AuthJWT = Depends(), db=Depends(get_db)):
crud_response = login_user_crud(db, user, Authorize)
if crud_response:
Initiate MFA process
mfa_service = MFAService()
mfa_response = mfa_service.initiate_mfa(user.email)
if mfa_response:
return {"status": status.HTTP_200_OK, "message": "MFA initiated. Please verify.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA initiation failed.")
else:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
@user_router.post("/refresh", tags=["Users"], summary="Refresh Token", description="Generate a new access token using the refresh token.")
async def refresh_token(Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_refresh_token_required()
current_user = Authorize.get_jwt_subject()
Check if MFA is completed before issuing a new access token
if not MFAService().is_mfa_completed(current_user):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA not completed.")
new_access_token = Authorize.create_access_token(subject=current_user, fresh=False)
return {"status": status.HTTP_200_OK, "message": "Access token refreshed successfully.", "access_token": new_access_token}
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")
@user_router.post("/logout", tags=["Users"], summary="Logout User", description="Logout the user by invalidating tokens.")
async def logout_user(Authorize: AuthJWT = Depends(), db=Depends(get_db)):
try:
Authorize.jwt_required()
current_user = Authorize.get_jwt_subject()
Ensure MFA is completed before logout
if not MFAService().is_mfa_completed(current_user):
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA not completed.")
Invalidate tokens securely
Authorize.unset_jwt_cookies()
Log the logout event for audit purposes
audit_log = AuditLog(db)
audit_log.record_logout(current_user)
return {"status": status.HTTP_200_OK, "message": "User logged out successfully."}
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
@user_router.get("/get_all", response_model=userAllResponse, status_code=status.HTTP_200_OK,
tags=["Users"], summary="List of All Users", description="Retrieve all users.",
response_description="List of all users.")
async def get_all_users(db=Depends(get_db), Authorize: AuthJWT = Depends(), eligible_for_project: bool = False):
try:
Authorize.jwt_required()
Check user role and permissions
current_user = Authorize.get_jwt_subject()
user_roles = Authorize.get_raw_jwt().get("roles", [])
if "admin" not in user_roles:
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view user information.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
Modify the query to filter users based on eligibility for project assignment
crud_response = get_all_users_crud(db, eligible_for_project=eligible_for_project)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "Users retrieved successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
@user_router.post("/projects/add", tags=["Projects"], summary="Add Project", description="Add a new project with currency selection.")
async def add_project(project: ProjectModel, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
if not project.currency:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project currency must be selected.")
Logic to add project with currency
crud_response = add_project_crud(db, project)
if crud_response:
return {"status": status.HTTP_201_CREATED, "message": "Project added successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project creation failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.put("/projects/edit/{project_id}", tags=["Projects"], summary="Edit Project", description="Edit an existing project with currency selection.")
async def edit_project(project_id: int, project: ProjectModel, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
if not project.currency:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project currency must be selected.")
Logic to edit project with currency
crud_response = edit_project_crud(db, project_id, project)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "Project updated successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project update failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.post("/projects/{project_id}/assign_role", tags=["Projects"], summary="Assign Role", description="Assign a role to a user in a project.")
async def assign_role(project_id: int, role_assignment: RoleAssignmentModel, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to assign role to user
role_service = RoleService(db)
crud_response = role_service.assign_role(project_id, role_assignment)
if crud_response:
Log the role assignment in the audit trail
audit_log = AuditLog(db)
audit_log.record_role_assignment(project_id, role_assignment)
return {"status": status.HTTP_200_OK, "message": "Role assigned successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role assignment failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.get("/projects/{project_id}/roles", tags=["Projects"], summary="View Roles", description="View roles assigned to users in a project.")
async def view_roles(project_id: int, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to view roles
role_service = RoleService(db)
roles_data = role_service.view_roles(project_id)
if roles_data:
return {"status": status.HTTP_200_OK, "message": "Roles retrieved successfully.", "data": roles_data}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No roles found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.get("/projects/{project_id}/audit_trail", tags=["Projects"], summary="Audit Trail", description="View audit trail of role assignments.")
async def view_audit_trail(project_id: int, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to view audit trail
audit_log = AuditLog(db)
audit_trail_data = audit_log.get_audit_trail(project_id)
if audit_trail_data:
return {"status": status.HTTP_200_OK, "message": "Audit trail retrieved successfully.", "data": audit_trail_data}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No audit trail found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.post("/crm/sync", tags=["CRM"], summary="Initiate CRM Synchronization", description="Initiate synchronization with the CRM system.")
async def initiate_crm_sync(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to initiate CRM synchronization
sync_response = initiate_crm_sync_crud(db)
if sync_response:
return {"status": status.HTTP_200_OK, "message": "CRM synchronization initiated successfully.", "data": sync_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CRM synchronization failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.get("/crm/customers", tags=["CRM"], summary="View Synchronized Customer Data", description="View customer data synchronized from the CRM system.")
async def view_synchronized_customers(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to retrieve synchronized customer data
customer_data = get_synchronized_customers_crud(db)
if customer_data:
return {"status": status.HTTP_200_OK, "message": "Customer data retrieved successfully.", "data": customer_data}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customer data found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.get("/crm/sync/logs", tags=["CRM"], summary="CRM Synchronization Logs", description="Retrieve logs of CRM synchronization activities.")
async def get_crm_sync_logs(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to retrieve CRM synchronization logs
sync_logs = get_crm_sync_logs_crud(db)
if sync_logs:
return {"status": status.HTTP_200_OK, "message": "CRM synchronization logs retrieved successfully.", "data": sync_logs}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No synchronization logs found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.get("/crm/customers/dropdown", tags=["CRM"], summary="Customer Dropdown", description="Get customer data for dropdown.")
async def get_customer_dropdown(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to retrieve customer data for dropdown
customer_data = get_synchronized_customers_crud(db)
if customer_data:
dropdown_data = [{"id": customer["id"], "name": customer["name"]} for customer in customer_data]
return {"status": status.HTTP_200_OK, "message": "Customer dropdown data retrieved successfully.", "data": dropdown_data}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customer data found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
New endpoint for assigning project teams
@user_router.post("/projects/{project_id}/assign_team", tags=["Projects"], summary="Assign Project Team", description="Assign a team to a project with work allocation.")
async def assign_project_team(project_id: int, team_assignment: TeamAssignmentModel, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Validate total work allocation
total_allocation = sum(member.allocation for member in team_assignment.members)
if total_allocation > 100:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total work allocation exceeds 100%.")
Logic to assign team to project
crud_response = assign_team_to_project_crud(db, project_id, team_assignment)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "Project team assigned successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project team assignment failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
New endpoints for HRM system integration
@user_router.get("/hrm/employees", tags=["HRM"], summary="Retrieve Employee Data", description="Retrieve employee data from the HRM system.")
async def get_employee_data(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to retrieve employee data from HRM system
employee_data = get_employee_data_crud(db)
if employee_data:
return {"status": status.HTTP_200_OK, "message": "Employee data retrieved successfully.", "data": employee_data}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employee data found.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.post("/hrm/update", tags=["HRM"], summary="Update Project Assignments", description="Update project assignments based on HRM data.")
async def update_project_assignments(hrm_update: HRMUpdateModel, db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to update project assignments based on HRM data
update_response = update_project_assignments_crud(db, hrm_update)
if update_response:
return {"status": status.HTTP_200_OK, "message": "Project assignments updated successfully.", "data": update_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project assignments update failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
@user_router.post("/hrm/auto_update", tags=["HRM"], summary="Automatic HRM Updates", description="Handle automatic updates from the HRM system.")
async def handle_automatic_hrm_updates(db=Depends(get_db), Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Logic to handle automatic updates from the HRM system
auto_update_response = handle_automatic_hrm_updates_crud(db)
if auto_update_response:
return {"status": status.HTTP_200_OK, "message": "Automatic HRM updates handled successfully.", "data": auto_update_response}
else:
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Automatic HRM updates handling failed.")
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")