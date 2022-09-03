from sqlalchemy import create_engine
import pandas as pd
# import psycopg2

conn = create_engine('postgresql://airflow:airflow@localhost/airflow')

def select(sql):
    print(pd.read_sql(conn, sql))

sql = """
    select version();
"""

select(sql)

