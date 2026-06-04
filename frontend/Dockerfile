FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
# devDependencies (typescript, vite) are required for `npm run build`
RUN npm ci --include=dev
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
