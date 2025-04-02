import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schemas.schemas import ContactCreate, ContactUpdate, ContactOut
from app.services.phonebook_db import ContactsDBService
from app.dependencies.redis import get_redis_client
from app.core.config import settings
from app.core.metrics import (
    cache_requests_total,
    cache_hits_total,
    contacts_total
)

logger = logging.getLogger("phonebook_controller")
logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)

class PhonebookController:

    @staticmethod
    def _get_cache(key: str):
        cache = get_redis_client()
        return cache.get(key)

    @staticmethod
    def _set_cache(key: str, value: str, expire: int = settings.CACHE_TTL):
        cache = get_redis_client()
        cache.setex(key, expire, value)

    @staticmethod
    def _clear_cache():
        cache = get_redis_client()
        keys = cache.keys("contacts:list:*")
        keys += cache.keys("search:*")
        if keys:
            cache.delete(*keys)
        logger.info("Cache cleared for list and search endpoints.")

    @staticmethod
    def _try_fetch_from_cache(key: str, endpoint: str):
        cache_requests_total.labels(endpoint=endpoint).inc()
        cached = PhonebookController._get_cache(key)
        if cached:
            cache_hits_total.labels(endpoint=endpoint).inc()
            logger.info(f"[Controller] Returning cached result for key={key}")
            return json.loads(cached)
        return None

    @staticmethod
    async def list_contacts(db: AsyncSession, skip: int = 0, limit: int = settings.PAGINATION_DEFAULT_PAGE) -> list[ContactOut]:
        logger.debug(f"[Controller] Listing contacts: skip={skip}, limit={limit}")
        try:
            key = f"contacts:list:{skip}:{limit}"

            cached_result = PhonebookController._try_fetch_from_cache(key, "/contacts")
            if cached_result is not None:
                return cached_result

            results = await ContactsDBService.get_contacts(db, skip, limit)
            serialized = [ContactOut.model_validate(r).model_dump() for r in results]
            contacts_total.set(len(serialized))

            PhonebookController._set_cache(key, json.dumps(serialized))
            return serialized
        except Exception as e:
            logger.exception(f"[Controller] Failed to list contacts: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not fetch contacts")

    @staticmethod
    async def get_contact(db: AsyncSession, contact_id: int) -> ContactOut:
        logger.debug(f"[Controller] Getting contact id={contact_id}")
        try:
            return await ContactsDBService.get_contact(db, contact_id)
        except Exception as e:
            logger.exception(f"[Controller] Failed to get contact id={contact_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not fetch contact")

    @staticmethod
    async def create_contact(db: AsyncSession, contact: ContactCreate) -> ContactOut:
        logger.debug(f"[Controller] Creating contact: {contact}")
        try:
            result = await ContactsDBService.create_contact(db, contact)
            PhonebookController._clear_cache()
            return result
        except ValueError as e:
            logger.warning(f"[Controller] Business logic error while creating contact: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception(f"[Controller] Unexpected error while creating contact: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not create contact")

    @staticmethod
    async def update_contact(db: AsyncSession, contact_id: int, contact: ContactUpdate) -> ContactOut:
        logger.debug(f"[Controller] Updating contact id={contact_id} with data: {contact}")
        try:
            result = await ContactsDBService.update_contact(db, contact_id, contact)
            PhonebookController._clear_cache()
            return result
        except ValueError as e:
            logger.warning(f"[Controller] Business logic error during update: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception(f"[Controller] Failed to update contact id={contact_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not update contact")

    @staticmethod
    async def delete_contact(db: AsyncSession, contact_id: int) -> ContactOut:
        logger.debug(f"[Controller] Deleting contact id={contact_id}")
        try:
            result = await ContactsDBService.delete_contact(db, contact_id)
            PhonebookController._clear_cache()
            return result
        except Exception as e:
            logger.exception(f"[Controller] Failed to delete contact id={contact_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not delete contact")

    @staticmethod
    async def search_contacts(db: AsyncSession, query: str, skip: int = 0, limit: int = settings.PAGINATION_DEFAULT_PAGE) -> list[ContactOut]:
        logger.debug(f"[Controller] Searching contacts: query='{query}', skip={skip}, limit={limit}")
        try:
            key = f"search:{query}:{skip}:{limit}"

            cached_result = PhonebookController._try_fetch_from_cache(key, "/contacts/search")
            if cached_result is not None:
                return cached_result

            results = await ContactsDBService.search_contacts(db, query, skip, limit)
            serialized = [ContactOut.model_validate(r).model_dump() for r in results]
            contacts_total.set(len(serialized))

            PhonebookController._set_cache(key, json.dumps(serialized))
            return serialized
        except Exception as e:
            logger.exception(f"[Controller] Failed to search contacts: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not search contacts")

    @staticmethod
    async def delete_all_contacts(db: AsyncSession):
        logger.debug("[Controller] Deleting all contacts")
        try:
            result = await ContactsDBService.delete_all_contacts(db)
            PhonebookController._clear_cache()
            return result
        except Exception as e:
            logger.exception(f"[Controller] Failed to delete all contacts: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Could not delete all contacts")

