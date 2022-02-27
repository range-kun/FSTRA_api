from datetime import datetime
import json

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from fstr_api.db import pereval_added_table, engine
from fstr_api.models import PerevalAddedIn
from fstr_api.utils import json_serial

app = FastAPI()


@app.post("/submitData")
async def create_pereval_data(payload: PerevalAddedIn):
    try:
        images = PerevalAddedIn.__config__.json_dumps(
            payload.images,
            default=PerevalAddedIn.__json_encoder__
        )
        query = pereval_added_table.insert().values(
            date_added=datetime.now(),
            raw_data=json.dumps(payload.raw_data.dict(), ensure_ascii=False, default=json_serial),
            images=images,
            status=payload.status
        )

        async with engine.begin() as conn:
            result = await conn.execute(query)
            row_id = result.inserted_primary_key[0]
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Server technical problem. Please try latter"
        )

    return f"New record with id {row_id} have been succesfully added"
