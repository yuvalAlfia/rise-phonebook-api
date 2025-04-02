# Rise Phonebook API

This application provides an easy-to-use API for managing contacts. Users can create, read, update, delete, and search contacts efficiently.

## Getting Started

To start using the Rise Phonebook API, you need to set up the environment using Docker. Follow these steps to get started:

1. Navigate to the project directory.
2. Run the following command to build and run the Docker containers:

```bash
  docker-compose up --build
```

Once the Docker environment is up and running, a Swagger UI is available at:

```
http://localhost:8000/docs
```

The Swagger UI provides a user-friendly interface to interact with the API.

## API Endpoints

#### Get Contacts:

Retrieve a paginated list of contacts.

```
GET http://localhost:8000/phonebook/contacts?skip=0&limit=10
```

```bash
  curl -X 'GET' \
    'http://localhost:8000/phonebook/contacts?skip=0&limit=10' \
    -H 'accept: application/json'
```

#### Create a Contact:

Create a new contact.

```
POST http://localhost:8000/phonebook/contacts
```

```bash
  curl -X 'POST' \
    'http://localhost:8000/phonebook/contacts' \
    -H 'Content-Type: application/json' \
    -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St"
  }'
```

#### Search Contacts:

Search for contacts matching a query.

```
GET http://localhost:8000/phonebook/contacts/search?query=John
```

```bash
  curl -X 'GET' \
    'http://localhost:8000/phonebook/contacts/search?query=John' \
    -H 'accept: application/json'
```

#### Update a Contact:

Search for contacts matching a query.

```
PUT http://localhost:8000/phonebook/contacts/{contact_id}
```

```bash
  curl -X 'PUT' \
    'http://localhost:8000/phonebook/contacts/1' \
    -H 'Content-Type: application/json' \
    -d '{
    "address": "456 New St"
  }'
```

#### Delete a Contact:

Delete a contact by its ID.

```
DELETE http://localhost:8000/phonebook/contacts/{contact_id}
```

```bash
  curl -X 'DELETE' \
    'http://localhost:8000/phonebook/contacts/1' \
    -H 'accept: application/json'
```
## Metrics and Caching

This API integrates with Prometheus to provide metrics on HTTP request counts, response times, and cache usage. Metrics are exposed at:

```
http://localhost:8000/metrics
```

These metrics help monitor API performance in real time.

In addition, the API implements caching (using Redis) for endpoints such as listing and searching contacts. Cached results are stored for a duration specified in the configuration (default TTL of 3600 seconds). This helps improve performance for frequently accessed data while ensuring that changes (via create/update/delete) clear the cache to maintain data consistency.



## Tests

To run the tests with pytest, first start the app using:

```bash
  docker-compose up --build
```

Make sure that you have `pytest` and `requests` installed in your environment. If not, install them using:

```bash
  pip install pytest
  pip install requests
```

Then run the tests using:

```bash
  pytest
```