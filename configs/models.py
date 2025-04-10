from configs.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date, Float, BigInteger, SmallInteger
from sqlalchemy.orm import relationship, configure_mappers
from lib.helper import verify_password_hash


configure_mappers()

#/**
# * The User class is a model that represents the users table in the database.
# */
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
    hire_date = Column(Date, nullable=False)  # date represented as Date
    release_date = Column(Date, nullable=True)  # date represented as Date
    created = Column(DateTime, nullable=False)  # datetime represented as DateTime
    is_enabled = Column(Boolean, nullable=False, default=True)  # bit(1) represented as Boolean
    is_locked = Column(Boolean, nullable=False, default=False)  # bit(1) represented as Boolean

    # Relationships
    teams = relationship("TeamMember", back_populates="users")
    team_members = relationship("TeamMember", back_populates="users")
    user_projects = relationship("UserProject", back_populates="users")
    user_tasks = relationship("UserTask", back_populates="users")
    user_task_comments = relationship("UserTaskComment", back_populates="users")
    user_date_leaves = relationship("UserDateLeave", back_populates="users")
    time_tracking_records = relationship("TimeTrackingRecord", back_populates="users")
    time_tracking_locks = relationship("TimeTrackingLock", back_populates="users")
    user_role_mappings = relationship("UserRoleMapping", back_populates="users")

    def verify_password(self, plain_password: str) -> bool:
        return verify_password_hash(plain_password, self.password)




#/**
# * The Customer class is a model that represents the customers table in the database.
# */
class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    create_timestamp = Column(DateTime, nullable=False)  # datetime represented as DateTime
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # mediumtext represented as Text
    logo = Column(String(255), nullable=True)
    archiving_timestamp = Column(DateTime, nullable=True)  # datetime represented as DateTime

    projects = relationship("Project", back_populates="customers")
    #tasks = relationship("Task", back_populates="customers")


#/**
# * The Project class is a model that represents the projects table in the database.
# */
class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # mediumtext represented as Text
    create_timestamp = Column(DateTime, nullable=False)  # datetime represented as DateTime
    archiving_timestamp = Column(DateTime, nullable=True)  # datetime represented as DateTime

    customers = relationship("Customer", back_populates="projects")
    user_projects = relationship("UserProject", back_populates="projects")
    tasks = relationship("Task", back_populates="projects")


#/**
# * The UserProject class is a model that represents the user_projects table in the database.
# */
class UserProject(Base):
    __tablename__ = 'user_projects'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True, nullable=False)

    users = relationship("User", back_populates="user_projects")
    projects = relationship("Project", back_populates="user_projects")


#/**
# * The Task class is a model that represents the tasks table in the database.
# */
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    last_tt_date = Column(Date, nullable=True)  # date represented as Date
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # text represented as Text
    completion_date = Column(Date, nullable=True)  # date represented as Date
    create_timestamp = Column(DateTime, nullable=False)  # datetime represented as DateTime

    #customers = relationship("Customer", back_populates="tasks")
    projects = relationship("Project", back_populates="tasks")
    user_tasks = relationship("UserTask", back_populates="tasks")
    user_task_comments = relationship("UserTaskComment", back_populates="tasks")
    time_tracking_records = relationship("TimeTrackingRecord", back_populates="tasks")



#/**
# * The UserTask class is a model that represents the user_tasks table in the database.
# */
class UserTask(Base):
    __tablename__ = 'user_tasks'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)

    users = relationship("User", back_populates="user_tasks")
    tasks = relationship("Task", back_populates="user_tasks")


#/**
# * The UserTaskComment class is a model that represents the user_task_comments table in the database.
# */
class UserTaskComment(Base):
    __tablename__ = 'user_task_comments'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)
    comment_date = Column(Date, nullable=False)  # date represented as Date
    comments = Column(Text, nullable=True)  # mediumtext represented as Text

    users = relationship("User", back_populates="user_task_comments")
    tasks = relationship("Task", back_populates="user_task_comments")


#/**
# * The UserDateLeave class is a model that represents the user_date_leaves table in the database.
# */
class UserDateLeave(Base):
    __tablename__ = 'user_date_leaves'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    leave_date = Column(Date, primary_key=True, nullable=False)  # date represented as Date
    leave_type_id = Column(Integer, ForeignKey('leave_types.id'), nullable=False)
    leave_duration = Column(Float, nullable=False)  # duration represented as Float

    users = relationship("User", back_populates="user_date_leaves")
    leave_types = relationship("LeaveType", back_populates="user_date_leaves")


#/**
# * The TimeTrackingRecord class is a model that represents the tt_records table in the database.
# */
class TimeTrackingRecord(Base):
    __tablename__ = 'tt_records'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True, nullable=False)
    record_date = Column(Date, nullable=False)  # date represented as Date
    actuals = Column(Float, nullable=False)  # actuals represented as Float

    users = relationship("User", back_populates="time_tracking_records")
    tasks = relationship("Task", back_populates="time_tracking_records")


#/**
# * The TimeTrackingLock class is a model that represents the tt_locks table in the database.
# */
class TimeTrackingLock(Base):
    __tablename__ = 'tt_locks'

    locked_user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    date_from = Column(Date, nullable=False)  # date represented as Date
    date_to = Column(Date, nullable=False)  # date represented as Date
    when_locked = Column(DateTime, nullable=False)  # datetime represented as DateTime

    users = relationship("User", back_populates="time_tracking_locks")


#/**
# * The LeaveType class is a model that represents the leave_types table in the database.
# */
class LeaveType(Base):
    __tablename__ = 'leave_types'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(80), nullable=False)
    is_planned = Column(Boolean, nullable=False, default=False)  # bit(1) represented as Boolean
    is_active = Column(Boolean, nullable=False, default=True)  # bit(1) represented as Boolean
    whole_day_text = Column(String(9), nullable=True)
    position = Column(SmallInteger, nullable=False)  # position represented as SmallInteger

    user_date_leaves = relationship("UserDateLeave", back_populates="leave_types")


#/**
# * The SystemConfig class is a model that represents the system_config table in the database.
# */
class SystemConfig(Base):
    __tablename__ = 'system_config'

    property_name = Column(String(255), primary_key=True, nullable=False)
    property_value = Column(Text, nullable=False)  # value represented as Text


#/**
# * The Role class is a model that represents the roles table in the database.
# */
class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    role = Column(String(255), nullable=False)

    permission_role_mappings = relationship("PermissionRoleMapping", back_populates="roles")
    user_role_mappings = relationship("UserRoleMapping", back_populates="roles")


#/**
# * The PermissionType class is a model that represents the permission_types table in the database.
# */
class PermissionType(Base):
    __tablename__ = 'permission_types'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('permission_types.id'), nullable=True)
    type = Column(String(255), nullable=False)

    parent = relationship("PermissionType", remote_side=[id], back_populates="children")
    children = relationship("PermissionType", back_populates="parent")
    permission_role_mappings = relationship("PermissionRoleMapping", back_populates="permission_types")


#/**
# * The UserRoleMapping class is a model that represents the user_role_mappings table in the database.
# */
class UserRoleMapping(Base):
    __tablename__ = 'user_role_mappings'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)

    users = relationship("User", back_populates="user_role_mappings")
    roles = relationship("Role", back_populates="user_role_mappings")


#/**
# * The PermissionRoleMapping class is a model that represents the permission_role_mappings table in the database.
# */
class PermissionRoleMapping(Base):
    __tablename__ = 'permission_role_mappings'

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False)
    permission_type_id = Column(Integer, ForeignKey('permission_types.id'), primary_key=True, nullable=False)

    roles = relationship("Role", back_populates="permission_role_mappings")
    permission_types = relationship("PermissionType", back_populates="permission_role_mappings")


#/**
# * The Team class is a model that represents the teams table in the database.
# */
class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)
    create_timestamp = Column(DateTime, nullable=False)  # datetime represented as DateTime

    team_members = relationship("TeamMember", back_populates="teams")


#/**
# * The TeamMember class is a model that represents the team_members table in the database.
# */
class TeamMember(Base):
    __tablename__ = 'team_members'

    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    lead = Column(Boolean, nullable=False, default=False)  # bit(1) represented as Boolean

    teams = relationship("Team", back_populates="team_members")
    users = relationship("User", back_populates="team_members")

