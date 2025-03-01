import pandas as pd
import streamlit as st
import clickhouse_connect
import subprocess
import sys
import time
sys.path.append('./streamlit_funcs/')

from streamlit_funcs.helpers import loading_button_clicked



def get_data():
    st.set_page_config(layout="wide", page_title='Loan processing', page_icon="🏹")

    if 'run_mode' not in st.session_state:
        st.session_state.run_mode = True

    if 'loading_button_clicked' not in st.session_state:
        st.session_state.loading_button_clicked = False

    if 'client' not in st.session_state:
        st.session_state.client = None

    if not 'exists' in st.session_state:
        st.session_state.exists = None
        if not st.session_state.client == None:
            st.session_state.exists = st.session_state.client.query('EXISTS german_cr.german_credit').result_columns[0][0]

    if 'check_hide' not in st.session_state:
        st.session_state.check_hide = False
    if st.session_state.client:
        st.session_state.exists = (
            st.session_state
            .client.query('EXISTS german_cr.german_credit')
            .result_columns[0][0]
        )

    if 'gc' not in st.session_state:
        # get main df
        gc = pd.read_csv('german_credit.csv', 
                 dtype={
                    'sex': 'category',
                    'job': 'category', 
                    'housing': 'category',
                    'purpose': 'category',
                    'default': 'category', 
                    'client_id': 'category', 
                 },
                 parse_dates=['contract_dt']
                 ).sort_values('contract_dt').reset_index(drop=True)
        st.session_state.gc = gc

        # get all months
        months = (
            pd
            .period_range(start = gc['contract_dt'].dt.to_period('M').min(), 
                        end = gc['contract_dt'].dt.to_period('M').max())
            .to_frame(name = 'month')
            .reset_index(drop = True)
            )
        st.session_state.months = months

        # get sum per month from data
        sum_per_month = (
            gc
            .assign(month = lambda x: x['contract_dt'].dt.to_period('M'))
            .groupby('month')
            [['credit_amount']].sum()
        )

        # get sum per month from all months between min and max date
        sum_per_month = (
            months
            .merge(sum_per_month, on='month', how='left')
            .assign(month = lambda x: x['month'].astype('string'))
        )
        st.session_state.sum_per_month = sum_per_month

query_admin_creation = r'CREATE ROLE IF NOT EXISTS admin'
query_grants = r'''GRANT ALL ON *.* TO admin WITH GRANT OPTION'''
query_db_creation = r'CREATE DATABASE IF NOT EXISTS german_cr'
query_drop_table = r'DROP TABLE IF EXISTS german_cr.german_credit'
query_table_creation = r'''
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

def loading_previous_step():
    try:
        if not st.session_state.client:
            st.session_state.client = clickhouse_connect.get_client(host = 'clickhouse-server', 
                                            port = '8123', 
                                            user = 'konsin1988', 
                                            password = 'konsin1988konsin1988')
        st.session_state.client.command(query_admin_creation)
        st.session_state.client.command(query_grants)
        st.session_state.client.command(query_db_creation)
        st.session_state.client.command(query_drop_table)
        st.session_state.client.command(query_table_creation)
        subprocess.run('cat german_credit.csv | python3 csv_to_click.py | clickhouse-client --host clickhouse-server --user konsin1988 --password konsin1988konsin1988 -q "INSERT INTO german_cr.german_credit FORMAT CSVWithNames"', shell=True)
    except:
        error_col, code_col = st.columns([0.5, 0.5])
        error_col.error('Docker connection failed. Try:')
        code_col.code('docker compose up -d --build', 'bash')
        return False
    return True

def load_checker():
    if st.session_state.run_mode and (not st.session_state.client or not st.session_state.exists or st.session_state.client.query(r'''
        SELECT COUNT(*) AS count
        FROM german_cr.german_credit
    ''').result_columns[0][0] == 0):
        info_col, load_col = st.columns([0.7, 0.3])
        info_col.info('Get client, create database and load data to the table from previous step or:')
        load_col.button('Loading data', on_click=loading_button_clicked)
        if st.session_state.loading_button_clicked:
            with st.spinner('One second, please...'):
                loading_previous_step()
                time.sleep(4)
                if st.session_state.client:
                    st.success('Request complited')

if __name__ == "__main__":
    get_data, loading_previous_step, load_checker