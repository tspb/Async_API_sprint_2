from typing import Optional, List

# pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genres: List[str]
    actors_names: List[str]
    directors_names: List[str]
    writers_names: List[str]
