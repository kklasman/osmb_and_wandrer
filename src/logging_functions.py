import logging

# Configure the root logger
logging.basicConfig(level=logging.INFO)

# Get a logger for the current module
logger = logging.getLogger(__name__)

# logger.info(f'python version: {sys.version}')
# logger.info(f'python version_info: {sys.version_info}')
# logger.info(f'Streamlit version: {st.__version__}')
