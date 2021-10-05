## ---- compile image -----------------------------------------------
FROM python:3.8-slim  AS base
RUN python -m venv /app/env
ENV PATH="/app/env/bin:$PATH"

RUN pip install --upgrade pip
COPY requirements.txt .
## pip install is fast here (while slow without the venv) :
RUN . /app/env/bin/activate && pip install -r requirements.txt

## Make sure we use the virtualenv:
ENV PATH="/app/env/bin:$PATH"
ENV PYTHONPATH="/app/:$PYTHONPATH"
COPY . /app/
WORKDIR /app/

ENTRYPOINT [ "python", "main.py" ]