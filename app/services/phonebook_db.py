from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete
from app.models.models import Contact
from app.schemas.schemas import ContactCreate, ContactUpdate
from sqlalchemy.exc import IntegrityError
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("phonebook_db", settings.LOG_LEVEL)

class ContactsDBService:

    @staticmethod
    async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = settings.PAGINATION_DEFAULT_PAGE):
        try:
            logger.debug(f"[DB] Fetching contacts with skip={skip}, limit={limit}")
            result = await db.execute(select(Contact).offset(skip).limit(limit))
            contacts = result.scalars().all()
            logger.info(f"[DB] Fetched {len(contacts)} contacts")
            return contacts
        except Exception as e:
            logger.exception(f"[DB] Failed to fetch contacts: {e}")
            raise

    @staticmethod
    async def get_contact(db: AsyncSession, contact_id: int):
        try:
            logger.debug(f"[DB] Fetching contact with id={contact_id}")
            result = await db.execute(select(Contact).where(Contact.id == contact_id))
            contact = result.scalars().first()
            if not contact:
                logger.warning(f"[DB] Contact not found: id={contact_id}")
            return contact
        except Exception as e:
            logger.exception(f"[DB] Failed to fetch contact id={contact_id}: {e}")
            raise

    @staticmethod
    async def create_contact(db: AsyncSession, contact: ContactCreate):
        try:
            logger.info("[DB] Creating new contact")
            db_contact = Contact(**contact.model_dump())
            db.add(db_contact)
            await db.commit()
            await db.refresh(db_contact)
            logger.info(f"[DB] Contact created successfully: id={db_contact.id}")
            return db_contact
        except IntegrityError:
            logger.warning(f"[DB] Phone number already exists: {contact.phone}")
            await db.rollback()
            raise ValueError("Phone number already exists")
        except Exception as e:
            logger.exception(f"[DB] Failed to create contact: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def update_contact(db: AsyncSession, contact_id: int, contact: ContactUpdate):
        try:
            logger.debug(f"[DB] Updating contact id={contact_id}")
            db_contact = await ContactsDBService.get_contact(db, contact_id)
            if not db_contact:
                logger.warning(f"[DB] Contact to update not found: id={contact_id}")
                return None
            for field, value in contact.model_dump(exclude_unset=True).items():
                setattr(db_contact, field, value)
            await db.commit()
            await db.refresh(db_contact)
            logger.info(f"[DB] Contact updated successfully: id={contact_id}")
            return db_contact
        except IntegrityError:
            logger.warning(f"[DB] Phone number already exists during update: {contact.phone}")
            await db.rollback()
            raise ValueError("Phone number already exists")
        except Exception as e:
            logger.exception(f"[DB] Failed to update contact id={contact_id}: {e}")
            raise

    @staticmethod
    async def delete_contact(db: AsyncSession, contact_id: int):
        try:
            logger.debug(f"[DB] Deleting contact id={contact_id}")
            db_contact = await ContactsDBService.get_contact(db, contact_id)
            if not db_contact:
                logger.warning(f"[DB] Contact to delete not found: id={contact_id}")
                return None
            await db.delete(db_contact)
            await db.commit()
            logger.info(f"[DB] Contact deleted successfully: id={contact_id}")
            return db_contact
        except Exception as e:
            logger.exception(f"[DB] Failed to delete contact id={contact_id}: {e}")
            raise

    @staticmethod
    async def search_contacts(db: AsyncSession, query: str, skip: int = 0, limit: int = settings.PAGINATION_DEFAULT_PAGE):
        try:
            logger.debug(f"[DB] Searching contacts with query='{query}', skip={skip}, limit={limit}")
            stmt = (
                select(Contact)
                .where(
                    or_(
                        Contact.first_name.ilike(f"%{query}%"),
                        Contact.last_name.ilike(f"%{query}%"),
                        Contact.phone.ilike(f"%{query}%"),
                    )
                )
                .order_by(Contact.first_name)
                .offset(skip)
                .limit(limit)
            )
            result = await db.execute(stmt)
            results = result.scalars().all()
            logger.info(f"[DB] Found {len(results)} contacts matching query='{query}'")
            return results
        except Exception as e:
            logger.exception(f"[DB] Failed to search contacts with query='{query}': {e}")
            raise

    @staticmethod
    async def delete_all_contacts(db: AsyncSession):
        try:
            logger.warning("[DB] Deleting all contacts from database")
            await db.execute(delete(Contact))
            await db.commit()
            logger.info("[DB] All contacts deleted successfully")
        except Exception as e:
            logger.exception(f"[DB] Failed to delete all contacts: {e}")
            raise
