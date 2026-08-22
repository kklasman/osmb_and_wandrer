import functools
from geopandas import GeoDataFrame
import hashlib
import json
import os
import shutil
import tempfile
import weakref
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import logging
logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that converts numpy arrays and scalars into serializable Python types."""

    def default(self, obj):
        # 1. Convert multidimensional numpy arrays to standard lists
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # 2. Convert numpy integer scalars (e.g., int64, int32) to Python int
        if isinstance(obj, np.integer):
            return int(obj)

        # 3. Convert numpy float scalars (e.g., float64, float32) to Python float
        if isinstance(obj, np.floating):
            return float(obj)

        # 4. Delegate everything else to the parent JSONEncoder
        return super().default(obj)


def _make_hashable(val):
    """Converts unhashable items (DataFrames, lists) into hashable strings/tuples."""
    if isinstance(val, pd.DataFrame):
        df_hash_array = pd.util.hash_pandas_object(val, index=True).values
        return hashlib.sha256(df_hash_array.tobytes()).hexdigest()
    if isinstance(val, (list, set, tuple)):
        # Sorted to handle arbitrary user selection order
        try:
            return tuple(_make_hashable(item) for item in sorted(val))
        except TypeError:
            return tuple(_make_hashable(item) for item in val)
    if isinstance(val, dict):
        return tuple((k, _make_hashable(v)) for k, v in sorted(val.items()))
    return val


class SessionDiskCleanup:
    """Manages a temporary directory linked to a specific user session."""

    def __init__(self):
        logger.info(f'Cleaning Cache...')
        self.dir_path = tempfile.mkdtemp(prefix="st_session_cache_")
        # Finalizer deletes the entire folder when this object gets garbage collected
        self._finalizer = weakref.finalize(self, shutil.rmtree, self.dir_path)

    def remove(self):
        """Manual cleanup if needed."""
        self._finalizer()


def cache_to_disk_session(func):
    """
    Decorator that caches Plotly figures to files.
    Files are automatically deleted when the user closes their session.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Ensure this user session has its own private, self-cleaning disk directory
        # Filter out GeoDataFrame objects
        filtered_args = [
            str(arg) for arg in args
            if not isinstance(arg, GeoDataFrame)
        ]

        # Create the final f-string style output
        result = f"{' '.join(filtered_args)}"
        print(result)  # Output: City 42 Population 1000

        if "_session_disk_manager" not in st.session_state:
            st.session_state["_session_disk_manager"] = SessionDiskCleanup()
            st.session_state["_disk_cache_registry"] = {}

        session_dir = st.session_state["_session_disk_manager"].dir_path
        registry = st.session_state["_disk_cache_registry"]

        # 2. Build the unique cache key from inputs
        hashable_args = tuple(_make_hashable(arg) for arg in args)
        hashable_kwargs = tuple((k, _make_hashable(v)) for k, v in sorted(kwargs.items()))
        cache_key = (func.__name__, hashable_args, hashable_kwargs)

        # 3. CACHE HIT: Read file from disk and reconstruct the Plotly Figure
        if cache_key in registry:
            logger.info(f"Cache HIT on function {func.__name__}, args: {filtered_args}")
            file_path = registry[cache_key]
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    fig_dict = json.load(f)
                return go.Figure(fig_dict)

        # 4. CACHE MISS: Run function, save result to a file, free RAM
        logger.info(f"Cache MISS on function {func.__name__}, args: {filtered_args}")
        fig = func(*args, **kwargs)

        # Create a unique filename for this plot configuration
        key_string = str(cache_key).encode("utf-8")
        file_name = f"{hashlib.md5(key_string).hexdigest()}.json"
        file_path = os.path.join(session_dir, file_name)

        # Write Plotly's underlying dictionary structure to disk
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(fig.to_dict(), f, cls=NumpyEncoder)

        # Store only the file path string in memory, not the heavy object
        registry[cache_key] = file_path
        return fig

    return wrapper
