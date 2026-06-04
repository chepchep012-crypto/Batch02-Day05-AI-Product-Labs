FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
# devDependencies (typescript, vite) are required for `npm run build`
RUN npm ci --include=dev
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
