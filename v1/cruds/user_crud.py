from fastapi import HTTPException, status
from configs.models import Project, ProjectTeam, User
from datetime import datetime
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