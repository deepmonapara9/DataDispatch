from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SubscribeRequest(BaseModel):
    email: EmailStr


class UnsubscribeRequest(BaseModel):
    email: EmailStr


class SubscriberResponse(BaseModel):
    id: int
    email: str
    status: str
    created_at: datetime
    updated_at: datetime


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class NewsletterContent(BaseModel):
    subject: str
    html: str


class EmailBatch(BaseModel):
    recipients: list[str]
    subject: str
    html_content: str
