from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    full_name: str
    gender: Optional[str]
