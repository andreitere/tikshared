FROM node:20.12.2-alpine3.19

WORKDIR /app

RUN mkdir -p /app/node_modules && chown -R node:node /app

RUN mkdir -p /app/downloads

COPY package*.json ./


RUN npm install

USER node

COPY --chown=node:node . .

EXPOSE 3000


CMD ["node", "server.js"]