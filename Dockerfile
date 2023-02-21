# 
FROM python:3.10.9 as requirements-stage

# 
WORKDIR /tmp

# 
RUN pip install poetry

# 
COPY ./pyproject.toml ./poetry.lock* /tmp/

# 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# 
FROM python:3.10.9

# 
WORKDIR /ingesion-fastapi

# 
COPY --from=requirements-stage /tmp/requirements.txt /ingesion-fastapi/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /ingesion-fastapi/requirements.txt

# 
COPY ./app /ingesion-fastapi/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
