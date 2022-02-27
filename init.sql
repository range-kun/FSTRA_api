-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers.

-- Sequence and defined type

-- Table Definition
CREATE SEQUENCE IF NOT EXISTS pereval_id_seq;
CREATE TABLE pereval_added (
    "id" int4 NOT NULL DEFAULT nextval('pereval_id_seq'::regclass),
    "date_added" timestamp,
    "raw_data" json,
    "images" json,
    "status" VARCHAR(20),
    PRIMARY KEY ("id")
);

-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS pereval_areas_id_seq;

-- Table Definition
CREATE TABLE pereval_areas (
    "id" int8 NOT NULL DEFAULT nextval('pereval_areas_id_seq'::regclass),
    "id_parent" int8 NOT NULL,
    "title" text,
    PRIMARY KEY ("id")
);

-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS pereval_added_id_seq;

-- Table Definition
CREATE TABLE pereval_images (
    "id" int4 NOT NULL DEFAULT nextval('pereval_added_id_seq'::regclass),
    "date_added" timestamp DEFAULT now(),
    "img" bytea NOT NULL,
    PRIMARY KEY ("id")
);

-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS untitled_table_200_id_seq;

-- Table Definition
CREATE TABLE spr_activities_types (
    "id" int4 NOT NULL DEFAULT nextval('untitled_table_200_id_seq'::regclass),
    "title" text,
    PRIMARY KEY ("id")
);