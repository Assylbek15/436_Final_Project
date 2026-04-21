# =========================
#  Frontend - React (Vite)
# =========================

# --- Stage 1: Build React project ---
FROM node:20 AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build


# --- Stage 2: Serve with Nginx ---
FROM nginx:latest

# Copy build output to nginx HTML root
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
