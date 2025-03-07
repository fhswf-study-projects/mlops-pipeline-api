import logging
from io import BytesIO
import os
from typing import Union

import pandas as pd


logger = logging.getLogger(__name__)


class DataFactory:
    @staticmethod
    def from_bytes(filename: str, file_bytes: bytes) -> Union[pd.DataFrame, None]:
        """
        Create a pandas DataFrame from file bytes based on file extension.

        Supports CSV, Excel, JSON, and Parquet formats.

        :param filename: Original filename (used for format detection)
        :param file_bytes: File content in bytes
        :return: Pandas DataFrame
        """
        file_stream = BytesIO(file_bytes)
        filename, extension = os.path.splitext(filename)

        if extension == ".csv":
            return pd.read_csv(file_stream)
        elif extension in [".xls", ".xlsx"]:
            return pd.read_excel(file_stream, engine="openpyxl")
        elif extension == ".json":
            return pd.read_json(file_stream)
        elif extension == ".parquet":
            return pd.read_parquet(file_stream, engine="pyarrow")
        else:
            logger.error(
                "Unsupported file format. Supported formats: CSV, Excel, JSON, Parquet."
            )
            return
