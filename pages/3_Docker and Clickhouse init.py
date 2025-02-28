import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import clickhouse_connect
import subprocess

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data
from streamlit_funcs.helpers import toggle_check_hide, toggle_run_mode

get_data()
toggle_run_mode()

st.header('Start docker, init clickhouse')

if not st.session_state.run_mode and not st.session_state.check_hide:
    st.info('If you run project without containers, clickhouse database code will not work. Yon may only see/copy it to another project')
st.text('To start docker in root directory enter the command: ')
st.code('docker compose up -d --build', 'bash')
st.text('Docker will download packages and libraries required to create the streamlit container and download the clickhouse container. It will take some time.')
st.subheader('Initial Docker Setup')
st.markdown('''Create user with sha256 pass and rm default user (./users/default-user.xml)
past file `konsin1988-user.xml` in "users" dir''')
st.markdown('Enable SQL user mode:')
st.text('''
-    <access_management>1</access_management>         
-    <named_collection_control>1</named_collection_control>
-    <show_named_collections>1</show_named_collections>
-    <show_named_collections_secrets>1</show_named_collections_secrets>''')

st.text('Get clickhouse client from docker')
st.code(r"""st.write(clickhouse_connect.get_client(host = 'clickhouse-server', 
                                        port = '8123', 
                                        user = 'konsin1988', 
                                        password = 'konsin1988konsin1988')""")

if st.session_state.run_mode:
    button_col, exception_col = st.columns([0.2, 0.8])
    if button_col.button('Run code', key='get_client'):
        try:
            client = clickhouse_connect.get_client(host = 'clickhouse-server',
                                    port = '8123', 
                                    user = 'konsin1988', 
                                    password = 'konsin1988konsin1988')
        except:
            exception_col.error('''You are not on **container** mode. Try:
                            
                            docker compose up -d --build in root directory''')
        else:
            st.session_state.client = client

    if st.session_state.client != None:
        st.write(st.session_state.client.headers)
elif not st.session_state.check_hide:
    col_box, col_check_hide = st.columns([0.7, 0.3])
    col_box.info('If you run project without containers, clickhouse database code will not work. Yon may only see/copy it to another project')
    col_check_hide.checkbox('Hide these messages', on_change=toggle_check_hide)
    



# create role admin
st.markdown('#### Create role admin IF NOT EXISTS')
query = r'''
    CREATE ROLE IF NOT EXISTS admin
'''
docker_role = ClickhouseCodeRunner(query, 'command', 'docker_role')
docker_role.run_code('verbose')
docker_role.show_code()

st.text('In "users/konsin1988-user.xml" we add role "admin" to have ALL GRANTS')

# grant to admin full access
st.markdown('#### Grant to admin full access')
query = r'''
    GRANT ALL ON *.* TO admin WITH GRANT OPTION
'''
grant_all = ClickhouseCodeRunner(query, 'command', 'grant_all')
grant_all.run_code(output = 'verbose')
grant_all.show_code()

st.text("And add role to xml user's file <role>admin</role>")

# # Checking roles
st.markdown("#### Checking the roles")
query = r'''SHOW ACCESS'''
check_roles = ClickhouseCodeRunner(query, 'query', 'check_roles')
check_roles.run_code(output = 'verbose')
check_roles.show_code()


# Create database german_cr and switch to german_cr
st.markdown("#### Create database german_cr and switch to german_cr")
query = r'CREATE DATABASE IF NOT EXISTS german_cr'
create_db = ClickhouseCodeRunner(query, 'command', 'create_db')
create_db.run_code(output = 'verbose')
create_db.show_code()

query = r'USE german_cr'
use_db = ClickhouseCodeRunner(query, 'command', 'use_db')
use_db.run_code(output = 'verbose')
use_db.show_code()

# Checking the database was created
st.markdown('#### Checking the database was created')
query = r'''
    SELECT name FROM system.databases
'''
check_db = ClickhouseCodeRunner(query, 'query', 'check_db')
check_db.run_code(output = 'verbose')
check_db.show_code()

# Create table german_credit with relevant data types
st.markdown('#### Create table german_credit with relevant data types')

query = r'''
    DROP TABLE IF EXISTS german_cr.german_credit;
'''
drop_table = ClickhouseCodeRunner(query, 'command', 'drop_table')
drop_table.run_code(output = 'verbose')
drop_table.show_code()

query = r'''
    CREATE TABLE IF NOT EXISTS german_cr.german_credit(
        `age` Nullable(Int64),
        `sex` Nullable(String),
        `job` Nullable(Int64),
        `housing` Nullable(String),
        `saving_accounts` Nullable(String),
        `checking_account` Nullable(String),
        `credit_amount` Nullable(Int64),
        `duration` Nullable(Int64),
        `purpose` Nullable(String),
        `default` Nullable(Int64),
        `contract_dt` DateTime('UTC'),
        `client_id` Nullable(Int64)
    ) ENGINE MergeTree 
            PARTITION BY toYYYYMM(contract_dt) 
            ORDER BY contract_dt 
            SETTINGS index_granularity = 256
'''
create_table = ClickhouseCodeRunner(query, 'command', 'create_table')
create_table.run_code(output = 'verbose')
create_table.show_code()

# Insert data from csv to table via bash
st.markdown('#### Insert data from csv to table via bash')

st.text('If you run code from local machine, you need to commands:')
col_code, col_text = st.columns([0.7, 0.3])
col_code.code('docker exec -it streamlit_loans bash', 'bash')
col_text.text(' , where "streamlit_loans" is name of the container')
st.text('And then in command-line of the container you need to run command:')
col_code, col_text = st.columns([0.7, 0.3])
col_code.code('cat german_credit.csv | python3 csv_to_click.py | clickhouse-client --host clickhouse-server --user konsin1988 --password konsin1988konsin1988 -q "INSERT INTO german_cr.german_credit FORMAT CSVWithNames"')
col_text.text(' , where we bind to clickhouse-client and insert data')
st.text('The script "csv_to_click.py" is needed to replace empty lines of a csv file with the escape sequence "\\N". This is done to ensure that clickhouse correctly handles missing values ​​and interprets them as None rather than an empty string.')

if (st.session_state.run_mode
    and st.session_state.client
    # and st.session_state.exists
    and st.session_state.client.query('EXISTS german_cr.german_credit').result_columns[0][0]
    and st.session_state.client.query(r'''
    SELECT COUNT(*) AS count
    FROM german_cr.german_credit
''').result_columns[0][0] == 0):
    if st.button('Insert data'):
        answer = subprocess.run('cat german_credit.csv | python3 csv_to_click.py | clickhouse-client --host clickhouse-server --user konsin1988 --password konsin1988konsin1988 -q "INSERT INTO german_cr.german_credit FORMAT CSVWithNames"', shell=True)
        st.code(answer)


st.info("From this project run only one command, cause code is running on streamlit_loans container, and we don't need to execute bash on it")

# Test data (head) and dtypes of table
st.markdown('#### Test data (total number of rows and head) of table')
query = r'''
    SELECT COUNT(*) AS `Total rows`
    FROM german_cr.german_credit
'''
total_count = ClickhouseCodeRunner(query, 'query', 'total_count')
total_count.run_code(output = 'verbose')
total_count.show_code()

query = r"""
    SELECT *
    FROM german_cr.german_credit
    LIMIT 5
"""
test_data = ClickhouseCodeRunner(query, 'query', 'test_data')
test_data.run_code(output = 'verbose')
test_data.show_code()

st.markdown('#### We can get list of columns from table:')
query = r'''
    SELECT column_name
    FROM information_schema.COLUMNS
    WHERE table_schema = 'german_cr' AND table_name = 'german_credit'
'''
list_of_cols = ClickhouseCodeRunner(query, 'query', 'list_of_cols')
list_of_cols.run_code(output = 'verbose')
list_of_cols.show_code()