import plotly
import streamlit as st
from streamlit import session_state as ss
import sys

@st.dialog("Settings")
def settings():
    # ss

    st.write("User Settings")
    # st.checkbox('Show raw data grid', key='show_raw_data', value=st.session_state.show_raw_data_state)
    show_raw_data = ss.cookie_controller.get('show_raw_data_state')
    print(f'{show_raw_data=}')
    st.checkbox('Show raw data grid', key='show_raw_data', value=show_raw_data)
    st.checkbox('Hide locations with 0 values', key='hide_zero_data', value=st.session_state.hide_zero_data_state)

    st.write('About:')
    with st.container(height=100, gap=None):
        st.write(f'Plotly version: {plotly.__version__}')
        st.write(f'python version: {sys.version.split(" ")[0]}')
        st.write(f'Streamlit version: {st.__version__}')

    # st.write(f"Checkbox value from session state: {st.session_state.show_raw_data_state}")

    if st.button('Close', key='close'):
        st.session_state.show_raw_data_state = ss.show_raw_data
        ss.cookie_controller.set('show_raw_data_state', ss.show_raw_data)
        st.session_state.hide_zero_data_state = ss.hide_zero_data
        st.session_state.settings_dismissed = True
        st.rerun()
