from datetime import date, datetime
import json

import sqlalchemy as sa
from sqlalchemy.engine.row import Row as saRow

from fstr_api.db import pereval_added_table, pereval_images_table


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def create_output_dict(table: sa.Table, data: saRow) -> dict:
    output = {}
    for column_name in table.columns.keys():
        value = getattr(data, column_name)
        if column_name == "raw_data" or column_name == "images":
            value = json.loads(value)
        output[column_name] = value

    return output


def create_pydantic_raw_data(pereval_data, images_data) -> dict:
    output = create_output_dict(pereval_added_table, pereval_data)
    byte_images = []
    for image_data in images_data:
        byte_image = create_output_dict(pereval_images_table, image_data)
        byte_images.append(byte_image)

    output["byte_images"] = byte_images
    return output
