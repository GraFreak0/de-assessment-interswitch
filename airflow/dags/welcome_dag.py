import requests
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
# from airflow.utils.email import send_email

def print_welcome():
    print("Welcome to the Airflow platform!")

def print_date():
    print(f"Execution date is {datetime.now()}")

def print_goodbye():
    print("Thank you for using the Airflow platform! Goodbye!")

# def failure_callback(context):
#     failed_task = context.get('task_instance').task_id
#     error_message = context.get('exception')

#     subject = f"Airflow Task Failed: {failed_task}"
#     body = f"""
#     <h3>Task {failed_task} has failed.</h3>
#     <p><strong>DAG:</strong> {context.get('dag').dag_id}</p>
#     <p><strong>Execution Date:</strong> {context.get('execution_date')}</p>
#     <p><strong>Error:</strong> {error_message}</p>
#     """

#     send_email(
#         to="j_oyin@yahoo.com",
#         subject=subject,
#         html_content=body
#     )

dag = DAG(
    dag_id="welcome_dag",
    default_args = {
        'start_date': days_ago(1)
        # 'on_failure_callback': failure_callback
    },
    schedule_interval='0 23 * * *',
    catchup=False
)

print_welcome_task = PythonOperator(
    task_id="print_welcome",
    python_callable=print_welcome,
    dag=dag
)

print_date_task = PythonOperator(
    task_id="print_date",
    python_callable=print_date,
    dag=dag
)

print_goodbye_task = PythonOperator(
    task_id="print_goodbye",
    python_callable=print_goodbye,
    dag=dag
)

# send_success_email = EmailOperator(
#     task_id="send_success_email",
#     to="j_oyin@yahoo.com",
#     subject="Airflow DAG Execution Successful",
#     html_content="All tasks in the DAG 'welcome_dag' completed successfully.",
#     dag=dag
# )

print_welcome_task >> print_date_task >> print_goodbye_task ###>> send_success_email