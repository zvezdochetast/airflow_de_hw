# Используем официальный образ Airflow
FROM apache/airflow:2.10.4

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

USER root

# Копируем файл requirements.txt в контейнер
COPY requirements.txt /opt/airflow/

# Копируем файл DAG в контейнер
COPY ./dags/bitcoin_to_clickhouse.py /opt/airflow/dags/

# Копируем сертификаты в контейнер
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем ваш сертификат
COPY IntermediateCA.crt /usr/local/share/ca-certificates/Yandex/
COPY RootCA.crt /usr/local/share/ca-certificates/Yandex/
RUN chmod 644 /usr/local/share/ca-certificates/Yandex/RootCA.crt
RUN update-ca-certificates

USER airflow

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Устанавливаем при необходимлсти другие средства для работы с кликхаус
# RUN pip install apache-airflow-providers-clickhouse
# RUN pip install airflow-clickhouse-plugin

# Настроим рабочую директорию для Airflow
# WORKDIR /opt/airflow
