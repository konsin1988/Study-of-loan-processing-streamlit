import streamlit as st
import plotly.express as px

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode, plot_code

get_data()
toggle_run_mode()
load_checker()

st.header('Sum of all loan requests per month by gender ')

st.subheader('Create view "months"')
query = r'''
    DROP VIEW IF EXISTS months
'''
drop_view_months = ClickhouseCodeRunner(query, 'command', 'drop_view_months')
drop_view_months.run_code(output = 'verbose')
drop_view_months.show_code()

query = r'''
    CREATE VIEW IF NOT EXISTS months AS 
    WITH get_first AS (
    SELECT MIN(toUnixTimestamp(contract_dt)) AS first_stamp
    FROM german_cr.german_credit
    ), get_last AS (
    SELECT MAX(toUnixTimestamp(contract_dt)) AS last_stamp
    FROM german_cr.german_credit
    ), get_months AS (
    SELECT DISTINCT toStartOfMonth(toDateTime(arrayJoin(range(first_stamp, last_stamp, 60 * 60 * 24 * 28)))) AS months
    FROM get_first, get_last
    )
    SELECT 
        months AS month,
        toMonth(months) AS month_number
    FROM get_months
'''
create_view_months = ClickhouseCodeRunner(query, 'command', 'create_view_months')
create_view_months.run_code(output = 'verbose')
create_view_months.show_code()

query = r'''
    SELECT * FROM months
'''
get_from_view_months = ClickhouseCodeRunner(query, 'query', 'get_from_view_months')
get_from_view_months.run_code(output = 'verbose')
get_from_view_months.show_code()

# loans per month by gender
st.subheader('Get total loan per month by gender')
query = r'''
    WITH get_sex AS (
        SELECT 'male' AS sex
        UNION ALL
        SELECT 'female' AS sex    
    )
    SELECT 
        mn.month AS month,
        gc.sex AS sex,
        SUM(gc.credit_amount) AS sum_amount_per_month
    FROM months mn
        CROSS JOIN get_sex gs 
        LEFT JOIN german_cr.german_credit gc ON mn.month = toStartOfMonth(gc.contract_dt) AND gc.sex = gc.sex
    GROUP BY mn.month, gc.sex
    ORDER BY month, sex
'''
get_loan_month_sex = ClickhouseCodeRunner(query, 'query', 'get_loan_month_sex')
get_loan_month_sex.run_code(output = 'verbose')
get_loan_month_sex.show_code()

st.subheader('Plot loans per month by gender in Plotly')

loans_per_month_pd = (
    st.session_state.gc
    .assign(month = lambda x: x['contract_dt'].dt.to_period('M').astype('string'))
    .groupby(['month', 'sex'], observed = False)[['credit_amount']].sum()
    .reset_index()
    .rename({'credit_amount': 'sum_amount_per_month'}, axis = 1)
)

loans_per_month = st.session_state.get_loan_month_sex_result if st.session_state.run_mode else loans_per_month_pd

if len(loans_per_month) > 0:
    fig = px.bar(
        loans_per_month, 
        x = 'month',
        y = 'sum_amount_per_month',
        color = 'sex',
        barmode = 'group',
        labels = {'month': 'Month', 'sum_amount_per_month': 'Loans total'},
        color_discrete_sequence=px.colors.qualitative.Safe,
        height = 500
    )
    fig.update_legends(
        title = dict(text = 'Sex',
                    font_size = 14,
                    font_weight = 'bold'
                    )
    )
    fig.update_layout(
        title = dict(
            text = 'Sum loans amount per month by gender',
            font = dict(
                size = 20,
                weight = 'bold'
            )
        ),
        xaxis = dict(
            title_font = dict(
                size = 16,
                weight = 'bold'
            )
        ),
        yaxis = dict(
            title_font = dict(
                size = 16,
                weight = 'bold'
            )
        )
    )
    st.plotly_chart(fig)

st.success('As can be seen from the graph, the percentage ratio "male-female" almost does not change over time.')

printing_code = r"""
fig = px.bar(
    loans_per_month, 
    x = 'month',
    y = 'Sum amount per month',
    color = 'sex',
    barmode = 'group',
    labels = {'month': 'Month'},
    color_discrete_sequence=px.colors.qualitative.Safe,
    height = 500
)
fig.update_legends(
    title = dict(text = 'Sex',
                font_size = 14,
                font_weight = 'bold'
                )
)
fig.update_layout(
    title = dict(
        text = 'Sum loans amount per month by gender',
        font = dict(
            size = 20,
            weight = 'bold'
        )
    ),
    xaxis = dict(
        title_font = dict(
            size = 16,
            weight = 'bold'
        )
    ),
    yaxis = dict(
        title_font = dict(
            size = 16,
            weight = 'bold'
        )
    )
)
"""
plot_code(printing_code)