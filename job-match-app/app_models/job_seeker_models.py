from pydantic import BaseModel, EmailStr
from typing import Optional

from app_models.validation_models import ALLOWED_USERNAME


class JobSeekerInfo(BaseModel):
    summary: Optional[str]
    email: Optional[str]
    address: Optional[str]
    telephone: Optional[str]
    location : Optional[str]
    status: Optional[str]
    number_of_matches_from_diffrent_cvs: Optional[int]

class JobSeekerOptionalInfo(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    telephone: Optional[str] = None
    address: Optional[str] = None

    @classmethod
    def from_query_result(cls, username, first_name, last_name, summary, status):
        return cls(username=username,
                   first_name=first_name,
                   last_name=last_name,
                   summary=summary,
                   status=status
                   )


class JobSeeker(BaseModel):
    id: Optional[int] = None
    group: str = 'seekers'
    username: ALLOWED_USERNAME
    first_name: str
    email: EmailStr
    last_name: str
    summary: Optional[str] = None
    blocked: Optional[bool] = 0

    @classmethod
    def from_query_results(cls, id, username, email,
                           first_name, last_name, summary, blocked):
        return cls(id=id, group='seekers', username=username, email=email,
                   first_name=first_name,
                   last_name=last_name,
                   summary=summary,
                   blocked=blocked)
