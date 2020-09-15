/* scripts to create ar_downconf and ar_imp_personal 

  ...

*/

-- custom function to get department path
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

-- custom view to expose department path
USE LEDESMA
GO

CREATE VIEW [dbo].[AR_PERSO_DEPTOS]
AS
	SELECT 
		H.PERS_TIPO, H.PERS_CODIGO, P.PERS_DNI, H.GR_ID, dbo.get_department_path(H.GR_ID) as PATH
	FROM
		HST_ORGANIGRAMA as H
		INNER JOIN PERSONAS as P ON H.PERS_CODIGO = P.PERS_CODIGO
GO



