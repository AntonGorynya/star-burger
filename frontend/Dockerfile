FROM node:16.16.0 as frontend
WORKDIR /usr/app/frontend
COPY . .
RUN npm install -g n
RUN npm ci --include=dev
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir staticfiles/bundles --public-url="./"
