# Dockerfile

FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Copiar as dependências
COPY pyproject.toml poetry.lock* ./

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências da aplicação
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

# Copiar o código da aplicação
COPY . .

# Expor a porta 8000 para o FastAPI
EXPOSE 8000

# Definir o comando para rodar a aplicação FastAPI com o uvicorn
CMD ["poetry", "run", "uvicorn", "fast_zero.app:app", "--host", "0.0.0.0", "--reload"]

