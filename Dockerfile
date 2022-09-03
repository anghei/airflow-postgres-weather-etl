FROM apache/airflow
COPY requirements.txt /
USER airflow
RUN pip install --user -r /requirements.txt