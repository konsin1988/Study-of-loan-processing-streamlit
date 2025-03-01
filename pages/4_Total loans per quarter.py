import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys      
sys.path.append('./streamlit_data/')
sys.path.append('./streamlit_funcs/')


from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import  get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode

get_data()
toggle_run_mode()

# if st.session_state.run_mode and  (not st.session_state.client or not st.session_state.exists or st.session_state.client.query(r'''
#     SELECT COUNT(*) AS count
#     FROM german_cr.german_credit
# ''').result_columns[0][0] == 0):
#     info_col, load_col = st.columns([0.7, 0.3])
#     info_col.info('Get client, create database and load data to the table from previous step or:')
#     if load_col.button('Loading data'):
#         with st.spinner('One second, please...'):
#             loading_previous_step()
#             time.sleep(5)
#             if st.session_state.client:
#                 st.success('Request complited')
load_checker()

st.header('Amount of loans issued for the quarter')
st.subheader('Сount the number of loans issued and refusals')

query = r'''
    SELECT * 
    FROM (
    SELECT 
        1 AS index,
        'Number' AS `Type of value`,
        CAST(SUM(IF(default = 1, 1, 0)), 'Int64') AS `Issued loans`,
        CAST(SUM(IF(default = 0, 1, 0)), 'Int64') AS `Refusal to issue a loan`
    FROM german_cr.german_credit
    
    UNION ALL
    
    SELECT 
        2,
        'Total amount',
        SUM(IF(default = 1, credit_amount, 0)) AS `Issued loans`,
        SUM(IF(default = 0, credit_amount, 0)) AS `Refusal to issue a loan`
    FROM german_cr.german_credit
    
    UNION ALL
    
    SELECT 
        3,
        'Percent, %',
        CAST(SUM(IF(default = 1, credit_amount, 0)) * 100 / SUM(credit_amount), 'Int64'),
        CAST(SUM(IF(default = 0, credit_amount, 0)) * 100 / SUM(credit_amount), 'Int64')
    FROM german_cr.german_credit
    )
    ORDER BY index
'''
nums_of_loans = ClickhouseCodeRunner(query, 'query', 'nums_of_loans')
nums_of_loans.run_code(output = 'verbose')
nums_of_loans.show_code()

# Amount of loans issued for the quarter
st.subheader('Amount of loans issued for the quarter')
query = r'''
    DROP VIEW IF EXISTS quarters
'''
drop_view_quart = ClickhouseCodeRunner(query, 'command', 'drop_view_quart')
drop_view_quart.run_code(output = 'verbose')
drop_view_quart.show_code()

st.text('Get all starts of quarters between first and last dates from german_credit')
query = r'''
    CREATE VIEW IF NOT EXISTS quarters AS 
    WITH get_first AS (
    SELECT MIN(toUnixTimestamp(contract_dt)) AS first_stamp
    FROM german_cr.german_credit
    ), get_last AS (
    SELECT MAX(toUnixTimestamp(contract_dt)) AS last_stamp
    FROM german_cr.german_credit
    ), get_quarters AS (
    SELECT DISTINCT toStartOfQuarter(toDateTime(arrayJoin(range(first_stamp, last_stamp, 60 * 60 * 24 * 90)))) AS quarters
    FROM get_first, get_last
    )
    SELECT 
        quarters AS quarter_start_date,
        toQuarter(quarters) AS quarter_number
    FROM get_quarters
'''
view_start_of_quarts = ClickhouseCodeRunner(query, 'command', 'view_start_of_quarts')
view_start_of_quarts.run_code(output = 'verbose')
view_start_of_quarts.show_code()

query = r'''
    SELECT * FROM quarters
'''
start_of_quarters = ClickhouseCodeRunner(query, 'query', 'start_of_quarters')
start_of_quarters.run_code(output = 'verbose')
start_of_quarters.show_code()

st.subheader('Amount of loans issued for the quarter')
query = r'''
    WITH get_main_data AS (
    SELECT
        toStartOfQuarter(contract_dt) AS quarter_start_date,
        SUM(credit_amount) AS total
    FROM german_cr.german_credit
    WHERE default = 1
    GROUP BY quarter_start_date
    ORDER BY quarter_start_date
    )
    SELECT 
        qa.quarter_start_date AS `Quarter start date`,
        qa.quarter_number AS `Quarter`,
        IF(total IS NULL, 0, total) AS `Total amount`
    FROM quarters qa
        LEFT JOIN get_main_data gmd ON gmd.quarter_start_date = qa.quarter_start_date
    ORDER BY `Quarter start date`
'''
loans_quarters = ClickhouseCodeRunner(query, 'query', 'loans_quarters')
loans_quarters.run_code(output = 'verbose')
loans_quarters.show_code()

# if not st.session_state.run_mode:
df = (
        st.session_state.gc
        .assign(quarter = lambda x: x['contract_dt'].dt.to_period('Q').astype('string'))
        .groupby(['quarter'], observed = False)[['credit_amount']].sum()
        .reset_index()
        .rename({'quarter': "Quarter start date", 'credit_amount': 'Total amount'}, axis = 1)
    )

if st.session_state.run_mode:
    total_quarters = st.session_state.loans_quarters_result
else:
    total_quarters = df

if len(total_quarters):
    fig = px.bar(
        total_quarters,
        x = 'Quarter start date',
        y = 'Total amount',
        title = 'Total number of loans issued per quarter',
        labels = {'Quarter start date': 'Quarter'},
        text = 'Total amount',
        height = 500
    )
    fig.update_traces(textfont_size=14, textangle=0, textposition="inside", cliponaxis=False)
    fig.update_layout(xaxis = dict(
        tickmode = 'array',
        tickvals = total_quarters['Quarter start date'],
        tickfont_size = 13,
        tickformat = '%B %Y'
    ), 
        yaxis = dict(
            tickfont_size = 13
        ),
        title_font = dict(size = 24, weight = 'bold'),
        margin=dict(l=70, r=30, t=60, b=20),
    )
    fig.add_trace(go.Scatter(
        x = total_quarters['Quarter start date'], 
        y = total_quarters['Total amount'], 
        name = 'Total amount <br>of loans issued',
        marker_color = '#812d91',
        line_width = 3,
        line_shape = 'spline'
    ))
    st.plotly_chart(fig)
    st.success("Based on the data and graph, we cannot make assumptions about the growth or decline of loans issued. Unfortunately, we don't have enough data to draw any conclusions in the long term.")


