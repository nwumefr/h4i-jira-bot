from pydantic import BaseModel
from uuid import uuid4, UUID
from typing import Optional

class Ticket(BaseModel):
    id:UUID
    issuer:str
    content:str
    # assigned_to:Optional[str]
