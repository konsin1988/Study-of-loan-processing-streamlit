import streamlit as st


st.title('Study of loan processing data using machine learning')

st.subheader('About dataset')
st.text('The original dataset contains 1000 entries with 20 categorial/symbolic attributes prepared by Prof. Hofmann. In this dataset, each entry represents a person who takes a credit by a bank. Each person is classified as good or bad credit risks according to the set of attributes.')
st.text('Variables:')
pad, col = st.columns([0.1, 0.9])
col.text(r'''
    1. Age (numeric)
    2. Sex (text: male, female)
    3. Job (numeric: 0 - unskilled and non-resident, 1 - unskilled and resident, 2 - skilled, 3 - highly skilled)
    4. Housing (text: own, rent, or free)
    5. Saving accounts (text - little, moderate, quite rich, rich)
    6. Checking account (numeric, in DM - Deutsch Mark)
    7. Credit amount (numeric, in DM)
    8. Duration (numeric, in month)
    9. Purpose (text: car, furniture/equipment, radio/TV, domestic appliances, repairs, education, business, vacation/others)
''')
pad, copyright_col = st.columns([0.4, 0.6])
copyright_col.markdown(":copyright: https://www.kaggle.com/datasets/uciml/german-credit")

st.subheader('Our goals')
st.text(r"""
1. Deploy docker containers for the application and database.
2. Create a connection to clickhouse, create a user, database, table and load data.  
3. Perform primary data analysis, find and eliminate inaccuracies in the data.
4. Analyze the data, try to find dependencies, display them graphically and in summary tables.
5. Perform client clustering, test two types of clustering, visualize the results.
6. Build a machine learning regression model that, based on the age and gender of the client and the purpose of the loan, will predict the approximate loan size.
""")

st.subheader('Development stack')
st.markdown(r"""
> **Python/Pandas/Numpy**  \
> **SQL/Clickhouse** \
> **Python/clickhouse_client** \
> **Plotly** \
> **Docker** \
> **Python/Scikit-learn**  \
> **Catboost**
""")

st.subheader('How to run?')
st.text('There are three ways to run the application:')
st.markdown(r'''
1. Locally, in docker containers. To start project, run in terminal: `docker compose up -d --build`. Then open http://localhost:8502
2. Locally, without docker. To start run in terminal: `streamlit run Introduction.py`. You need to have streamlit in your local machine.
3. In streamlit cloud, https://study-of-loan-processing-app.streamlit.app/
''')

st.subheader('Source code and contacts')
st.markdown('**Github**: https://github.com/konsin1988/Study-of-loan-processing-streamlit')
st.markdown('**Telegram**: @dmitry_konsin')


st.image('https://g.foolcdn.com/image/?url=https%3A//g.foolcdn.com/editorial/images/488167/handful-of-money.jpg&w=2000&op=resize')