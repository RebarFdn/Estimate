from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from typing import List

from pydantic import BaseModel, EmailStr
from httpx import get


class Section(BaseModel):
    _id: UUID = uuid4()
    title:str | None = None
    items:list

class EstimateModel(BaseModel):
    _id: UUID = uuid4()
    title:str | None = None
    subtitle:str | None = None
    project:str | None = None
    sections:list = []
    created_by:str | None = None
