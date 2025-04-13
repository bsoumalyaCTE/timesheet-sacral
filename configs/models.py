from configs.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date, Float, BigInteger, SmallInteger
from sqlalchemy.orm import relationship, configure_mappers
from lib.helper import verify_password_hash
from lib.mfa import send_mfa_code, verify_mfa_code   Assuming these functions are available in the mfa module
configure_mappers()
class User(Base):
__tablename__ = 'users'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
username = Column(String(255), nullable=False, unique=True)
password = Column(String(255), nullable=False)
first_name = Column(String(255), nullable=False)
middle_name = Column(String(255), nullable=True)
last_name = Column(String(255), nullable=False)
email = Column(String(255), nullable=False, unique=True)
phone = Column(String(255), nullable=True)
fax = Column(String(255), nullable=True)
mobile = Column(String(255), nullable=True)
other_contact = Column(String(255), nullable=True)
workday_duration = Column(Integer, nullable=False)
hire_date = Column(Date, nullable=False)
release_date = Column(Date, nullable=True)
created = Column(DateTime, nullable=False)
is_enabled = Column(Boolean, nullable=False, default=True)
is_locked = Column(Boolean, nullable=False, default=False)
mfa_enabled = Column(Boolean, nullable=False, default=False)   New field to indicate if MFA is enabled
mfa_secret = Column(String(255), nullable=True)   New field to store MFA secret
teams = relationship("TeamMember", back_populates="users")
team_members = relationship("TeamMember", back_populates="users")
user_projects = relationship("UserProject", back_populates="users")
user_tasks = relationship("UserTask", back_populates="users")
user_task_comments = relationship("UserTaskComment", back_populates="users")
user_date_leaves = relationship("UserDateLeave", back_populates="users")
time_tracking_records = relationship("TimeTrackingRecord", back_populates="users")
time_tracking_locks = relationship("TimeTrackingLock", back_populates="users")
user_role_mappings = relationship("UserRoleMapping", back_populates="users")
def verify_password(self, plain_password: str, mfa_code: str = None) -> bool:
if not verify_password_hash(plain_password, self.password):
return False
if self.mfa_enabled:
if not mfa_code:
send_mfa_code(self.mfa_secret)   Send MFA code to user
return False
return verify_mfa_code(self.mfa_secret, mfa_code)
return True
class Customer(Base):
__tablename__ = 'customers'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
create_timestamp = Column(DateTime, nullable=False)
name = Column(String(255), nullable=False)
description = Column(Text, nullable=True)
logo = Column(String(255), nullable=True)
archiving_timestamp = Column(DateTime, nullable=True)
projects = relationship("Project", back_populates="customers")
class Project(Base):
__tablename__ = 'projects'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
name = Column(String(255), nullable=False)
code = Column(String(255), nullable=False)
description = Column(Text, nullable=True)
create_timestamp = Column(DateTime, nullable=False)
archiving_timestamp = Column(DateTime, nullable=True)
customers = relationship("Customer", back_populates="projects")
user_projects = relationship("UserProject", back_populates="projects")
tasks = relationship("Task", back_populates="projects")
class UserProject(Base):
__tablename__ = 'user_projects'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True, nullable=False)
users = relationship("User", back_populates="user_projects")
projects = relationship("Project", back_populates="user_projects")
class Task(Base):
__tablename__ = 'tasks'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
last_tt_date = Column(Date, nullable=True)
name = Column(String(255), nullable=False)
description = Column(Text, nullable=True)
completion_date = Column(Date, nullable=True)
create_timestamp = Column(DateTime, nullable=False)
projects = relationship("Project", back_populates="tasks")
user_tasks = relationship("UserTask", back_populates="tasks")
user_task_comments = relationship("UserTaskComment", back_populates="tasks")
time_tracking_records = relationship("TimeTrackingRecord", back_populates="tasks")
class UserTask(Base):
__tablename__ = 'user_tasks'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)
users = relationship("User", back_populates="user_tasks")
tasks = relationship("Task", back_populates="user_tasks")
class UserTaskComment(Base):
__tablename__ = 'user_task_comments'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)
comment_date = Column(Date, nullable=False)
comments = Column(Text, nullable=True)
users = relationship("User", back_populates="user_task_comments")
tasks = relationship("Task", back_populates="user_task_comments")
class UserDateLeave(Base):
__tablename__ = 'user_date_leaves'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
leave_date = Column(Date, primary_key=True, nullable=False)
leave_type_id = Column(Integer, ForeignKey('leave_types.id'), nullable=False)
leave_duration = Column(Float, nullable=False)
users = relationship("User", back_populates="user_date_leaves")
leave_types = relationship("LeaveType", back_populates="user_date_leaves")
class TimeTrackingRecord(Base):
__tablename__ = 'tt_records'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)
record_date = Column(Date, nullable=False)
actuals = Column(Float, nullable=False)
users = relationship("User", back_populates="time_tracking_records")
tasks = relationship("Task", back_populates="time_tracking_records")
class TimeTrackingLock(Base):
__tablename__ = 'tt_locks'
locked_user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
date_from = Column(Date, nullable=False)
date_to = Column(Date, nullable=False)
when_locked = Column(DateTime, nullable=False)
users = relationship("User", back_populates="time_tracking_locks")
class LeaveType(Base):
__tablename__ = 'leave_types'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
name = Column(String(80), nullable=False)
is_planned = Column(Boolean, nullable=False, default=False)
is_active = Column(Boolean, nullable=False, default=True)
whole_day_text = Column(String(9), nullable=True)
position = Column(SmallInteger, nullable=False)
user_date_leaves = relationship("UserDateLeave", back_populates="leave_types")
class SystemConfig(Base):
__tablename__ = 'system_config'
property_name = Column(String(255), primary_key=True, nullable=False)
property_value = Column(Text, nullable=False)
class Role(Base):
__tablename__ = 'roles'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
role = Column(String(255), nullable=False)
permission_role_mappings = relationship("PermissionRoleMapping", back_populates="roles")
user_role_mappings = relationship("UserRoleMapping", back_populates="roles")
class PermissionType(Base):
__tablename__ = 'permission_types'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
parent_id = Column(Integer, ForeignKey('permission_types.id'), nullable=True)
type = Column(String(255), nullable=False)
parent = relationship("PermissionType", remote_side=[id], back_populates="children")
children = relationship("PermissionType", back_populates="parent")
permission_role_mappings = relationship("PermissionRoleMapping", back_populates="permission_types")
class UserRoleMapping(Base):
__tablename__ = 'user_role_mappings'
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)
users = relationship("User", back_populates="user_role_mappings")
roles = relationship("Role", back_populates="user_role_mappings")
class PermissionRoleMapping(Base):
__tablename__ = 'permission_role_mappings'
role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)
permission_type_id = Column(Integer, ForeignKey('permission_types.id'), primary_key=True, nullable=False)
roles = relationship("Role", back_populates="permission_role_mappings")
permission_types = relationship("PermissionType", back_populates="permission_role_mappings")
class Team(Base):
__tablename__ = 'teams'
id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
name = Column(String(255), nullable=False)
create_timestamp = Column(DateTime, nullable=False)
team_members = relationship("TeamMember", back_populates="teams")
class TeamMember(Base):
__tablename__ = 'team_members'
team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, nullable=False)
user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
lead = Column(Boolean, nullable=False, default=False)
teams = relationship("Team", back_populates="team_members")
users = relationship("User", back_populates="team_members")