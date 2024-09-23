from http import HTTPStatus
from typing import Optional, List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from services.person import PersonService, get_person_service
from models.person import Person

router = APIRouter()


@router.get("/persons",
            response_model=List[Person],
            summary="Поиск персонажей",
            description="Полнотекстовый поиск по персонажам",
            response_description="Список персонажей",
            tags=['Полнотекстовый поиск']
            )
async def get_persons(
    filter_by: Optional[str] = None,
    query: Optional[str] = None,
    page: Annotated[int, Query(description='Страница', ge=1)] = 1,
    per_page: Annotated[int, Query(description='Размер страницы', ge=1)] = 10,
    sort_by: Optional[str] = None,
    person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    persons = await person_service.get_list(filter_by, query, page, per_page, sort_by)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')
    return persons


@router.get('/person/{person_id}',
            response_model=Person,
            summary="Данные по персоне",
            description="Данные по персоне",
            response_description="Ид, ФИО, пол",
            tags=['Персонажи']
            )
async def person_details(person_id: str,
                         person_service: PersonService = Depends(
                             get_person_service)
                         ) -> Person:

    entity = await person_service.get_by_id(entity_id=person_id)
    if not entity:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')

    return entity
