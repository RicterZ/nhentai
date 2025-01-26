FROM python:3

WORKDIR /usr/src/nhentai

COPY . .
RUN pip install --no-cache-dir .

WORKDIR /output
ENTRYPOINT ["nhentai"]
