import json
from typing import Optional, Union

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import sqlalchemy as sa
from sqlalchemy.sql.dml import Update as saUpdate


from fstr_api.db import async_session, engine, pereval_added_table, pereval_images_table
from fstr_api.models import RawData, RawDataOut, UserSubmittedData, RawDataUpdate
from fstr_api.utils import json_serial, create_pydantic_raw_data

app = FastAPI()


@app.post("/submitData")
async def create_pereval_data(payload: RawData):
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
    pereval_byte_new_images = [byte_image.dict() for byte_image in payload.byte_images]
    response = await update_submitted_data(query_pereval_added, pereval_byte_new_images)
    if type(response) == int:
        return f"New record with id {response} have been succesfully added"
    return response


@app.get("/submitData/{pereval_id}/status")
async def get_pereval_status(pereval_id: int):
    query = sa.select(
        pereval_added_table.c["status"]).where(pereval_added_table.c["id"] == pereval_id)

    async with engine.begin() as conn:
        result = await conn.execute(
            query
        )
        status = result.fetchone()
    if status:
        return f"Current status - {status[0]}"
    return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=f"An entry with the specified id {pereval_id} was not found"
        )


@app.get("/submitData/", response_model=UserSubmittedData)
async def get_sumbited_data(
        email: Optional[str] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        fam: Optional[str] = None,
        otc: Optional[str] = None,
):
    query_params = {"email": email, "phone": phone, "name": name, "fam": fam, "otc": otc}

    if not any(query_params.values()):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=f"Please specify one of the following query to proceed search process:"
                    f" email, name, phone, lastname"
        )

    pereval_query = sa.select(pereval_added_table)
    for name, value in query_params.items():
        if value is None:
            continue
        pereval_query = pereval_query.filter(sa.text(f"raw_data::text like '%{value}%'"))

    pereval_query = pereval_query.where(pereval_added_table.c["status"] == "new")
    async with engine.begin() as conn:
        pereval_rows = await conn.execute(pereval_query)

    pereval_data = pereval_rows.fetchall()
    if not pereval_data:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=f"Entry with specify parameters wasn't found"
        )
    pererval_dict_data = {row["id"]: row for row in pereval_data}

    image_conditions = \
        [pereval_images_table.c["pereval_added_id"] == id_ for id_ in pererval_dict_data]
    image_query = sa.select(pereval_images_table).filter(sa.or_(*image_conditions))
    async with engine.begin() as conn:
        rows = await conn.execute(image_query)
    byte_images = rows.fetchall()

    output = []
    for pererval_id in pererval_dict_data:
        byte_images_id = [byte_image for byte_image in byte_images
                          if byte_image["pereval_added_id"] == pererval_id]
        pydantic_dict = create_pydantic_raw_data(
            pererval_dict_data[pererval_id],
            byte_images_id
        )
        output.append(pydantic_dict)
    return {"sent_data": output}


@app.get("/submitData/{pereval_id}", response_model=RawDataOut)
async def get_pereval_info(pereval_id: int):
    pereval_data, images_data = await fetch_pereval_info(pereval_id)

    if pereval_data is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=f"An entry with the specified id {pereval_id} was not found"
        )
    try:
        return create_pydantic_raw_data(pereval_data, images_data)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Server technical problem. Please try latter"
        )


@app.put("/submitData/{pereval_id}")
async def get_update_info(pereval_id: int, payload: RawDataUpdate):
    pereval_sql_data, _ = await fetch_pereval_info(pereval_id)
    pereval_new_data = {key: value for key, value in payload.dict().items() if value}

    try:
        pereval_byte_new_images = pereval_new_data.pop("byte_images")
    except KeyError:
        pereval_byte_new_images = []

    if pereval_sql_data is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=f"An entry with the specified id {pereval_id} was not found"
        )
    if pereval_sql_data["status"] != "new":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Current entry already has been proceed"
        )

    try:
        raw_data = json.loads(pereval_sql_data["raw_data"])
    except json.decoder.JSONDecodeError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Not valid json data at field raw data"
        )

    for key, value in payload.raw_data.dict().items():
        if value:
            raw_data[key] = value
    pereval_new_data["raw_data"] = json.dumps(
        payload.raw_data.dict(),
        ensure_ascii=False,
        default=json_serial
    )

    if pereval_new_data.get("images"):
        images = RawDataUpdate.__config__.json_dumps(
            pereval_new_data["images"],
            default=RawData.__json_encoder__
        )
        pereval_new_data["images"] = images

    query_pereval_added = sa.update(pereval_added_table).where(
        pereval_added_table.c["id"] == pereval_id).values(**pereval_new_data)

    response = await update_submitted_data(query_pereval_added, pereval_byte_new_images, pereval_id)
    if type(response) == int:
        return f"Entry with id {pereval_id} has been successfully updated"
    return response


async def fetch_pereval_info(pereval_id: int):
    query_date_added = sa.select(pereval_added_table).where(
        pereval_added_table.c["id"] == pereval_id
    )
    query_images = pereval_images_table.select().where(
        pereval_images_table.c["pereval_added_id"] == pereval_id
    )
    async with async_session() as session:
        pereval_db_data = await session.execute(query_date_added)
        images_db_data = await session.execute(query_images)

    pereval_data = pereval_db_data.fetchone()
    images_data = images_db_data.fetchall()
    return pereval_data, images_data


async def update_submitted_data(
        query_pereval_added: saUpdate,
        pereval_new_images: list[dict],
        main_id: Optional[int] = None
) -> Union[int, JSONResponse]:
    try:
        async with async_session() as session:
            result = await session.execute(query_pereval_added)
            if not main_id:
                main_id = result.inserted_primary_key[0]
            await session.execute(query_pereval_added)
            for byte_image in pereval_new_images:
                image_query = pereval_images_table.insert().values(
                    date_added=byte_image["date_added"],
                    img=byte_image["img"],
                    pereval_added_id=main_id
                )
                await session.execute(image_query)

            await session.commit()
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
    return int(main_id)
