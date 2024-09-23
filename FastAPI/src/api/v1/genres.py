from http import HTTPStatus
from typing import Optional, List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from services.genre import GenreService, get_genre_service
from models.genre import Genre

router = APIRouter()


@router.get("/genres",
            response_model=List[Genre],
            summary="Поиск жанров",
            description="Полнотекстовый поиск по жанрам",
            response_description="Название и описание жанров",
            tags=['Полнотекстовый поиск']
            )
async def get_genres(
    filter_by: Optional[str] = None,
    query: Optional[str] = None,
    page: Annotated[int, Query(description='Страница', ge=1)] = 1,
    per_page: Annotated[int, Query(description='Размер страницы', ge=1)] = 10,
    sort_by: Optional[str] = None,
    genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    genres = await genre_service.get_list(filter_by, query, page, per_page, sort_by)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genres not found')
    return genres


@router.get('/genre/{genre_id}',
            response_model=Genre,
            summary="Данные по жанру",
            description="Данные по жанру",
            response_description="Название, описание",
            tags=['Жанры']
            )
async def genre_details(genre_id: str,
                        genre_service: GenreService = Depends(
                            get_genre_service)
                        ) -> Genre:

    genre = await genre_service.get_by_id(entity_id=genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')

    return genre
