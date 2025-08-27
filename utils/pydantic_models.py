from pydantic import BaseModel
from uuid import uuid4, UUID
import datetime
from typing import Optional, Union

class Ticket(BaseModel):
    id:str = str(uuid4())
    issuer:str
    content:str
    assigned_to:Optional[Union[str|None]] = None
    status:Optional[str] = 'not assigned'
    date_started:str = str(datetime.datetime.now())
    date_completed:Optional[Union[str|None]] = None

class TicketRequest(BaseModel):
    issuer:str
    content:str

class AssignRequest(BaseModel):
    id:str
    assigned_to:str

class CompleteRequest(AssignRequest):
    content:Union[str|None] = None

class TicketCompletion(Ticket):
    completion_content:Union[str|None] = None