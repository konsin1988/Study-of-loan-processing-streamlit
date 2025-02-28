import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data

get_data()

st.header('Total loan amount depending on the age category, purpose and gender')

sum_by_sex_age_purpose = (
    st.session_state.gc
    .assign(age_cat = lambda x: pd.cut(x['age'], bins = [0, 28, 38, 100], labels = ['young', 'middle age', 'elderly']))
    .groupby(['sex', 'purpose', 'age_cat'], observed=False)['credit_amount'].sum().to_frame()
).reset_index()
st.dataframe(pd.pivot_table(sum_by_sex_age_purpose, columns = ['sex', 'age_cat'], index = ['purpose']))

if st.toggle('Show code', value=False, key = 'calculation'):
    st.code(r"""
    sum_by_sex_age_purpose = (
        st.session_state.gc
        .assign(age_cat = lambda x: pd.cut(x['age'], 
                                        bins = [0, 28, 38, 100], 
                                        labels = ['young', 'middle age', 'elderly']))
        .groupby(['sex', 'purpose', 'age_cat'], observed=False)['credit_amount'].sum().to_frame()
    ).reset_index()
    st.dataframe(pd.pivot_table(sum_by_sex_age_purpose, 
                columns = ['sex', 'age_cat'], index = ['purpose']))
    """, 'python')

fig = px.pie(
    sum_by_sex_age_purpose,
    values = 'credit_amount',
    facet_col = 'age_cat',
    facet_row = 'sex',
    names = 'purpose',
    labels = {
        'sex': 'Sex',
        'age_cat': 'Age category',
        'purpose': 'Purpose of the loan',
        'credit_amount': 'Sum of amounts by groups'
    },
    color_discrete_sequence = px.colors.qualitative.Pastel1, 
    height = 800,
)

fig.update_legends(
    title = dict(
        text = 'Purpose of the loan:',
        font = dict(
            size = 14,
            weight = 'bold'
        )
    ),
    yanchor = "bottom",
    y = -0.1,
    xanchor = "left",
    x = -0.1, 
    orientation = 'h'
)

fig.update_layout(
    title = dict(
        text = 'The amount of loans requested depending on the age category, purpose and sex',
        font = dict(
            size = 22,
            weight = 'bold'
        )
    )
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
st.plotly_chart(fig)
st.success("Judging by the plots, we can conclude that young girls take much more credits on furneture than middle-aged and older girls. Despite the fact that this trend is not observed among men. It is also interesting that it is middle-aged girls who take out car loans from women more often, while it is mainly the elderly who take out car loans from men.")

if st.toggle('Show code', value=False, key='plot'):
    st.code(r"""
fig = px.pie(
    sum_by_sex_age_purpose,
    values = 'credit_amount',
    facet_col = 'age_cat',
    facet_row = 'sex',
    names = 'purpose',
    labels = {
        'sex': 'Sex',
        'age_cat': 'Age category',
        'purpose': 'Purpose of the loan',
        'credit_amount': 'Sum of amounts by groups'
    },
    color_discrete_sequence = px.colors.qualitative.Pastel1, 
    height = 800,
)

fig.update_legends(
    title = dict(
        text = 'Purpose of the loan:',
        font = dict(
            size = 14,
            weight = 'bold'
        )
    ),
    yanchor = "bottom",
    y = -0.1,
    xanchor = "left",
    x = -0.1, 
    orientation = 'h'
)

fig.update_layout(
    title = dict(
        text = 'The amount of loans requested depending on the age category, purpose and sex',
        font = dict(
            size = 22,
            weight = 'bold'
        )
    )
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
""")