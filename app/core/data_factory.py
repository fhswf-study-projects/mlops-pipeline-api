import os
import logging
from io import BytesIO
from typing import Union, Dict

import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataFactory:
    @staticmethod
    def merge_dfs(*args) -> pd.DataFrame:
        try:
            return pd.concat([*args], ignore_index=True).drop_duplicates()
        except Exception as e:
            logger.exception(e)
        return args[0]

    @staticmethod
    def from_dict(d: Dict) -> Union[pd.DataFrame, None]:
        try:
            return pd.DataFrame([d])
        except Exception as e:
            logger.exception(f"Couldn't make df from python dict: {e}")
        return

    @staticmethod
    def from_bytes(filename: str, file_bytes: bytes) -> Union[pd.DataFrame, None]:
        """
        Create a pandas DataFrame from file bytes based on file extension.

        Supports CSV, Excel, JSON, and Parquet formats.

        :param filename: Original filename (used for format detection)
        :param file_bytes: File content in bytes
        :return: Pandas DataFrame or None if unsupported file format provided.
        """
        file_stream = BytesIO(file_bytes)
        filename, extension = os.path.splitext(filename)

        if extension == ".csv":
            return pd.read_csv(file_stream)  # type: ignore
        elif extension in [".xls", ".xlsx"]:
            return pd.read_excel(file_stream, engine="openpyxl")
        elif extension == ".json":
            return pd.read_json(file_stream)
        elif extension == ".parquet":
            return pd.read_parquet(file_stream, engine="pyarrow")

        logger.exception(
            "Unsupported file format. Supported formats: CSV, Excel, JSON, Parquet."
        )
        return
