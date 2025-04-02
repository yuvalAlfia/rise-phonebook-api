import os
import pytest
import requests
import logging
from app.core.config import settings, Logs

logger = logging.getLogger("test_phonebook")
logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)

@pytest.fixture(autouse=True, scope="session")
def clear_database():
    logger.info("Clearing database before test session")
    resp = requests.delete(f"{settings.HOST_URL}/debug/all")
    yield
    logger.info("Clearing database after test session")
    requests.delete(f"{settings.HOST_URL}/debug/all")

test_contact = {
    "first_name": "Testy",
    "last_name": "McTestFace",
    "phone": "1234567890",
    "address": "123 Test Lane"
}

updated_contact = {
    "first_name": "Updated",
    "last_name": "User",
    "phone": "123456789",
    "address": "456 Updated St"
}

@pytest.fixture(scope="module")
def created_id():
    logger.info("Creating contact for test suite")
    response = requests.post(settings.HOST_URL, json=test_contact)
    assert response.status_code == 201, f"Failed to create contact: {response.text}"
    contact_id = response.json()["id"]
    yield contact_id
    logger.info(f"Cleaning up contact id={contact_id}")
    delete_response = requests.delete(f"{settings.HOST_URL}/{contact_id}")
    assert delete_response.status_code == 200, f"Failed to delete contact during cleanup: {delete_response.text}"

def test_read_contact(created_id):
    logger.info(f"Testing read_contact with id={created_id}")
    response = requests.get(f"{settings.HOST_URL}/{created_id}")
    assert response.status_code == 200, f"Read failed: {response.text}"
    assert response.json()["first_name"] == test_contact["first_name"]

def test_update_contact(created_id):
    logger.info(f"Testing update_contact with id={created_id}")
    response = requests.put(f"{settings.HOST_URL}/{created_id}", json=updated_contact)
    assert response.status_code == 200, f"Update failed: {response.text}"
    assert response.json()["first_name"] == updated_contact["first_name"]

def test_search_contact():
    logger.info("Testing search_contact with query='Updated'")
    response = requests.get(f"{settings.HOST_URL}/search?query=Updated")
    assert response.status_code == 200, f"Search failed: {response.text}"
    assert isinstance(response.json(), list)

def test_delete_contact():
    logger.info("Testing delete_contact by creating and deleting")
    res = requests.post(settings.HOST_URL, json=test_contact)
    assert res.status_code == 201, f"Failed to create contact for delete test: {res.text}"
    contact_id = res.json()["id"]

    logger.debug(f"Deleting contact id={contact_id}")
    response = requests.delete(f"{settings.HOST_URL}/{contact_id}")
    assert response.status_code == 200, f"Delete failed: {response.text}"

    followup = requests.get(f"{settings.HOST_URL}/{contact_id}")
    assert followup.status_code == 404, f"Expected 404 after delete, got: {followup.status_code}"

def test_create_contact_duplicate_phone():
    logger.info("Testing duplicate contact creation")
    contact_data = {
        "first_name": "Dup",
        "last_name": "Test",
        "phone": "5555555555",
        "address": "Dup Address"
    }
    resp1 = requests.post(settings.HOST_URL, json=contact_data)
    assert resp1.status_code == 201, f"Initial creation failed: {resp1.text}"
    contact_data2 = {
        "first_name": "Dup2",
        "last_name": "Test2",
        "phone": "5555555555",
        "address": "Dup Address 2"
    }
    resp2 = requests.post(settings.HOST_URL, json=contact_data2)
    assert resp2.status_code == 400, f"Expected duplicate error, got: {resp2.text}"
    assert "Phone number already exists" in resp2.json()["detail"]
    delete_resp = requests.delete(f"{settings.HOST_URL}/{resp1.json()['id']}")
    assert delete_resp.status_code == 200

def test_update_contact_duplicate_phone():
    logger.info("Testing duplicate phone update")
    contact1 = {
        "first_name": "First",
        "last_name": "User",
        "phone": "6666666666",
        "address": "Address 1"
    }
    contact2 = {
        "first_name": "Second",
        "last_name": "User",
        "phone": "7777777777",
        "address": "Address 2"
    }
    res1 = requests.post(settings.HOST_URL, json=contact1)
    res2 = requests.post(settings.HOST_URL, json=contact2)
    assert res1.status_code == 201
    assert res2.status_code == 201
    id2 = res2.json()["id"]
    update_data = {"phone": "6666666666"}
    resp = requests.put(f"{settings.HOST_URL}/{id2}", json=update_data)
    assert resp.status_code == 400, f"Expected duplicate error on update, got: {resp.text}"
    assert "Phone number already exists" in resp.json()["detail"]
    del1 = requests.delete(f"{settings.HOST_URL}/{res1.json()['id']}")
    del2 = requests.delete(f"{settings.HOST_URL}/{id2}")
    assert del1.status_code == 200
    assert del2.status_code == 200

def test_get_nonexistent_contact():
    logger.info("Testing error handling for non-existent contact")
    response = requests.get(f"{settings.HOST_URL}/999999")
    assert response.status_code == 404, f"Expected 404 for non-existent contact, got: {response.status_code}"
    assert "not found" in response.json()["detail"].lower()

def test_list_contacts_cache():
    logger.info("Testing cache for list_contacts")
    resp1 = requests.get(f"{settings.HOST_URL}?skip=0&limit=10")
    assert resp1.status_code == 200, f"First list_contacts failed: {resp1.text}"
    data1 = resp1.json()
    resp2 = requests.get(f"{settings.HOST_URL}?skip=0&limit=10")
    assert resp2.status_code == 200, f"Second list_contacts failed: {resp2.text}"
    data2 = resp2.json()
    assert data1 == data2

def test_search_contacts_cache():
    logger.info("Testing cache for search_contacts")
    resp1 = requests.get(f"{settings.HOST_URL}/search?query=Updated&skip=0&limit=10")
    assert resp1.status_code == 200, f"First search_contacts failed: {resp1.text}"
    data1 = resp1.json()
    resp2 = requests.get(f"{settings.HOST_URL}/search?query=Updated&skip=0&limit=10")
    assert resp2.status_code == 200, f"Second search_contacts failed: {resp2.text}"
    data2 = resp2.json()
    assert data1 == data2
