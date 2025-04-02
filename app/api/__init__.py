from fastapi import APIRouter
from . import phonebook

api_router = APIRouter()
api_router.include_router(phonebook.router, prefix="/phonebook")
