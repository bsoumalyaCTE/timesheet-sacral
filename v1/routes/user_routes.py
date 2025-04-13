from fastapi import APIRouter, HTTPException, Depends, status
from configs.database import get_db
from fastapi_jwt_auth import AuthJWT
from configs.schemas.user_schema import *
from v1.cruds.user_crud import *
from v1.cruds.project_crud import *   Assuming this is where project-related CRUD functions are defined
from v1.cruds.crm_integration import *   Assuming this is where CRM integration functions are defined
user_router = APIRouter(prefix="/user", tags=["Users"])
@AuthJWT.load_config
def get_config():
return tokenSettings()
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
return {"status": status.HTTP_200_OK, "message": "User logged in successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
@user_router.post("/refresh", tags=["Users"], summary="Refresh Token", description="Generate a new access token using the refresh token.")
async def refresh_token(Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_refresh_token_required()
current_user = Authorize.get_jwt_subject()
new_access_token = Authorize.create_access_token(subject=current_user, fresh=False)
return {"status": status.HTTP_200_OK, "message": "Access token refreshed successfully.", "access_token": new_access_token}
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")
@user_router.post("/logout", tags=["Users"], summary="Logout User", description="Logout the user by invalidating tokens.")
async def logout_user(Authorize: AuthJWT = Depends()):
try:
Authorize.jwt_required()
Authorize.unset_jwt_cookies()
return {"status": status.HTTP_200_OK, "message": "User logged out successfully."}
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
@user_router.get("/get_all", response_model=userAllResponse, status_code=status.HTTP_200_OK,
tags=["Users"], summary="List of All Users", description="Retrieve all users.",
response_description="List of all users.")
async def get_all_users(db=Depends(get_db), Authorize: AuthJWT = Depends(), eligible_for_project: bool = False):
try:
Authorize.jwt_required()
except Exception as e:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired.")
Modify the query to filter users based on eligibility for project assignment
crud_response = get_all_users_crud(db, eligible_for_project=eligible_for_project)
if crud_response:
return {"status": status.HTTP_200_OK, "message": "Users retrieved successfully.", "data": crud_response}
else:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
New code for project module
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
New endpoints for CRM integration
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