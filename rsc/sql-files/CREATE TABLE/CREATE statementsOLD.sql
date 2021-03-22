-- Table: public.access
-- Table: public.building
-- Table: public.camera
-- Table: public.department
-- Table: public.room
-- Table: public.usercredentials
-- Table: public.userface

DROP TABLE IF EXISTS public.userface CASCADE;
DROP TABLE IF EXISTS public.usercredentials CASCADE;
DROP TABLE IF EXISTS public.room CASCADE;
DROP TABLE IF EXISTS public.department CASCADE;
DROP TABLE IF EXISTS public.camera CASCADE;
DROP TABLE IF EXISTS public.building CASCADE;
DROP TABLE IF EXISTS public.access CASCADE;

CREATE TABLE public.building
(
    "BuildingID" SERIAL,
    "BuildingName" character varying COLLATE pg_catalog."default" NOT NULL,
    "BuildingInfo" character varying COLLATE pg_catalog."default",
    CONSTRAINT "Building_pkey" PRIMARY KEY ("BuildingID"),
    CONSTRAINT "Building_BuildingID_key" UNIQUE ("BuildingID")

)

TABLESPACE pg_default;

ALTER TABLE public.building
    OWNER to postgres;
	

CREATE TABLE public.department
(
    "DepartmentID" SERIAL,
    "BuildingID" integer NOT NULL,
    "DepartmentName" character varying COLLATE pg_catalog."default" NOT NULL,
    "DepartmentInfo" character varying COLLATE pg_catalog."default",
    CONSTRAINT "Department_pkey" PRIMARY KEY ("DepartmentID"),
    CONSTRAINT "Department_DepartmentID_key" UNIQUE ("DepartmentID")
,
    CONSTRAINT "Department_BuildingID_fkey" FOREIGN KEY ("BuildingID")
        REFERENCES public.building ("BuildingID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.department
    OWNER to postgres;
	

CREATE TABLE public.room
(
    "RoomID" SERIAL,
    "DepartmentID" integer NOT NULL,
    "RoomNumber" character varying COLLATE pg_catalog."default" NOT NULL,
    "RoomInfo" character varying COLLATE pg_catalog."default",
    CONSTRAINT "RoomID" PRIMARY KEY ("RoomID"),
    CONSTRAINT "Room_RoomID_key" UNIQUE ("RoomID")
,
    CONSTRAINT "Room_DepartmentID_fkey" FOREIGN KEY ("DepartmentID")
        REFERENCES public.department ("DepartmentID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.room
    OWNER to postgres;


CREATE TABLE public.camera
(
    "RoomID" integer,
    "CameraName" character varying COLLATE pg_catalog."default" NOT NULL,
    "CameraIPAddress" character varying COLLATE pg_catalog."default",
    "CameraID" SERIAL,
    "CameraInfo" character varying COLLATE pg_catalog."default",
    CONSTRAINT "Camera_pkey" PRIMARY KEY ("CameraID"),
    CONSTRAINT "Camera_RoomID_fkey" FOREIGN KEY ("RoomID")
        REFERENCES public.room ("RoomID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public.camera
    OWNER to postgres;
	


CREATE TABLE public.usercredentials
(
    "UserID" SERIAL,
    "UserAccessLevel" integer NOT NULL,
    "Password" character varying COLLATE pg_catalog."default" NOT NULL,
    "UserName" character varying COLLATE pg_catalog."default" NOT NULL,
    "UserInfo" character varying COLLATE pg_catalog."default",
    CONSTRAINT "UserCredentials_pkey" PRIMARY KEY ("UserID"),
    CONSTRAINT "UserCredentials_UserID_key" UNIQUE ("UserID")

)

TABLESPACE pg_default;

ALTER TABLE public.usercredentials
    OWNER to postgres;
	


CREATE TABLE public.userface
(
    "UserID" SERIAL,
    "UserName" character varying COLLATE pg_catalog."default" NOT NULL,
    "UserSurname" character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "UserFace_pkey" PRIMARY KEY ("UserID"),
    CONSTRAINT "UserFace_UserID_key" UNIQUE ("UserID")

)

TABLESPACE pg_default;

ALTER TABLE public.userface
    OWNER to postgres;
	
CREATE TABLE public.access
(
    "UserID" integer NOT NULL,
    "RoomID" integer NOT NULL,
    CONSTRAINT "Access_RoomID_fkey" FOREIGN KEY ("RoomID")
        REFERENCES public.room ("RoomID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT "Access_UserID_fkey" FOREIGN KEY ("UserID")
        REFERENCES public.userface ("UserID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.access
    OWNER to postgres;
	