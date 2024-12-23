from snowflake.core import Root
import snowflake.connector
from datetime import timedelta
from snowflake.core.task import Task , StoredProcedureCall
import procedures
from snowflake.snowpark import Session
from snowflake.snowpark.types import StringType
from snowflake.core.task.context import TaskContext
import os

from snowflake.core.task.dagv1 import DAG , DAGTask , DAGOperation , CreateMode , DAGTaskBranch

#conn = snowflake.connector.connect()

 conn = snowflake.connector.connect(
     user=os.environ.get('SNOWFLAKE_USER'),
     password=os.environ.get('SNOWFLAKE_PASSWORD'),
     account=os.environ.get("SNOWFLAKE_ACCOUNT"),
     warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
     database=os.environ.get('SNOWFLAKE_DATABASE'),
     schema=os.environ.get('SNOWFLAKE_SCHEMA'),
     role=os.environ.get('SNOWFLAKE_ROLE'))


print("connection established")
print(conn)

root = Root(conn)
print(root)

my_task = Task("my_task",StoredProcedureCall(procedures.hello_procedure,\
    stage_location="@dev_deployment"),warehouse="compute_wh",schedule=timedelta(hours=1))

tasks = root.databases["demo_db"].schemas['public'].tasks
#tasks.create(my_task)

# create dag  
with DAG("my_dag",schedule=timedelta(days=1),stage_location='@dev_deployment',warehouse="compute_wh") as dag:
  dag_task_1 =  DAGTask("my_hello_task",StoredProcedureCall(procedures.hello_procedure,args=["sushmitha"],\
    input_types=[StringType()],return_type=StringType(), packages=["snowflake-snowpark-python"],imports=['@dev_deployment/my_snowpark_project/app.zip'],\
    stage_location='@dev_deployment'),warehouse="compute_wh")
  
  dag_task_2 =  DAGTask("my_test_task",StoredProcedureCall(procedures.test_procedure,\
    packages=["snowflake-snowpark-python"],imports=["@dev_deployment/my_snowpark_project/app.zip"],\
    stage_location="@dev_deployment"),warehouse="compute_wh")
  
  dag_task_1 >> dag_task_2

  schema = root.databases["demo_db"].schemas["public"]
  dag_op = DAGOperation(schema)
  dag_op.deploy(dag,CreateMode.or_replace)