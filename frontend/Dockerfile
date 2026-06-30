# Frontend development image
FROM node:lts AS dev

LABEL org.opencontainers.image.title="puckhate-frontend"
LABEL org.opencontainers.image.description="puckhate frontend dev server"

WORKDIR /app
COPY package*.json ./
RUN set -eux; npm install
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
