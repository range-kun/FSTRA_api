from datetime import datetime
import json

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import sqlalchemy as sa

from fstr_api.db import async_session, engine, pereval_added_table, pereval_images_table
from fstr_api.models import RawData
from fstr_api.utils import json_serial

app = FastAPI()


@app.post("/submitData")
async def create_pereval_data(payload: RawData):
    try:
        images = RawData.__config__.json_dumps(
            payload.images,
            default=RawData.__json_encoder__
        )
        query_pereval_added = pereval_added_table.insert().values(
            date_added=payload.date_added,
            raw_data=json.dumps(payload.raw_data.dict(), ensure_ascii=False, default=json_serial),
            images=images,
            status=payload.status
        )

        bytes_images_list = [byte_image.dict() for byte_image in payload.byte_images]

        async with engine.begin() as conn:
            result = await conn.execute(query_pereval_added)
            row_id = result.inserted_primary_key[0]
            await conn.execute(
                pereval_images_table.insert(),
                bytes_images_list
            )

    except sa.exc.DBAPIError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content="Not valid sql:"
                    + f"SQL statment {e.statement}"
                    + f"SQL ERROR {e.orig}"
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Server technical problem. Please try latter"
        )

    return \
        f"New record with id {row_id} have been succesfully added"


@app.get("/submitData/{pereval_id}/status")
async def det_pereval_status(pereval_id: int):
    async with engine.begin() as conn:
        query = sa.select(
            pereval_added_table.c["status"]).where(pereval_added_table.c["id"] == pereval_id)
        result = await conn.execute(
            query
        )
        status = result.fetchone()
        if status:
            return f"Current status - {status[0]}"
        return f"An entry with the specified id {pereval_id} was not found"
