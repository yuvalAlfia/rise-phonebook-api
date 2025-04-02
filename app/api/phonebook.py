from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.services.phonebook_controller import PhonebookController
from app.schemas.schemas import ContactCreate, ContactUpdate, ContactOut
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("phonebook_api", "INFO")

router = APIRouter()

@router.get("/contacts", tags=["Contact"], response_model=list[ContactOut])
async def read_contacts(
    skip: int = 0,
    limit: int = settings.PAGINATION_DEFAULT_PAGE,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[GET /contacts] skip={skip}, limit={limit}")
    try:
        return await PhonebookController.list_contacts(db, skip, limit)
    except Exception as e:
        logger.exception(f"[GET /contacts] Failed to read contacts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not fetch contacts")

@router.post("/contacts", tags=["Contact"], response_model=ContactOut, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[POST /contacts] Creating contact: {contact}")
    try:
        return await PhonebookController.create_contact(db, contact)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[POST /contacts] Failed to create contact: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not create contact")

@router.get("/contacts/search", tags=["Contact"], response_model=list[ContactOut])
async def search_contacts(
    query: str,
    skip: int = 0,
    limit: int = settings.PAGINATION_DEFAULT_PAGE,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[GET /contacts/search] query='{query}', skip={skip}, limit={limit}")
    try:
        results = await PhonebookController.search_contacts(db, query, skip, limit)
        if not results:
            msg = f"No contacts found matching query: '{query}'"
            logger.info(f"[GET /contacts/search] {msg}")
            raise HTTPException(status_code=404, detail=msg)
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[GET /contacts/search] Failed to search contacts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not search contacts")

@router.get("/contacts/{contact_id}", tags=["Contact"], response_model=ContactOut)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[GET /contacts/{contact_id}] Fetching contact")
    try:
        contact = await PhonebookController.get_contact(db, contact_id)
        if contact is None:
            msg = f"Contact with id={contact_id} not found"
            logger.warning(f"[GET /contacts/{contact_id}] {msg}")
            raise HTTPException(status_code=404, detail=msg)
        return contact
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[GET /contacts/{contact_id}] Failed to fetch contact: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not fetch contact")

@router.put("/contacts/{contact_id}", tags=["Contact"], response_model=ContactOut)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[PUT /contacts/{contact_id}] Updating with data: {contact}")
    try:
        updated = await PhonebookController.update_contact(db, contact_id, contact)
        if updated is None:
            msg = f"Contact with id={contact_id} not found"
            logger.warning(f"[PUT /contacts/{contact_id}] {msg}")
            raise HTTPException(status_code=404, detail=msg)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[PUT /contacts/{contact_id}] Failed to update contact: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not update contact")

@router.delete("/contacts/{contact_id}", tags=["Contact"], response_model=ContactOut)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"[DELETE /contacts/{contact_id}] Deleting contact")
    try:
        deleted = await PhonebookController.delete_contact(db, contact_id)
        if deleted is None:
            msg = f"Contact with id={contact_id} not found"
            logger.warning(f"[DELETE /contacts/{contact_id}] {msg}")
            raise HTTPException(status_code=404, detail=msg)
        return deleted
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[DELETE /contacts/{contact_id}] Failed to delete contact: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not delete contact")


@router.delete("/contacts/debug/all", tags=["Debug"])
async def delete_all_contacts(
    db: AsyncSession = Depends(get_db)
):
    logger.debug("[DELETE /contacts/debug/all] Deleting all contacts")
    try:
        await PhonebookController.delete_all_contacts(db)
        return {"message": "All contacts have been deleted."}
    except Exception as e:
        logger.exception(f"[DELETE /contacts/debug/all] Failed to delete all contacts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Could not delete all contacts")
