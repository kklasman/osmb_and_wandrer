import os
import logging_functions as lf

def get_filepath_for_filename(file_name):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, 'data', 'boundaries', file_name)
    # file_path = os.path.join(cwd, 'Lib', 'data', 'boundaries', file_name)
    lf.logger.info(f'file_path {file_path} exists {os.path.exists(file_path)}')
    if not os.path.exists(file_path):
        # file lives in a different folder in development
        file_path = os.path.join(cwd, r'data\boundaries', file_name)
    return file_path
