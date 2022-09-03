import os
import json
from datetime import datetime
from urllib import response

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
# from airflow.providers.telegram.operators.telegram import TelegramOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

TELEGRAM_BOT_TOKEN = '5596926666:AAGa-D6ZcLvwlcKYDGPFXwWz6ratSz6bwFM'


def context_handler_krd(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='getting_weather_krd'))
    ti.xcom_push(key='description', value=response.get('weather')[0].get('description'))
    ti.xcom_push(key='temp', value=response.get('main').get('temp'))
    ti.xcom_push(key='temp_min', value=response.get('main').get('temp_min'))
    ti.xcom_push(key='temp_max', value=response.get('main').get('temp_max'))
    ti.xcom_push(key='feels_like', value=response.get('main').get('feels_like'))
    ti.xcom_push(key='pressure', value=response.get('main').get('pressure'))
    ti.xcom_push(key='humidity', value=response.get('main').get('humidity'))
    ti.xcom_push(key='wind_speed', value=response.get('wind').get('speed'))
    ti.xcom_push(key='name', value=response.get('name'))
    ti.xcom_push(key='sunset', value=response.get('sys').get('sunset'))
    ti.xcom_push(key='sunrise', value=response.get('sys').get('sunrise'))

def context_handler_mkp(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='getting_weather_mkp'))
    ti.xcom_push(key='description', value=response.get('weather')[0].get('description'))
    ti.xcom_push(key='temp', value=response.get('main').get('temp'))
    ti.xcom_push(key='temp_min', value=response.get('main').get('temp_min'))
    ti.xcom_push(key='temp_max', value=response.get('main').get('temp_max'))
    ti.xcom_push(key='feels_like', value=response.get('main').get('feels_like'))
    ti.xcom_push(key='pressure', value=response.get('main').get('pressure'))
    ti.xcom_push(key='humidity', value=response.get('main').get('humidity'))
    ti.xcom_push(key='wind_speed', value=response.get('wind').get('speed'))
    ti.xcom_push(key='name', value=response.get('name'))
    ti.xcom_push(key='sunset', value=response.get('sys').get('sunset'))
    ti.xcom_push(key='sunrise', value=response.get('sys').get('sunrise'))
    # return response.get('weather')

city_dict = {
    'Krasnodar' : {'lat': 45.039268, 'lon': 38.987221},
    'Maikop'    : {'lat': 44.606509, 'lon': 40.107755}
}

with DAG(
    dag_id='weather_data',
    schedule_interval='@hourly',
    start_date=datetime(2022,9,2),
    catchup=False,
    max_active_runs=1
) as dag:
    # drop_table = PostgresOperator(
    #     task_id='drop_table',
    #     postgres_conn_id='postgres_default',
    #     sql="""
    #         drop table if exists weather;
    #     """
    # )
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
            create table if not exists weather(
                id              serial primary key,
                name            varchar(50),
                temp            float,
                temp_feels_like float,
                temp_min        float,
                temp_max        float,
                description     varchar(50),
                wind_speed      float,
                humidity        float,
                pressure        smallint,
                sunset          int,
                sunrise         int
            );
        """
    )

    getting_weather_krd = SimpleHttpOperator(
        task_id='getting_weather_krd',
        method='GET',
        endpoint='/data/2.5/weather',
        data={
            'lat': 45.039268,
            'lon': 38.987221,
            'appid':'ebcf05a4beaccac19a1759922fb4ff22',
            'lang':'ru',
            'units':'metric'

            },
            do_xcom_push=True
        )

    getting_weather_mkp = SimpleHttpOperator(
        task_id='getting_weather_mkp',
        method='GET',
        endpoint='/data/2.5/weather',
        data={
            'lat': 44.606509,
            'lon': 40.107755,
            'appid':'ebcf05a4beaccac19a1759922fb4ff22',
            'lang':'ru',
            'units':'metric'

            },
            do_xcom_push=True
        )

    check_weather_krd = PythonOperator(
        task_id='check_weather_krd',
        python_callable=context_handler_krd,
        
    )

    check_weather_mkp = PythonOperator(
        task_id='check_weather_mkp',
        python_callable=context_handler_mkp,
        
    )

    insert_weather_krd = PostgresOperator(
        task_id='insert_weather_krd',
        postgres_conn_id='postgres_default',
        sql="""
            insert into weather(
                name,
                temp,
                temp_feels_like,
                temp_min,
                temp_max,
                description,
                wind_speed,
                humidity,
                pressure,
                sunset,
                sunrise
            ) values (
                '{{ ti.xcom_pull(task_ids='check_weather_krd', key='name') }}',
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='temp') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='feels_like') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='temp_min') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='temp_max') }},
                '{{ ti.xcom_pull(task_ids='check_weather_krd', key='description') }}',
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='wind_speed') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='humidity') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='pressure') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='sunset') }},
                {{ ti.xcom_pull(task_ids='check_weather_krd', key='sunrise') }}
            );
        """
    )

insert_weather_mkp = PostgresOperator(
        task_id='insert_weather_mkp',
        postgres_conn_id='postgres_default',
        sql="""
            insert into weather(
                name,
                temp,
                temp_feels_like,
                temp_min,
                temp_max,
                description,
                wind_speed,
                humidity,
                pressure,
                sunset,
                sunrise
            ) values (
                '{{ ti.xcom_pull(task_ids='check_weather_mkp', key='name') }}',
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='temp') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='feels_like') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='temp_min') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='temp_max') }},
                '{{ ti.xcom_pull(task_ids='check_weather_mkp', key='description') }}',
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='wind_speed') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='humidity') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='pressure') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='sunset') }},
                {{ ti.xcom_pull(task_ids='check_weather_mkp', key='sunrise') }}
            );
        """
    )


create_table >> getting_weather_krd >> check_weather_krd >> insert_weather_krd >> getting_weather_mkp >> check_weather_mkp >> insert_weather_mkp
# >> getting_weather_mkp >> check_weather_mkp