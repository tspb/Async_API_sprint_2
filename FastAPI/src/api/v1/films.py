from http import HTTPStatus
from typing import Optional, List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
# from fastapi_filter import FilterDepends
# from fastapi_filter.contrib.sqlalchemy import Filter

from services.film import FilmService, get_film_service
from services.genre import GenreService, get_genre_service
from models.film import Film

router = APIRouter()


@router.get("/films",
            response_model=List[Film],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильмов, жанры, актеры",
            tags=['Полнотекстовый поиск']
            )
async def get_films(
    filter_by: Optional[str] = None,
    query: Optional[str] = None,
    page: Annotated[int, Query(description='Страница', ge=1)] = 1,
    per_page: Annotated[int, Query(description='Размер страницы', ge=1)] = 10,
    sort_by: Optional[str] = None,
    film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    films = await film_service.get_list(filter_by, query, page, per_page, sort_by)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    return films


@router.get('/film/{film_id}',
            response_model=Film,
            summary="Информация о кинопроизведении",
            description="Информация о кинопроизведении",
            response_description="Ид и название фильма",
            tags=['Фильмы']
            )
async def film_details(film_id: str,
                       film_service: FilmService = Depends(get_film_service)
                       ) -> Film:

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')

    return film


@router.get('/film/{film_id}/films_in_genre/',
            response_model=List[Film],
            summary="Фильмы в том же жанре",
            description="Получение фильмов того же жанра",
            response_description="Список фильмов в том же жанре",
            tags=['Фильмы']
            )
async def films_in_genre(film_id: UUID,
                         film_service: FilmService = Depends(get_film_service)
                         ) -> List[Film]:
    films = await film_service.get_films_in_genre(film_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No films found in the same genre')
    return films


@router.get("/genre/{genre_id}/popular_films/",
            response_model=List[Film],
            summary="Популярные фильмы в жанре",
            description="Популярные фильмы в жанре",
            response_description="Название и описание жанров",
            tags=['Жанры']
            )
async def get_popular_films(
    genre_id: str,
    page: Annotated[int, Query(description='Страница', ge=1)] = 1,
    per_page: Annotated[int, Query(description='Размер страницы', ge=1)] = 10,
    sort_by: Optional[str] = '-imdb_rating',
    film_service: FilmService = Depends(get_film_service),
    genre_service: GenreService = Depends(get_genre_service)
) -> List[Film]:

    genre = await genre_service.get_by_id(entity_id=genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    films = await film_service.get_list('genres', genre.name, page, per_page, sort_by)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    return films
