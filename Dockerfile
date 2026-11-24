# Web app image: serves index.html with nginx
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
