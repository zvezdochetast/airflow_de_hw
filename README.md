# Template airflow for Yandex Cloud VM.

Шаблон предназначен для разворачивания инстанса airflow и запуска DAG-а в Yandex Cloud.

### Пререквизиты 
1. Настроена и запущена VM в YC
2. На VM установлен docker и docker-compose

### Развертывание 
1. Подключиться к VM по ssh
2. Запустить команды:
``` 
git clone https://github.com/zvezdochetast/airflow_de_hw.git
cd airflow_de_hw
chmod +x init.sh 
./init.sh
docker-compose up airflow-init 
docker-compose up -d
```
:::tip
Если установлен docker-compose-plugin, то следует использовать команды синтаксиса `docker compose ...`.
Для проверки версии docker-compose или docker-compose-plugin выполните: `apt list --installed | grep compose`
:::

### Пререквизиты для запуска DAG-а
DAG `bitcoin_to_clickhouse.py` предназначен получения данных по API и сохранения результатов в облачном инстансе Clickhouse YC.
Концептуальная схема Dag-a: 
- отправить запрос в API на конечную точку `https://api.coincap.io/v2/rates/bitcoin`;
- распарсить пришедший результат;
- положить данные в БД через insert в таблицу `Analytics`.

3. Для запуска DAG-а установлен облачный инстанс БД Clickhouse в Yandex Cloud, в котором создана таблица `Analytics`:
```sql
CREATE TABLE analytics (
    id String COMMENT 'Unique identifier of the asset',
    symbol String COMMENT 'Symbol of the asset',
    currencySymbol Nullable(String) COMMENT 'Symbol of the currency, nullable',
    type String COMMENT 'Type of the asset (e.g., cryptocurrency)',
    rateUsd Float64 COMMENT 'Exchange rate in USD',
    timestamp UInt64 COMMENT 'Timestamp in milliseconds'
) ENGINE = MergeTree()
ORDER BY (id, timestamp)
SETTINGS index_granularity = 8192;

```
4. Настроено публичное подключение к облачному инстансу БД YC на порту `9440`.
