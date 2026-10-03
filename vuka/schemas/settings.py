from enum import Enum
from pydantic import BaseModel, Field

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class SupportCategory(str, Enum):
    ACCOUNT = "Account"
    ASSESSMENTS = "Assessments"
    OPPORTUNITIES = "Opportunities"
    OTHER = "Other"


class SupportTicketCreate(BaseModel):
    category: SupportCategory
    message: str = Field(min_length=1, max_length=5000)


class SupportTicketResponse(BaseModel):
    ticket_id: int
    status: str
    category: SupportCategory
    message: str
    created_at: str
