import streamlit as st
import plotly.express as px

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode, plot_code

get_data()
toggle_run_mode()
load_checker()

st.header('Sum of all loan requests by gender')
st.subheader('As pivot table')

query = r'''
    SELECT 
        'Sum credit amount' AS Metrics,
        SUM(IF(sex = 'male', credit_amount, 0)) AS male,
        SUM(IF(sex = 'female', credit_amount, 0)) AS female
    FROM german_cr.german_credit
'''
sum_as_pivot = ClickhouseCodeRunner(query, 'query', 'sum_as_pivot')
sum_as_pivot.run_code(output = 'verbose')
sum_as_pivot.show_code()

st.subheader('As data to plotly')
query = r'''
    SELECT 
        sex, SUM(credit_amount) AS sum_amount
    FROM german_cr.german_credit
    GROUP BY sex
'''
sum_by_gender = ClickhouseCodeRunner(query, 'query', 'sum_by_gender')
sum_by_gender.run_code(output = 'verbose')
sum_by_gender.show_code()

sum_by_gender_pd = (
    st.session_state.gc
    .groupby(['sex'], observed = False)[['credit_amount']].sum().reset_index()
    .rename({'credit_amount': 'sum_amount'}, axis = 1)
)
sex_amount = st.session_state.sum_by_gender_result if st.session_state.run_mode else sum_by_gender_pd

if len(sex_amount) != 0:
    fig = px.bar(
        sex_amount,
        x = 'sex',
        y = 'sum_amount',
        height = 500,
        labels = {'sex': 'Gender', 'sum_amount': 'Amount of loans'},
        color = 'sex',
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    fig.update_layout(
        title = dict(
            text = 'Dependence of the sum of credits on gender',
            font = dict(
                size = 22,
                weight = 'bold'
            )
        ),
        xaxis = dict(
            tickmode = 'array',
            tickvals = sex_amount['sex'],
            ticktext = sex_amount['sex'],
            tickfont_size = 15,
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

    fig.update_legends(
        title_font = dict(
            size = 18,
            weight = 'bold'
        )
    )
    st.plotly_chart(fig)

printing_code = r"""
fig = px.bar(
    sex_amount,
    x = 'sex',
    y = 'sum_amount',
    height = 500,
    labels = {'sex': 'Gender', 'sum_amount': 'Amount of loans'},
    color = 'sex',
    color_discrete_sequence=px.colors.qualitative.Pastel1
)
fig.update_layout(
    title = dict(
        text = 'Dependence of the sum of credits on gender',
        font = dict(
            size = 22,
            weight = 'bold'
        )
    ),
    xaxis = dict(
        tickmode = 'array',
        tickvals = sex_amount['sex'],
        ticktext = sex_amount['sex'],
        tickfont_size = 15,
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

fig.update_legends(
    title_font = dict(
        size = 18,
        weight = 'bold'
    )
)
"""
plot_code(printing_code)