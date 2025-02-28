import plotly.express as px
import streamlit as st
from streamlit_data.get_data import get_data

# data
get_data()
sum_per_month = st.session_state.sum_per_month

# get all months between min and max date from data
st.header('Total amount of credits (approved and rejected) per month')
st.subheader('Get all months from period')
st.code(r'''
    months = (
        pd
            .period_range(start = gc['contract_dt'].dt.to_period('M').min(), 
                        end = gc['contract_dt'].dt.to_period('M').max())
            .to_frame(name = 'month')
            .reset_index(drop = True)
        )
''')
st.write(st.session_state.months.T)

st.subheader('Get sum per month from data')
st.code('''
    sum_per_month = (
        gc
            .assign(month = lambda x: x['contract_dt'].dt.to_period('M'))
            .groupby('month')
            [['credit_amount']].sum()
        )''')

st.subheader('get sum per month from all months between min and max date')
st.code(r'''
    sum_per_month = (
        months
            .merge(sum_per_month, on='month', how='left')
            .assign(month = lambda x: x['month'].astype('string'))
        )
''')
st.write(sum_per_month.set_index('month').rename({'credit_amount': 'Total per month'}, axis = 1).T)

fig = px.line(sum_per_month, 
    x = 'month', 
    y = 'credit_amount', 
    markers = True,
    line_shape = 'spline',
    labels = {'month': 'Month', 'credit_amount': 'Total amount of all loans'},
    width = 900
)
fig.update_layout(
    title = dict(
        text = 'Change in total number of loans',
        font = dict(
            size = 20,
            weight = 'bold',
            color = '#231f20'
        )
    ),
    xaxis = dict(
        tickmode = 'array',
        tickvals = sum_per_month['month'],
        tickfont_size = 14,
        tickformat = '%b, %Y',
        tickfont_color = '#231f20'
    ),
    yaxis = dict(
        tickfont_color = '#231f20',
        tickfont_size = 14
    ),
    paper_bgcolor="LightSteelBlue",
    margin=dict(l=70, r=30, t=60, b=20)
)

fig.update_xaxes(
    title = dict(
        font = dict(
            color = '#231f20',
            size = 16
        )
    )
)
fig.update_yaxes(
    title = dict(
        font = dict(
            color = '#231f20',
            size = 16
        )
    )
)
fig.update_xaxes(tickangle = 60)
st.plotly_chart(fig)

if st.checkbox('Show code'):
    st.code(r'''
import plotly.express as px

fig = px.line(sum_per_month, 
            x = 'month', 
            y = 'credit_amount', 
            markers = True,
            line_shape = 'spline',
            labels = {'month': 'Month', 'credit_amount': 'Total amount of all loans'},
            width = 900
             )
fig.update_layout(
    title = dict(
        text = 'Change in total number of loans',
        font = dict(
            size = 20,
            weight = 'bold',
            color = '#231f20'
        )
    ),
    xaxis = dict(
        tickmode = 'array',
        tickvals = sum_per_month['month'],
        tickfont_size = 14,
        tickformat = '%b, %Y',
        tickfont_color = '#231f20'
    ),
    yaxis = dict(
        tickfont_color = '#231f20',
        tickfont_size = 14
    ),
    paper_bgcolor="LightSteelBlue",
    margin=dict(l=70, r=30, t=60, b=20)
)

fig.update_xaxes(
    title = dict(
        font = dict(
            color = '#231f20',
            size = 16
        )
    )
)
fig.update_yaxes(
    title = dict(
        font = dict(
            color = '#231f20',
            size = 16
        )
    )
)
fig.update_xaxes(tickangle = 60)
fig.show()
''', "python")


st.success("> Based on available data, it can be assumed that people are more active in taking out loans in the pre-New Year period and in the period before the start of the summer holiday season. But we do not have enough data to confirm these hypotheses.")

