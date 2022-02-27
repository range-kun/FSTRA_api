FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.1.12

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml config.py ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

ADD ./fstr_api ./fstr_api
CMD ["uvicorn", "fstr_api:app", "--host", "0.0.0.0", "--port", "8888"]