from datetime import date, datetime
import json

import sqlalchemy as sa
from sqlalchemy.engine.row import Row as saRow


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def create_output_dict(table: sa.Table, data: saRow) -> dict:
    output = {}
    for column_name in table.columns.keys():
        value = getattr(data, column_name)
        if column_name == "raw_data":
            value = json.loads(value)
        output[column_name] = value

    return output
