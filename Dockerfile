FROM python:3

WORKDIR /usr/src/nhentai
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install .

WORKDIR /output
ENTRYPOINT ["nhentai"]
