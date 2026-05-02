import os
from streamlit import session_state as ss
import utilities as u

def get_geojson_filename(selected_state):
    cwd = os.getcwd()
    # file_name = st.session_state.geojson_files_dict[selected_state]
    # filename_column = 'geojson_filename' if st.session_state.selected_maptype == 'Town' else 'state_geojson_filename'
    # file_name = ss.wandrer_regions.query(f'State == "{selected_state}"')[filename_column].to_list()[0]
    geojson_column_name = ''
    # match ss.selected_map_type:
    #     case 'State':
    #         geojson_column_name = 'state_geojson_filename'
    #     case 'County':
    #         geojson_column_name = 'county_geojson_filename'
    #     case _:
    #         geojson_column_name = 'geojson_filename'

    file_name = ss.wandrer_regions.query(f'State == "{selected_state}"')['geojson_filename'].to_list()[0]
    if file_name is None:
        return ''

    # file_path = os.path.join(cwd, r'data\10150\boundaries', file_name)
    file_path = u.get_filepath_for_filename(file_name)

    # file_path = os.path.join(cwd, r'data\boundaries', file_name)
    filesize = os.path.getsize(file_path)
    return file_path
