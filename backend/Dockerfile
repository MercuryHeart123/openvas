FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& apt-get install -y --no-install-recommends nmap 

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "./manage.py", "runserver", "0.0.0.0:8081"]
