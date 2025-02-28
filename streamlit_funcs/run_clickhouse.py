from random import randint
import streamlit as st
import pandas as pd

class ClickhouseCodeRunner:
    def __init__(self, query, command, key):
        self.__result = None
        self.__key = key
        self.__query = query 
        self.__command = command

    def show_code(self):
        self.__init_state()
        click_command = 'client.command(query)' if self.__command == 'command' else 'pd.DataFrame(client.query(query).named_results())'
        if st.session_state[self.__key + '_code_visibility']:
            st.code(("query = "+ "'''" + self.__query + "'''" + '\n' 
 + click_command), 'python')
        
    def __init_state(self):
        if f'{self.__key}_button' not in st.session_state:
            st.session_state[self.__key + '_button'] = False
        if f'{self.__key}_result' not in st.session_state:
            st.session_state[self.__key + '_result'] = []
        if f'{self.__key}_output_visibility' not in st.session_state:
            st.session_state[self.__key + '_output_visibility'] = True
        if f'{self.__key}_code_visibility' not in st.session_state:
            st.session_state[self.__key + '_code_visibility'] = True

    def __click_button(self):
        st.session_state[self.__key + '_button'] = True

    def __toggle_output_visibility(self):
        st.session_state[self.__key + '_output_visibility'] = not st.session_state[self.__key + '_output_visibility']

    def __toggle_code_visibility(self):
        st.session_state[self.__key + '_code_visibility'] = not st.session_state[self.__key + '_code_visibility']

    def __toggle_check_hide():
        st.session_state.check_hide = not st.session_state.check_hide
    
    def run_code(self, output = 'verbose'):
        self.__init_state()
        if st.session_state.run_mode and st.session_state.client != None:
            button_col, exception_col = st.columns([0.2, 0.8])
            button_col.button('Run code', key=self.__key, on_click=self.__click_button)

            if st.session_state[self.__key + '_button']:
                try:
                    (st.session_state.client.command(self.__query) 
                                if self.__command == 'command' 
                                else pd.DataFrame(st.session_state.client.query(self.__query).named_results()))
                except:
                    if not st.session_state.client:
                        exception_col.error('''You are not on **container** mode or don't get client. Try:
                                    
                                    `docker compose up -d --build in root directory`
                                            
            or get a clickhouse client at the top of this page''')
                    else:
                        exception_col.info("Table doesn't exists. Create table before run this command")
                        
                else:
                    output_visibility, code_visibility = exception_col.columns([0.5, 0.5])
                    output_visibility.checkbox('Output visibility', key = self.__key + '_hide_output', on_change=self.__toggle_output_visibility, value = True)
                    code_visibility.checkbox('Code visibility', key = self.__key + '_hide_code', on_change=self.__toggle_code_visibility, value = True)
                    self.__result = (st.session_state.client.command(self.__query) 
                                if self.__command == 'command' 
                                else pd.DataFrame(st.session_state.client.query(self.__query).named_results()))
                    st.session_state[self.__key + '_result'] = self.__result
                    self.__show_result(output)
                    st.success('Request completed')

    def __show_result(self, output):
        if output not in ['verbose', 'silent']:
            return st.error('Output mode not understood. Possible options: ["silent", "verbose"] ')
        if output == 'verbose':
            if st.session_state[self.__key + '_output_visibility']:
                if self.__command == 'command':
                    st.text(self.__result)
                else:
                    st.dataframe(self.__result)
    
    def get_result(self):
        return self.__result
    
    def get_status(self):
        return st.session_state[self.__key + '_button']

if __name__ == "__main__":
    ClickhouseCodeRunner