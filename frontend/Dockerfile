# Stage 1: Base image
FROM node:lts AS dependencies

LABEL org.opencontainers.image.title="puckcurl Frontend"
LABEL org.opencontainers.image.description="puckcurl frontend dependency pack"

WORKDIR /app
COPY package*.json ./
RUN set -eux; npm install
COPY . .

# Stage 2: Dev server
FROM dependencies AS dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# Stage 3: Asset builder - emits to /backend/spa
FROM dependencies AS builder
RUN set -eux; npm run build
