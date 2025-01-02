#!/bin/bash

# Создание необходимых директорий
echo "Создание директорий ./dags, ./logs, ./plugins, ./config"
mkdir -p ./dags ./logs ./plugins ./config

# Создание файла .env с AIRFLOW_UID
echo "Создание файла .env с AIRFLOW_UID"
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Установка прав доступа для всех директорий
echo "Установка прав доступа для директорий"
chmod -R 777 ./dags ./logs ./plugins ./config

# Получение сертификатов для yc
curl https://storage.yandexcloud.net/cloud-certs/RootCA.pem --output RootCA.crt
curl https://storage.yandexcloud.net/cloud-certs/IntermediateCA.pem --output IntermediateCA.crt

docker-compose build
 