from datetime import datetime
from enum import Enum
import re
from typing import Optional


from pydantic import BaseModel, EmailStr, validator


class ImageLinks(BaseModel):
    sedlo: Optional[list[int]]
    Nord: Optional[list[int]]
    West: Optional[list[int]]
    South: Optional[list[int]]
    East: Optional[list[int]]


class User(BaseModel):
    id: int
    email: Optional[EmailStr]
    phone: str
    fam: Optional[str]
    name: Optional[str]
    otc: Optional[str]

    @validator("phone")
    def phone_validation(cls, phone_number: str) -> str:
        regex = r"^\+?[1-9][0-9\-\(\)\.]{9,15}$"
        if phone_number and not re.search(regex, phone_number, re.I):
            raise ValueError("Invalid Phone Number ")
        return phone_number


class Coords(BaseModel):
    latitude: float
    longitude: float
    height: int

    @validator("latitude")
    def latitude_validation(cls, number: float) -> float:
        if not -90 <= number <= 90:
            raise ValueError("Latitude Invalid value. Make sure its in range -90 : 90")
        return number

    @validator("longitude")
    def longitude_validation(cls, number: float) -> float:
        if not -180 <= number <= 180:
            raise ValueError("Longitude Invalid value. Make sure its in range -180 : 180")
        return number


class Level(BaseModel):
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class GeoData(BaseModel):
    pereval_id: int
    beautyTitle: str
    title: str
    other_titles: Optional[str]
    connect: Optional[str]

    user: User

    coords: Coords
    type: str = "pass"

    level: Level


class GeoDataOut(BaseModel):
    pereval_id: int
    beautyTitle: str
    title: str
    other_titles: Optional[str]
    connect: Optional[str]

    coords: Coords
    type: str = "pass"

    level: Level


class PerevalImages(BaseModel):
    date_added: datetime
    img: bytes


class StatusEnum(str, Enum):
    new = "new"
    pending = "pending"
    resolved = "resolved"
    accepted = "accepted"
    rejected = "rejected"


class RawData(BaseModel):
    date_added: datetime
    raw_data: GeoData
    images: ImageLinks
    status: StatusEnum = StatusEnum.new
    byte_images: list[PerevalImages]


class RawDataOut(BaseModel):
    date_added: datetime
    raw_data: GeoDataOut
    status: StatusEnum = StatusEnum.new
    images: ImageLinks
    byte_images: list[PerevalImages]

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
        }


class RawDataUpdate(BaseModel):
    date_added: datetime
    raw_data: GeoDataOut
    images: Optional[ImageLinks]
    byte_images: Optional[list[PerevalImages]]


class UserSubmittedData(BaseModel):
    sent_data: list[RawDataOut]
