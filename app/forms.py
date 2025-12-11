from pydantic import BaseModel
from typing import Optional


class UserForm(BaseModel):
    email: str
    password: str


class UserCreateForm(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None


class SnippetCreateForm(BaseModel):
    title: str
    code: str
    description: Optional[str] = None


class SnippetUpdateForm(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
