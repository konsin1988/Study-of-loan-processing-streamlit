import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode, plot_code

get_data()
toggle_run_mode()
load_checker()

st.header('Percentage of loans issued from the total number for men and women for different loan purposes')

fig = px.bar(
    st.session_state.gc['default'].value_counts().to_frame().reset_index().rename({'default': 'solution'}, axis = 1),
    x = 'solution',
    y = 'count',
    height = 500
)
fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [0, 1],
        ticktext = ['rejected', 'approved'],
        tickfont_weight = 'bold',
        tickfont_size = 14
    ),
    title = dict(
        text = 'Count of approved and rejected loans',
        font = dict(
            size = 20,
            weight = 'bold'
        )
    )
)
st.plotly_chart(fig)

printing_code = r"""
fig = px.bar(
    df['default'].value_counts().to_frame().reset_index().rename({'default': 'solution'}, axis = 1),
    x = 'solution',
    y = 'count',
    height = 500
)
fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [0, 1],
        ticktext = ['rejected', 'approved'],
        tickfont_weight = 'bold',
        tickfont_size = 14
    ),
    title = dict(
        text = 'Count of approved and rejected loans',
        font = dict(
            size = 20,
            weight = 'bold'
        )
    )
)
"""
if st.toggle('Show code', value=False):
    st.code(printing_code, 'python')

query = r'''
    SELECT 
        sex AS Gender,
        purpose AS Purpose,
        ROUND(SUM(default) * 100.0/COUNT(*), 2) as `Percent of approved loans, %` 
    FROM german_cr.german_credit
    GROUP BY sex, purpose
    ORDER BY sex, purpose
'''
percent_approved = ClickhouseCodeRunner(query, 'query', 'percent_approved')
percent_approved.run_code(output = 'verbose')
percent_approved.show_code()

query = r'''
    SELECT 
        sex AS Gender,
        purpose AS Purpose,
        CASE WHEN default = 1 THEN 'approved' ELSE 'rejected' END AS `Is approved`,
        COUNT(*) AS `Number of observations`
    FROM german_cr.german_credit
    GROUP BY sex, purpose, default
    ORDER BY sex, purpose
'''
loan_approved_rejected = ClickhouseCodeRunner(query, 'query', 'loan_approved_rejected')
loan_approved_rejected.run_code(output = 'verbose')
loan_approved_rejected.show_code()

loan_approved_pd = (
    st.session_state.gc
    .assign(**{'Is approved': lambda x: x['default'].apply(lambda x: 'approved' if x == '1' else 'rejected')})
    .groupby(['sex', 'purpose', 'Is approved'], observed = False)[['credit_amount']].count()
    .reset_index()
    .rename({'credit_amount': 'Number of observations', 
             'purpose': 'Purpose',
             'sex': 'Gender'}, axis = 1)
)

loan_approved = (st.session_state.loan_approved_rejected_result 
                    if st.session_state.run_mode
                    else loan_approved_pd)

if len(loan_approved) > 0:
    fig = px.pie(
        loan_approved,
        values = 'Number of observations',
        names = 'Is approved',
        facet_row = 'Purpose',
        facet_col = 'Gender'
    )

    fig.update_legends(
        title = dict(
            text = 'Loan approved <br>or rejected',
            font = dict(
                size = 16,
                weight = 'bold'
            )
        )
    )

    fig.update_layout(
        title = dict(
            text = r'''The ratio of the number of approved loans to the number<br>
            of rejected loans for men and women, depending on the purpose of the loan<br>''',
            font_size = 20,
            font_weight = 'bold'
        ),
        # autosize = False,
        margin=dict(pad = 100, t = 150, l = 20, r = 20),
        height = 3000,
    )

    fig.for_each_annotation(
        lambda x: x.update(
            text = x.text.split('=')[-1],
            font = dict(
                size = 14,
                weight = 'bold'
            ),
            textangle = 0
        )
    )
    st.plotly_chart(fig)

printing_code_pie = r"""
fig = px.pie(
    loan_approved,
    values = 'Number of observations',
    names = 'Is approved',
    facet_row = 'Purpose',
    facet_col = 'Gender'
)

fig.update_legends(
    title = dict(
        text = 'Loan approved <br>or rejected',
        font = dict(
            size = 16,
            weight = 'bold'
        )
    )
)

fig.update_layout(
    title = dict(
        text = r'''The ratio of the number of approved loans to the number<br>
        of rejected loans for men and women, depending on the purpose of the loan<br>''',
        font_size = 20,
        font_weight = 'bold'
    ),
    margin=dict(pad = 100, t = 150, l = 20, r = 20),
    height = 3000,
)

fig.for_each_annotation(
    lambda x: x.update(
        text = x.text.split('=')[-1],
        font = dict(
            size = 14,
            weight = 'bold'
        ),
        textangle = 0
    )
)
"""
plot_code(printing_code_pie)