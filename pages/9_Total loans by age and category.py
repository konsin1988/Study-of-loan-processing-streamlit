import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode, plot_code

get_data()
toggle_run_mode()
load_checker()

st.header('The amount of loans requested depending on the age category')
st.subheader('Distribution of the age variable')

fig = px.histogram(
    st.session_state.gc,
    x = 'age',
    title = 'Distribution of age variable',
    height = 500
)
st.plotly_chart(fig)
st.text("Let's cut our data by age category (young, middle age, elderly)")
st.code(r"""
age_cat = (
    df
    .assign(Age_category = lambda x: pd.cut(x['age'], bins = [0, 28, 38, 100], labels = ['young', 'middle age', 'elderly']))
)[['Age_category']].value_counts(sort=False).to_frame()
""", 'python')

age_cat = (
    st.session_state.gc
    .assign(Age_category = lambda x: pd.cut(x['age'], bins = [0, 28, 38, 100], labels = ['young', 'middle age', 'elderly']))
)[['Age_category']].value_counts(sort=False).to_frame()
st.dataframe(age_cat)

fig = px.bar(
    age_cat.reset_index(),
    x = 'Age_category',
    y = 'count',
    color = 'Age_category',
    color_discrete_sequence = px.colors.qualitative.Safe, 
    labels = dict(
        Age_category = 'Age category',
        count = 'Number of observations'
    ),
    height = 500
)
fig.update_layout(
    title = dict(
        text = 'Distribution of age variable',
        font = dict(
            size = 18,
            weight = 'bold'
        )
    ),
    xaxis = dict(
        title = dict(
            text = 'Age category',
            font_weight = 'bold'
        )
    ),
    yaxis = dict(
        title = dict(
            text = 'Number of observations'
        )
    )
)
st.plotly_chart(fig)

if st.toggle('Show code', value=False):
    st.code(r"""
fig = px.bar(
    age_cat.reset_index(),
    x = 'Age_category',
    y = 'count',
    color = 'Age_category',
    color_discrete_sequence = px.colors.qualitative.Safe, 
    labels = dict(
        Age_category = 'Age category',
        count = 'Number of observations'
    ),
    height = 500
)
fig.update_layout(
    title = dict(
        text = 'Distribution of age variable',
        font = dict(
            size = 18,
            weight = 'bold'
        )
    ),
    xaxis = dict(
        title = dict(
            text = 'Age category',
            font_weight = 'bold'
        )
    ),
    yaxis = dict(
        title = dict(
            text = 'Number of observations'
        )
    )
)
""", 'python')
    
st.subheader('The same operation in SQL')
query = r'''
    WITH get_category AS (
    SELECT 
        age, 
        NTILE(3) OVER w AS Age_category
    FROM german_cr.german_credit
    WINDOW w AS (
        ORDER BY age
    ))
    SELECT 
        CASE 
            WHEN Age_category = 1 THEN 'young'
            WHEN Age_category = 2 THEN 'middle age'
            ELSE 'elderly'
        END AS Age_category,
        COUNT(*) AS `Number of observations`
    FROM get_category
    GROUP BY Age_category
'''
get_count_age_cat = ClickhouseCodeRunner(query, 'query', 'get_count_age_cat')
get_count_age_cat.run_code(output = 'verbose')
get_count_age_cat.show_code()

st.subheader("Split data by age category and purposes")
query = r'''
    WITH get_category AS (
    SELECT 
        purpose,
        NTILE(3) OVER w AS age_category,
        credit_amount
    FROM german_cr.german_credit
    WINDOW w AS (
        ORDER BY age
    ))
    SELECT
        purpose,
        CASE 
            WHEN age_category = 1 THEN 'young'
            WHEN age_category = 2 THEN 'middle age'
            ELSE 'elderly'
        END AS age_category,
        SUM(credit_amount) AS sum_amount
    FROM get_category
    GROUP BY purpose, age_category 
    ORDER BY purpose, age_category
'''
split_by_age_purpose = ClickhouseCodeRunner(query, 'query', 'split_by_age_purpose')
split_by_age_purpose.run_code(output = 'verbose')
split_by_age_purpose.show_code()

st.subheader("The same splitting result in wide table format")
query = r'''
    WITH get_category AS (
    SELECT 
        purpose,
        NTILE(3) OVER w AS Age_category,
        credit_amount
    FROM german_cr.german_credit
    WINDOW w AS (
        ORDER BY age
    ))
    SELECT
        purpose,
        SUM(CASE WHEN Age_category = 1 THEN credit_amount ELSE 0 END) AS young,
        SUM(CASE WHEN Age_category = 2 THEN credit_amount ELSE 0 END) AS middle_age,
        SUM(CASE WHEN Age_category = 3 THEN credit_amount ELSE 0 END) AS elderly
    FROM get_category
    GROUP BY purpose
    ORDER BY purpose
'''
age_purpose_wide = ClickhouseCodeRunner(query, 'query', 'age_purpose_wide')
age_purpose_wide.run_code(output = 'verbose')
age_purpose_wide.show_code()

sum_by_age_pd = (
    st.session_state.gc
    .assign(age_category = lambda x: pd.cut(x['age'], bins = [0, 28, 38, 100], labels = ['young', 'middle age', 'elderly']))
    .groupby(['purpose', 'age_category'], observed = False)[['credit_amount']].sum()
    .reset_index()
    .rename({'credit_amount': 'sum_amount'}, axis = 1)
)

sum_by_age = (st.session_state.split_by_age_purpose_result 
                if st.session_state.run_mode 
                else sum_by_age_pd)

if len(sum_by_age) > 0:
    fig = px.pie(
        sum_by_age,
        values = 'sum_amount',
        facet_col = 'age_category',
        names = 'purpose',
        labels = {
            'age_category': 'Age category',
            'purpose': 'Purpose of loan',
            'sum_amount': 'Sum amount of loans by groups'
        },
        category_orders = {
            'age_category': ['young', 'middle age', 'elderly']
        }
        # height = 600
    )
    fig.for_each_annotation(
        lambda x: x.update(
            text = x.text.split("=")[-1], 
            font = dict(size = 15, 
                        weight = 'bold', 
                        textcase = 'upper')
        )
    )
    fig.for_each_trace(
        lambda x: x.update(
            textposition='inside'
        )
    )
    fig.update_legends(
        title = dict(
            text = 'Purposes',
            font_weight = 'bold'
        )
    )
    st.plotly_chart(fig)
    st.success('Based on the plot above, we can conclude that as people age, they take out more loans for a car and less for a TV/radio')

printing_code = r"""
fig = px.pie(
    sum_by_age,
    values = 'sum_amount',
    facet_col = 'age_category',
    names = 'purpose',
    labels = {
        'age_category': 'Age category',
        'purpose': 'Purpose of loan',
        'sum_amount': 'Sum amount of loans by groups'
    },
    category_orders = {
        'age_category': ['young', 'middle age', 'elderly']
    }
)
fig.for_each_annotation(
    lambda x: x.update(
        text = x.text.split("=")[-1], 
        font = dict(size = 15, 
                    weight = 'bold', 
                    textcase = 'upper')
    )
)
fig.for_each_trace(
    lambda x: x.update(
        textposition='inside'
    )
)
fig.update_legends(
    title = dict(
        text = 'Purposes',
        font_weight = 'bold'
        )
    )
"""
plot_code(printing_code)