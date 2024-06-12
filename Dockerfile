FROM node:20.12.2-alpine3.19

WORKDIR /app

RUN mkdir -p /app/node_modules

RUN mkdir -p /app/downloads

COPY package*.json ./


RUN npm install

COPY  . .

ENV API_KEY=$API_KEY

EXPOSE 3000


CMD ["node", "server.js"]