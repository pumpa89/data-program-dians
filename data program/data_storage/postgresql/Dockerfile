# postgres/Dockerfile
FROM postgres:13

COPY init.sql /docker-entrypoint-initdb.d/

ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=finance

EXPOSE 5432