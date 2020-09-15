/***** AR_IMP_PERSONAL *****/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AR_IMP_PERSONAL](
	[SISTEMA] [varchar](10) NULL,
	[ESTADO] [varchar](10) NULL,
	[F_ALTA] [varchar](8) NULL,
	[COD_PERS] [varchar](10) NULL,
	[COD_EMP] [varchar](10) NULL,
	[MATRICULA] [varchar](10) NULL,
	[TARJETA] [varchar](50) NULL,
	[VERS_TARJ] [varchar](50) NULL,
	[INI_VAL] [varchar](8) NULL,
	[FIN_VAL] [varchar](8) NULL,
	[APELLIDOS] [varchar](40) NULL,
	[NOMBRE] [varchar](40) NULL,
	[DNI] [varchar](20) NOT NULL,
	[NUM_SS] [varchar](25) NULL,
	[MAIL] [varchar](100) NULL,
	[SEXO] [varchar](10) NULL,
	[F_NACIMIENTO] [varchar](8) NULL,
	[TLF_PERS] [varchar](20) NULL,
	[MOVIL] [varchar](20) NULL,
	[TLF_EMPR] [varchar](20) NULL,
	[EXTENSION] [varchar](10) NULL,
	[DIRECCION] [varchar](40) NULL,
	[POBLACION] [varchar](32) NULL,
	[PROVINCIA] [varchar](32) NULL,
	[COD_POST] [varchar](5) NULL,
	[EDIFICIO] [varchar](32) NULL,
	[PLANTA] [varchar](32) NULL,
	[DESPACHO] [varchar](32) NULL,
	[COD_CENT] [varchar](50) NULL,
	[RUTA_NIVELES] [varchar](255) NULL,
	[SEP_NIVELES] [varchar](5) NULL,
	[NIVEL_1] [varchar](50) NULL,
	[NIVEL_2] [varchar](50) NULL,
	[NIVEL_3] [varchar](50) NULL,
	[NIVEL_4] [varchar](50) NULL,
	[NIVEL_5] [varchar](50) NULL,
	[NIVEL_6] [varchar](50) NULL,
	[NIVEL_7] [varchar](50) NULL,
	[NIVEL_8] [varchar](50) NULL,
	[NIVEL_9] [varchar](50) NULL,
	[NIVEL_10] [varchar](50) NULL,
	[DATO_1] [varchar](255) NULL,
	[DATO_2] [varchar](255) NULL,
	[DATO_3] [varchar](255) NULL,
	[DATO_4] [varchar](255) NULL,
	[DATO_5] [varchar](255) NULL,
	[DATO_6] [varchar](255) NULL,
	[DATO_7] [varchar](255) NULL,
	[DATO_8] [varchar](255) NULL,
	[GRUPO_A] [varchar](40) NULL,
	[GRUPO_B] [varchar](40) NULL,
	[GRUPO_C] [varchar](40) NULL,
	[GRUPO_D] [varchar](40) NULL,
	[GRUPO_E] [varchar](40) NULL,
	[GRUPO_F] [varchar](40) NULL,
	[GRUPO_G] [varchar](40) NULL,
	[GRUPO_H] [varchar](40) NULL,
	[F_ALTA_EMPRESA] [varchar](8) NULL,
	[EMPLEO] [smallint] NULL,
	[CAL] [varchar](8) NULL,
	[CAL_FEST] [varchar](8) NULL,
	[NIF_EMP] [varchar](15) NULL,
	[NOMBRE_EMPLEO] [varchar](30) NULL,
	[FECHA_APLICACION] [int] NULL,
	[CONTROL_HORARIO] [varchar](14) NULL,
	[INI_CONTRATO] [varchar](8) NULL,
	[FIN_CONTRATO] [varchar](8) NULL
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[AR_IMP_PERSONAL] ADD  DEFAULT ((0)) FOR [EMPLEO]
GO

/***** AR_DOWNCONF *****/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AR_DOWNCONF](
	[DATE_TIME] [datetime] NULL,
	[TABLE_NAME] [varchar](max) NULL,
	[PARTIAL] [bit] NULL,
	[SOURCE] [varchar](max) NULL,
	[LIPS] [varchar](max) NULL,
	[HASH_CODE] [varchar](max) NULL,
	[END_TIME] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/***** custom function to get department path *****/
CREATE FUNCTION dbo.get_department_path(
    @id_node INT
)
RETURNS VARCHAR(max)
AS 
BEGIN
	DECLARE @path varchar(max) = (select GR_DESC from organigrama where GR_ID = @id_node);
	DECLARE @padre int = (select gr_padre from organigrama where GR_ID = @id_node);

	WHILE @padre <> 0
	BEGIN
		set @path = (select GR_DESC from organigrama where GR_ID = @padre) + ';' + @path;
		set @padre = (select gr_padre from organigrama where GR_ID = @padre);
	END

    RETURN @path;
END;

/***** custom view to expose department path *****/
CREATE VIEW [dbo].[AR_PERSO_DEPTOS]
AS
	SELECT 
		H.PERS_TIPO, H.PERS_CODIGO, P.PERS_DNI, H.GR_ID, dbo.get_department_path(H.GR_ID) as PATH
	FROM
		HST_ORGANIGRAMA as H
		INNER JOIN PERSONAS as P ON H.PERS_CODIGO = P.PERS_CODIGO
GO

-- after can use select * from [dbo].[AR_PERSO_DEPTOS]
