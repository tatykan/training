import datetime as dt
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

def fetch_data():
    from library.titanic_main import connection
    postgres = connection(host='HOST_HERE', 
                      dbname='DBNAME_HERE', 
                      user='USER_HERE', 
                      password='PASSWORD_HERE')
    postgres.query_table('SELECT * FROM titanic', columns=['survived', 'pclass', 'name', 'sex', 'age', 'sib_spouse', 'parent_child', 'fare'])
    titanic = postgres.df
    postgres.close_connection()
    titanic.to_csv(r'./airflow/stage/titanic_stage.csv', index=False)
    
def add_title():
    import pandas as pd
    titanic = pd.read_csv(r'./airflow/stage/titanic_stage.csv')
    titanic['title'] = [x.split('.')[0] for x in titanic['name']]
    titanic.to_csv(r'./airflow/stage/titanic_stage.csv', index=False)

def add_age_group():
    import pandas as pd
    titanic = pd.read_csv(r'./airflow/stage/titanic_stage.csv')
    age_group = []
    for age in titanic['age']:
        if age < 1:
            age_group.append('00 years')
        elif age <= 4:
            age_group.append('01-04 years')
        elif age <= 9:
            age_group.append('05-09 years')
        elif age <= 14:
            age_group.append('10-14 years')
        elif age <= 19:
            age_group.append('15-19 years')
        elif age <= 24:
            age_group.append('20-24 years')
        elif age <= 29:
            age_group.append('25-29 years')
        elif age <= 34:
            age_group.append('30-34 years')
        elif age <= 39:
            age_group.append('35-39 years')
        elif age <= 44:
            age_group.append('40-44 years')
        elif age <= 49:
            age_group.append('45-49 years')
        elif age <= 54:
            age_group.append('50-54 years')
        else:
            age_group.append('55+ years')
    titanic['age_group'] = age_group
    titanic.to_csv(r'./airflow/stage/titanic_stage.csv', index=False)
    
def store_data():
    import pandas as pd
    from library.titanic_main import connection
    titanic = pd.read_csv(r'./airflow/stage/titanic_stage.csv')
    postgres = connection(host='HOST_HERE', 
                      dbname='DBNAME_HERE', 
                      user='USER_HERE', 
                      password='PASSWORD_HERE')
    postgres.create_table('titanic_final', titanic)
    postgres.fill_table('titanic_final', titanic)
    postgres.close_connection()

    
    
default_args = {
    'owner': 'Adam Raveret',
    'start_date': dt.datetime(2019, 1, 27),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=2)
}


with DAG('titanic_example',
         default_args=default_args,
         schedule_interval='0 0 * * *'
         ) as dag:
    retrieve_data = PythonOperator(task_id='fetch_data',
                               python_callable=fetch_data)
    transformation_1 = PythonOperator(task_id='add_title',
                               python_callable=add_title)
    transformation_2 = PythonOperator(task_id='add_age_group',
                               python_callable=add_age_group)
    save_data = PythonOperator(task_id='store_data',
                               python_callable=store_data)
    
retrieve_data >> transformation_1 >> transformation_2 >> save_data
