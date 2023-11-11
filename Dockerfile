FROM node:16.16.0
WORKDIR /usr/app
COPY package*.json ./
RUN npm install -g n
RUN npm ci --include=dev 
