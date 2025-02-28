import streamlit as st
import plotly.express as px

from streamlit_funcs.run_clickhouse import ClickhouseCodeRunner
from streamlit_data.get_data import get_data, load_checker
from streamlit_funcs.helpers import toggle_run_mode, plot_code

get_data()
toggle_run_mode()
load_checker()

st.header('Dependence of the amount of loans by category')


query = r'''
    SELECT
        toStartOfMonth(gc.contract_dt) AS Month,
        gc.purpose AS Purpose,
        SUM(gc.credit_amount) AS sum_amount
    FROM german_cr.german_credit gc
    GROUP BY Month, Purpose
    ORDER BY Month
'''
get_sum_by_category = ClickhouseCodeRunner(query, 'query', 'get_sum_by_category')
get_sum_by_category.run_code(output = 'verbose')
get_sum_by_category.show_code()

st.subheader('Order the xaxes by value of sum_amount (in first month avaliable)')

st.code(r'''
get_sum_by_category_pd = (
    st.session_state.gc
        .assign(Month = lambda x: x['contract_dt'].dt.to_period('M').astype('string'))
        .groupby(['Month', 'purpose'])[['credit_amount']].sum()
        .reset_index()
        .rename({'credit_amount': 'sum_amount', 'purpose': 'Purpose'}, axis = 1)
)

cat_order = (
    get_sum_by_category_pd
        .query('Month == "2007-05" ')
        .sort_values(['sum_amount'], ascending = False)['Purpose'].to_list()
)
''', 'python')

get_sum_by_category_pd = (
    st.session_state.gc
        .assign(Month = lambda x: x['contract_dt'].dt.to_period('M').astype('string'))
        .groupby(['Month', 'purpose'])[['credit_amount']].sum()
        .reset_index()
        .rename({'credit_amount': 'sum_amount', 'purpose': 'Purpose'}, axis = 1)
)

cat_order = (
    get_sum_by_category_pd
        .query('Month == "2007-05" ')
        .sort_values(['sum_amount'], ascending = False)['Purpose'].to_list()
)

amount_purpose = (st.session_state.get_sum_by_category_result if st.session_state.run_mode else get_sum_by_category_pd)

if len(amount_purpose) > 0:
    fig = px.bar(
        amount_purpose.sort_values('Month'),
        x = 'Month',
        y = 'sum_amount',
        facet_col = 'Purpose',
        facet_col_wrap = 2,
        labels = {'sum_amount': 'Sum loans'},
        color = 'Month',
        category_orders = {'Purpose': cat_order},
        color_discrete_sequence=px.colors.qualitative.Vivid,
        height = 1500
    )
    fig.for_each_annotation(lambda x: x.update(text = x.text.split("=")[-1], font = dict(size = 15, weight = 'bold', textcase = 'upper')))
    fig.update_xaxes(tickangle = 90, showgrid=True, ticks="outside")
    fig.for_each_xaxis(lambda x: x.update(tickmode = 'array',
                                tickvals = amount_purpose['Month'],
                                tickfont_size = 10,
                                tickformat = '%b, %Y'))
    fig.for_each_xaxis(lambda xaxis: xaxis.update(showticklabels=True))
    st.plotly_chart(fig)
    st.success("Unfortunately, the graphs cannot make any assumptions about the interdependence of variables")
    
printing_code = r"""
fig = px.bar(
    amount_purpose.sort_values('Month'),
    x = 'Month',
    y = 'sum_amount',
    facet_col = 'Purpose',
    facet_col_wrap = 2,
    labels = {'sum_amount': 'Sum loans'},
    color = 'Month',
    category_orders = {'Purpose': cat_order},
    color_discrete_sequence=px.colors.qualitative.Vivid,
    height = 1500
)
fig.for_each_annotation(lambda x: x.update(text = x.text.split("=")[-1], font = dict(size = 15, weight = 'bold', textcase = 'upper')))
fig.update_xaxes(tickangle = 90, showgrid=True, ticks="outside")
fig.for_each_xaxis(lambda x: x.update(tickmode = 'array',
                                tickvals = amount_purpose['Month'],
                                tickfont_size = 10,
                                tickformat = '%b, %Y'))
fig.for_each_xaxis(lambda xaxis: xaxis.update(showticklabels=True))
"""
plot_code(printing_code)