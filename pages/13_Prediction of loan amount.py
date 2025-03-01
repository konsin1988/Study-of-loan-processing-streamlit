import streamlit as st
import plotly.express as px
import catboost as cb
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, root_mean_squared_error
from sklearn.model_selection import GridSearchCV
from streamlit_data.get_data import get_data

get_data()

st.header('Prediction of loan amount by gender, age, purpose')
st.info('Since we are dealing with the prediction of a continuum variable, we use regression analysis. The model has proven itself in various tasks, we choose catBoost')

st.text('Selecting features and target variables')
st.code(r'''X = df[['sex', 'age', 'purpose']]
y = df['credit_amount']''', 'python')
X = st.session_state.gc[['sex', 'age', 'purpose']]
y = st.session_state.gc['credit_amount']

st.text('Features:')
st.dataframe(X.head())

st.text('One-hot encoding')
st.code(r"""
X_dum = pd.get_dummies(X, columns=['sex', 'purpose'])
""", 'python')
X_dum = pd.get_dummies(X, columns=['sex', 'purpose'])

st.text('Split to train and test:')
st.code(r"""
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=1234)
""", 'python')
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=1234)

st.text('Fitting the model')
st.code(r"""
model = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6, verbose=0)
model.fit(X_train, y_train, cat_features=['sex', 'purpose'])
""", 'python')
model = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6, verbose=0)
model.fit(X_train, y_train, cat_features=['sex', 'purpose'])

st.text('Making forecasts and evaluating the model')
st.code(r"""
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)
""", 'python')
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

st.text('Calculate indicators on the training set')
st.code(r"""
print(f'MSE_train = {mean_squared_error(y_pred_train, y_train)}')
print(f'RMSE_train = {root_mean_squared_error(y_pred_train, y_train)}')
""", 'python')
st.text(f'MSE_train = {mean_squared_error(y_pred_train, y_train)}')
st.text(f'RMSE_train = {root_mean_squared_error(y_pred_train, y_train)}')

st.text('Calculate indicators on the test set')
st.code(r"""
print(f'MSE_test = {mean_squared_error(y_pred_test, y_test)}')
print(f'RMSE_test = {root_mean_squared_error(y_pred_test, y_test)}')
""", 'python')
st.text(f'MSE_test = {mean_squared_error(y_pred_test, y_test)}')
st.text(f'RMSE_test = {root_mean_squared_error(y_pred_test, y_test)}')

st.subheader('Now we will try to select more successful model hyperparameters')

X_train, X_test, y_train, y_test = train_test_split(X_dum, y, test_size=0.2, shuffle=True, random_state=1234)

st.text('Select the model')
st.code(r'''
model = CatBoostRegressor(loss_function='RMSE', verbose=0)
''', 'python')
model = CatBoostRegressor(loss_function='RMSE', verbose=0)

st.text('Setting hyperparameters')
st.code(r'''
param_grid = {
    'iterations': [100, 200, 500], 
    'learning_rate': [0.1, 0.05, 0.01], 
    'depth': [ 4, 6, 8]
}
''', 'python')
param_grid = {
    'iterations': [100, 200, 500], 
    'learning_rate': [0.1, 0.05, 0.01], 
    'depth': [ 4, 6, 8]
}

st.text('Fit model')
st.code(r'''
search = GridSearchCV(model, param_grid)
search.fit(X_train, y_train)
''', 'python')
with st.spinner('Search params...'):
    search = GridSearchCV(model, param_grid)
    search.fit(X_train, y_train)

text_col, output_col = st.columns([0.3, 0.7])
text_col.text('The best params:')
output_col.code(search.best_params_)

st.text('Making forecasts and evaluating the model with best hyperparams')
st.code(r'''
y_pred_train_best_estimator = search.best_estimator_.predict(X_train)
y_pred_test_best_estimator = search.best_estimator_.predict(X_test)
''')
y_pred_train_best_estimator = search.best_estimator_.predict(X_train)
y_pred_test_best_estimator = search.best_estimator_.predict(X_test)

st.text('Calculate metrics on the training set')
st.code(r'''
print(f'MSE_train = {mean_squared_error(y_pred_train_best_estimator, y_train)}')
print(f'RMSE_train = {root_mean_squared_error(y_pred_train_best_estimator, y_train)}')
''')
st.text(f'MSE_train = {mean_squared_error(y_pred_train_best_estimator, y_train)}')
st.text(f'RMSE_train = {root_mean_squared_error(y_pred_train_best_estimator, y_train)}')

st.text('Calculate metrics on the test set')
st.code(r'''
print(f'MSE_test = {mean_squared_error(y_pred_test_best_estimator, y_test)}')
print(f'RMSE_test = {root_mean_squared_error(y_pred_test_best_estimator, y_test)}')
''')
st.text(f'MSE_test = {mean_squared_error(y_pred_test_best_estimator, y_test)}')
st.text(f'RMSE_test = {root_mean_squared_error(y_pred_test_best_estimator, y_test)}')

st.success('On test data, the model with the selected hyperparameters performs slightly better.')