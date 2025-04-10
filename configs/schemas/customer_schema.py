from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime, date

# Define Pydantic schemas for request and response
class CustomerCreate(BaseModel):
    id: Optional[int] = None
    name: str
    description: str = None 
    logo: Optional[str] = None
    create_timestamp: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True

class customerModel(BaseModel):
    id: int
    name: str
    description: Optional[str]
    logo: Optional[str]
    create_timestamp: datetime  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archiving_timestamp: datetime | None = None

class customerNameModel(BaseModel):
    id: int
    name: str

class CustomerResponse(BaseModel):
    status: int
    message: str
    data: customerModel

class AllCustomerResponse(BaseModel):
    status: int
    message: str
    data: list[customerModel]
    customer_names: List[customerNameModel]
