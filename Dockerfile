FROM node:16.16.0 as frontend
WORKDIR /usr/app
COPY package*.json ./
RUN npm install -g n
RUN npm ci --include=dev 

FROM python:3.9-slim as static
WORKDIR /usr/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

FROM static  as gunicorn
WORKDIR /usr/app
RUN pip install gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "star_burger.wsgi:application"]
