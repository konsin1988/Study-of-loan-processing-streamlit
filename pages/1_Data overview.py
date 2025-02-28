import streamlit as st
import pandas as pd
import sys
import io

sys.path.append('./streamlit_data/')
from get_data import get_data

import plotly.express as px

get_data()

gc = pd.read_csv('german_credit.csv', 
                 dtype={
                    'sex': 'category',
                    'job': 'category', 
                    'housing': 'category',
                    'purpose': 'category',
                    'default': 'category', 
                    'client_id': 'category',   
                    },
                 parse_dates=['contract_dt'],
                 ).sort_values('contract_dt').reset_index(drop=True)

st.header('Data overview')
st.subheader('General information about the data')

if st.checkbox('All data'):
    st.write(gc)
else:
    st.write(gc.head(3))

st.subheader('Dataframe info')  
buffer = io.StringIO()
gc.info(buf=buffer)
lines = buffer.getvalue().splitlines()
info_df = (pd.DataFrame([x.split() for x in lines[5:-2]], columns=lines[3].split())
       .drop('Count',axis=1)
       .rename(columns={'Non-Null':'Non-Null Count', '#': '№'})
       .set_index('№')
       )
st.write(info_df)

st.subheader('NA counts')
st.write(pd.DataFrame(gc.isna().sum(), columns=['NA counts']))
st.subheader('Describe numeric variables')
st.dataframe(gc.describe(include='number'))
st.subheader('Describe categorical variables')
st.dataframe(gc.describe(include=['category', 'object']))

st.subheader('Correlation between numeric variables')

fig = px.imshow(
    gc.corr(numeric_only=True),
    range_color=[-1, 1],
    x = ['Age', 'Amount of loans', 'Duration'],
    y = ['Age', 'Amount of loans', 'Duration'],
    text_auto=True
)
fig.update_layout(
    title = dict(
        text = 'Correlation between numeric variables',
        font = dict(
            size = 20,
            weight = 'bold'
        )
    )   
)
fig.update_traces(
    texttemplate='%{z:.2f}'
)
st.plotly_chart(fig)

st.subheader('Conclusions')
st.success('We have a fairly strong correlation between the length of time people take out loans and the size of the loan. Which is quite logical. For us, this suggests that it is undesirable to use both of these variables to build a model.')