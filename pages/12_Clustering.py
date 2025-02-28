import streamlit as st
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from streamlit_data.get_data import get_data

get_data()

st.header('Clustering clients with KMeans, DBSCAN')

st.subheader('KMeans clustering')
st.info('Our task is to understand the optimal number of clusters for further work with them')
gc_cluster = st.session_state.gc[['age', 'duration', 'credit_amount']]
for k in [3, 5, 8, 10]:
    km = KMeans(k)
    km.fit(gc_cluster)
    predicted_clusters = km.predict(gc_cluster)
    fig = px.scatter_3d(
    (gc_cluster.assign(predicted_clusters = predicted_clusters).sort_values('predicted_clusters')
    .assign(predicted_clusters = lambda x: (x['predicted_clusters'] + 1).astype('category'))
    ),
    x = 'age',
    y = 'duration',
    z = 'credit_amount',
    color = 'predicted_clusters',
    labels= {
        'age': 'Client age',
        'duration': 'Duration',
        'credit_amount': 'Loan amount',
        'predicted_clusters': 'Predicted clusters'
    }
    )
    fig.update_layout(
        title = dict(
            text = f'Dependence loan amount from duration and age with k = {k}'
        )
    )
    fig.update_traces(
        marker_size = 3
    )
    st.plotly_chart(fig)

st.success('As can be seen from the graphs, the most appropriate would be to divide the data into 3-5 clusters. A quantity of 8 is no longer obvious and makes working with data difficult')
if st.toggle('Show code', value = False):
    st.code(r"""
gc_cluster = st.session_state.gc[['age', 'duration', 'credit_amount']]
for k in [3, 5, 8, 10]:
    km = KMeans(k)
    km.fit(gc_cluster)
    predicted_clusters = km.predict(gc_cluster)
    fig = px.scatter_3d(
    (gc_cluster.assign(predicted_clusters = predicted_clusters).sort_values('predicted_clusters')
    .assign(predicted_clusters = lambda x: (x['predicted_clusters'] + 1).astype('category'))
    ),
    x = 'age',
    y = 'duration',
    z = 'credit_amount',
    color = 'predicted_clusters',
    labels= {
        'age': 'Client age',
        'duration': 'Duration',
        'credit_amount': 'Loan amount',
        'predicted_clusters': 'Predicted clusters'
    }
    )
    fig.update_layout(
        title = dict(
            text = f'Dependence loan amount from duration and age with k = {k}'
        )
    )
    fig.update_traces(
        marker_size = 3
    )
    st.plotly_chart(fig)
""", 'python')


st.subheader('DBSCAN clustering')
st.text('We need to define the epsilon parameter')

def plot_k_distance(X, k):
    neigh = NearestNeighbors(n_neighbors=k)
    neigh.fit(X)
    distances, _  = neigh.kneighbors(X)
    distances = np.sort(distances[:, k - 1])

    fig = px.line(distances,
                  labels={'value': '5-th nearest neighbor distance'}
                  )
    fig.update_layout(
        showlegend = False
    )
    fig.add_vline(x = 783, line_color = 'red', line_dash = 'dash')
    fig.add_hline(y = 0.4, line_color = 'red', line_dash = 'dash')
    return fig



gc_cluster_scaled = StandardScaler().fit_transform(gc_cluster)

st.plotly_chart(plot_k_distance(gc_cluster_scaled, 5))
if st.toggle('Show code', value=False, key='k_distance'):
    st.code(r"""
def plot_k_distance(X, k):
    neigh = NearestNeighbors(n_neighbors=k)
    neigh.fit(X)
    distances, _  = neigh.kneighbors(X)
    distances = np.sort(distances[:, k - 1])

    fig = px.line(distances,
                  labels={'value': '5-th nearest neighbor distance'}
                  )
    fig.update_layout(
        showlegend = False
    )
    fig.add_vline(x = 783, line_color = 'red', line_dash = 'dash')
    fig.add_hline(y = 0.4, line_color = 'red', line_dash = 'dash')
    return fig

st.plotly_chart(plot_k_distance(gc_cluster, 5))
""", 'python')
st.success("We select an epsilon value equal to 100 (the place of a start growth '5-th nearest neighbor distance' in the graph)")

dbscan_clusters = DBSCAN(eps = 0.4, min_samples=5).fit(gc_cluster_scaled)
labels = dbscan_clusters.labels_

fig = px.scatter_3d(
    (gc_cluster.assign(dbscan_clusters = dbscan_clusters.labels_)
     .assign(dbscan_clusters = lambda x: x['dbscan_clusters'].astype('category'))),
     x = 'age',
     y = 'duration',
     z = 'credit_amount',
     color='dbscan_clusters',
     labels= {
        'age': 'Client age',
        'duration': 'Duration',
        'credit_amount': 'Loan amount',
        'dbscan_clusters': 'Predicted clusters'
    }
)
fig.update_traces(
        marker_size = 5
)
st.plotly_chart(fig)
if st.toggle('Show code', value = False, key = 'dbscan_vis'):
    st.code(r"""
gc_cluster_scaled = StandardScaler().fit_transform(gc_cluster)
dbscan_clusters = DBSCAN(eps = 0.4, min_samples=5).fit(gc_cluster_scaled)
labels = dbscan_clusters.labels_

fig = px.scatter_3d(
    (gc_cluster_scaled.assign(dbscan_clusters = dbscan_clusters)
     .assign(dbscan_clusters = lambda x: x['dbscan_clusters'].astype('category'))),
     x = 'age',
     y = 'duration',
     z = 'credit_amount',
     color='dbscan_clusters',
     labels= {
        'age': 'Client age',
        'duration': 'Duration',
        'credit_amount': 'Loan amount',
        'dbscan_clusters': 'Predicted clusters'
    }
)
fig.update_traces(
        marker_size = 5
)
""")
st.text("Number of clusters:")
st.code("n_clusters = len(set(labels)) - (1 if -1 in labels else 0)", 'python')
st.write(f'Number of clusters = {len(set(labels)) - (1 if -1 in labels else 0)}')
st.text("Number of noize points:")
st.code("n_noise = list(labels).count(-1)", 'python')
st.write(f'Number of noize points = {list(labels).count(-1)}')
st.success('Judging by the work of two clustering algorithms, we can clearly distinguish three groups of observations based on age, loan duration and loan amount.')
