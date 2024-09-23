from typing import Optional

from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str]
