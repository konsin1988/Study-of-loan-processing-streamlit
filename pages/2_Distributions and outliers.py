import pandas as pd
from pandas.api.types import is_numeric_dtype
from plotly.subplots import make_subplots
import streamlit as st
import io

from streamlit_data.get_data import get_data

get_data()


def get_df_var_name(name):
    return name_dict[name]

name_dict = {"Age": ['age', 
                     'Age of clients',
                     'The distribution is close to normal, with a shift to the left. There are outliers, but their values ​​are not anomalous.'], 
                "Sex": ['sex', 
                        'Gender',
                        'The distribution by gender is heterogeneous; there is a rather strong bias towards the value “male”.'], 
                "Housing": ['housing', 
                        'Get own house?',
                        'Based on the value of the “housing” variable, we can say that loans are taken out mostly by those who own housing. Strong bias towards the value "housing".'], 
                "Credit amount": ['credit_amount', 
                        'Amount of loan',
                        'The distribution of the "credit_amount" variable is similar to normal, but has a rather strong shift towards the origin. There are outliers, but they are within the limits of logically acceptable values, without anomalous values.'], 
                "Duration of loan": ['duration', 
                        'Duration of loan',
                        'The value of the "duration" variable is difficult to classify as normal, although there is a tendency. There are outliers, 3 of them can be classified as anomalous (72, 60 and 54). Based on the amount of data, we can afford to exclude lines with these values.'], 
                "Purpose": ['purpose', 
                        'Purpose',
                        'In the distribution of the "purpose" variable there are 3 explicit favorites: "car", "radio/tv", "furniture/equipment". We have a strong imbalance of classes in terms of the number of applications. Again, for the full picture, we will look further at the distribution by loan amount.'],
                "Issued or rejected": ['default', 
                        'Issued or rejected',
                        'Based on the distribution of the target variable (loan issued or application rejected), we can say that only 30% of the total number of applications are issued. We will look at the distribution of the loan amount later.'],
                "Number of loans per month": ['month', 
                        'Number of loans per month',
                        'Based on the distribution of the total amount of loans per month, it can be assumed that the number of applications increases before the holiday season (April, May) and during the New Year period (November, December, January).']
                }

st.header('Distributions and outliers of variables')

if st.toggle('Show dataframe info'):
    buffer = io.StringIO()
    st.session_state.gc.info(buf=buffer)
    lines = buffer.getvalue().splitlines()
    info_df = (pd.DataFrame([x.split() for x in lines[5:-2]], columns=lines[3].split())
        .drop('Count',axis=1)
        .rename(columns={'Non-Null':'Non-Null Count', '#': '№'})
        .set_index('№')
        )
    col_left, col_mid, col_right = st.columns([0.1, 0.6, 0.3])
    col_mid.write(info_df)

var = st.sidebar.radio('Select variable to plot', ("Age", 
                              "Sex", 
                              "Housing", 
                              "Credit amount", 
                              "Duration of loan", 
                              "Purpose",
                              "Issued or rejected",
                              "Number of loans per month" 
                              ))
count_per_month = (
            st.session_state.gc
            .assign(month = lambda x: x['contract_dt'].dt.to_period('M').astype('string'))
        )

if var == 'Number of loans per month':
    df = count_per_month
else:
    df = st.session_state.gc

n_rows = 2 if is_numeric_dtype(df[get_df_var_name(var)[0]]) else 1

fig = make_subplots(rows=n_rows)
fig.add_histogram(
    x = df[get_df_var_name(var)[0]],
    name = 'Data distribution',
    row = 1,
    col = 1
)
if is_numeric_dtype(df[get_df_var_name(var)[0]]):
    fig.add_box(
        y = df[get_df_var_name(var)[0]],
        name = 'Main data characteristics',
        row=2,
        col = 1
    )

fig.update_layout(
    height = 450 * n_rows,
    title = dict(
        text = get_df_var_name(var)[1],
        font = dict(
            size = 24,
            weight = 'bold'
        )
    )
)

st.plotly_chart(fig)

st.subheader('Conclusions')
st.success(name_dict[var][2])

