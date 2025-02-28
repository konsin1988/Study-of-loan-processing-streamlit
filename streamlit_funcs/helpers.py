import streamlit as st

# Docker and clickhouse init
def toggle_check_hide():
    st.session_state.check_hide = not st.session_state.check_hide

# Sum of all loan requested by gender
def __run_mode_changer():
    st.session_state.run_mode = not st.session_state.run_mode

def loading_button_clicked():
    st.session_state.loading_button_clicked = True

def toggle_run_mode():
    st.toggle('In docker container', 
          on_change=__run_mode_changer,
          value=st.session_state.run_mode,
          disabled=False if st.session_state.client == None else True)

def plot_code(query):
    toggle_col, info_col = st.columns([0.2, 0.8])
    if toggle_col.toggle('Show plot code', value=False):
        st.code(query, 'python')
    if st.session_state.run_mode:
        info_col.info('If you run code into docker containers, in order to see the plot, load the data ("Loading data" button) and run the code from the previous steps ("Run code" button)')

if __name__ == "__main__":
    toggle_check_hide, loading_button_clicked, toggle_run_mode, plot_code