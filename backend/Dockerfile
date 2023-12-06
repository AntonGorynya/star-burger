FROM python:3.9-slim as static
WORKDIR /usr/app/backend
COPY . .
RUN mkdir -p /usr/app/staticfiles/assets
RUN mkdir -p /usr/app/staticfiles/bundles
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 manage.py collectstatic --noinput

FROM static  as gunicorn
WORKDIR /usr/app/backend
RUN pip install gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "star_burger.wsgi:application"]
