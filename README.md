# PonyExpress - a messaging application

## Backend

The backend of the application is written in python using the [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/) framework.

### Setup

If you are using `poetry` on the command line, you can install the dependencies using

```bash
poetry install
```

If you are using `poetry` in your IDE, follow the IDE's instructions for setting up a
poetry project.

If you are managing your own virtual environment on the command line, you can install the
dependencies **with the virtual environment activated** using

```bash
python -m pip install -r requirements.txt
```

### Development

Start the backend server using any of the following commands:

- ```bash
  poetry run fastapi dev backend
  ```

- ```bash
  poetry run fastapi dev backend/main.py
  ```

- ```bash
  poetry run uvicorn backend:app --reload
  ```

- ```bash
  poetry run uvicorn backend.main:app --reload
  ```

If you are not using `poetry` or already have the `poetry` environment activated, you can
run the same commands without the `poetry run` prefix.

Once the server is running, you can make HTTP requests against `http://127.0.0.1:8000` or
`localhost:8000`. For example,

```http
GET http://127.0.0.1:8000/status

HTTP/1.1 204 No Content
```

You may also view the documentation:

- SwaggerUI: `http:127.0.0.1:8000/docs`
- Redocly: `http:127.0.0.1:8000/redoc`

### Testing

Tests are contained in the `backend/__tests__` module. You can run the tests via the
command-line using

```bash
poetry run pytest
```

You can also run them in your IDE.

#### Starlette's TestClient

Starlette comes with a `TestClient` object that can be used in testing. The best way to
use it is as a context object in a `pytest` fixture.

```python
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
```

- Include `client` as a parameter in your test method.
- Invoke one of the methods `get`, `post`, `put`, `delete` to get an `httpx.Response`
  object.
- Make assertions about the response status code and/or body.

```python
def test_hello_world(client):
    response = client.get("/hello_world")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```
