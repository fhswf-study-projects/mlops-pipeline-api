import json

import pandas as pd


def retrieve_metadata(data: pd.DataFrame) -> str:
    metadata = {}

    for col in data.columns:
        metadata[col] = data[col].dropna().unique().tolist()  # type: ignore
    return json.dumps(metadata)


def get_metadata(client, bucket: str, object_name: str) -> dict:
    return client.get_object_attributes(
        Bucket=bucket, Key=object_name, ObjectAttributes=["Metadata"]
    )
