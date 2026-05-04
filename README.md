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

# Pony Express — DevOps Runbook

Full CI/CD deployment of the Pony Express React/FastAPI app on AWS.

## Architecture

```
GitHub → GitHub Actions → AWS ECR → AWS EC2 (inside VPC)
                ↓
         Terraform (infra)
         Ansible (config + hardening)
         Docker (packaging)
```

## What each tool does

| Tool | Role |
|---|---|
| Terraform | Creates VPC, EC2, ECR, IAM, security groups |
| Ansible | Installs Docker, applies CIS hardening on EC2 |
| Docker | Packages React and FastAPI into images |
| ECR | Stores Docker images in AWS |
| GitHub Actions | Orchestrates everything on every push |

---

## One-time setup (do this before first push)

### Step 1 — Create S3 bucket for Terraform state
```bash
aws s3 mb s3://ponyexpress-terraform-state --region us-east-1
```

### Step 2 — Create EC2 key pair
In AWS Console → EC2 → Key Pairs → Create key pair.
Name: `ponyexpress-key`. Download the `.pem` file.
```bash
chmod 400 ponyexpress-key.pem
```

### Step 3 — Run Terraform locally (first time only)
```bash
cd terraform
terraform init
terraform apply -var="my_ip=$(curl -s ifconfig.me)/32"
```
Note the outputs — you need these for GitHub Secrets.

### Step 4 — Set GitHub Secrets
Repo → Settings → Secrets and variables → Actions → New repository secret

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | From AWS IAM |
| `AWS_SECRET_ACCESS_KEY` | From AWS IAM |
| `EC2_SSH_PRIVATE_KEY` | Full contents of `.pem` file |
| `FRONTEND_ECR_URL` | From `terraform output frontend_ecr_url` |
| `BACKEND_ECR_URL` | From `terraform output backend_ecr_url` |

---

## Every deployment after that

```bash
git checkout -b feature/my-change
# make changes
git push origin feature/my-change
# open PR → tests run automatically
# merge to main → full pipeline runs
```

Pipeline jobs in order:
1. **test** — pytest + React tests
2. **terraform** — updates infrastructure if `.tf` files changed
3. **ansible** — patches and hardens EC2 (idempotent)
4. **build-and-push** — Docker images → ECR
5. **deploy** — SSH into EC2, pull images, restart containers

---

## Local development

```bash
docker-compose up --build
# Frontend: http://localhost:80
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Troubleshooting (escalation guide)

| Symptom | Check first | Escalate if |
|---|---|---|
| Tests failing | Read pytest/npm output in Actions | Flaky tests with no clear cause |
| Terraform errors | Check AWS Console for resource conflicts | IAM permission denied errors |
| Ansible fails | Check SSH connectivity, EC2 state | Playbook runs but app still broken |
| Docker build fails | Check Dockerfile, requirements.txt | Base image pull failures |
| App not responding | `docker ps` on EC2, check port 80/8000 | Both containers running but no response |

---

## Teardown (avoid AWS charges)

```bash
cd terraform
terraform destroy -var="my_ip=$(curl -s ifconfig.me)/32"
```