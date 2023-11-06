# importarción de librerias que se van a utilizar.
import pandas as pd
import numpy as np

# definición del path del archivo y la hoja la cual se va a traer y depurar.
str_ruta = r'C:\Users\RentAdvisor\Bot2-Eficacia\Archivos Base\PLANTILLA REAL A LIQUIDAR  TRANSPORTES FINAL.xlsx'
str_nombre_hoja = 'FLETES'

# creación del dataframe de la hoja "FLETES"
df_fletes = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja)

# Depuración de las columnas para eliminar valores invalidos
columnas_tipo_texto = ['punto', 'tipo_despacho', 'pedido', 'identificacion', 'contacto', 'nombre_completo', 'nombre_ciudad', 'codigo_flete', 'usuario_pedido', 'dato_adicional_pedido', 'articulos', 'documentos1', 'documentos2', 'tipo_ubicacion', 'placa', 'nombre_conductor', 'transportador', 'nombre_transportador', 'clasificador1', 'soporte', 'proveedor', 'usuario_insercion', 'CONCATENAR PESO,PROVEEDOR ', 'CIUDA', 'DEPARTAMENTO', 'PUNTO ORIGEN ', 'RANGO VOLUMEN', 'RANGOPESO ', 'PESO COTIZADO ', 'VOLUMEN COTIZADO ']
columnas_tipo_numero = ['entrega', 'despacho', 'salida', 'codigo', 'departamento', 'ciudad', 'ruta_terrestre', 'total_peso', 'total_volumen', 'peso_cotizado', 'volumen_cotizado', 'cajas_cotizado', 'valor_mercancia', 'tiempo_real', 'demora', 'numero_guia']

for columna in columnas_tipo_texto:
    df_fletes[columna] = df_fletes[columna].fillna("")

for columna in columnas_tipo_numero:
    df_fletes[columna] = pd.to_numeric(df_fletes[columna], errors='coerce').replace(np.nan, 0, regex=True)

# Creación de nueva columna y conversión de la columna de "fecha_entrega" con formato fecha con hora a nueva columna "fecha_entrega_dia" con formato año-mes-día
df_fletes['fecha_entrega_dia'] = df_fletes['fecha_entrega'].dt.date

# Creación de nuevas columnas necesarias dentro del dataframe
df_fletes['tipo']=""
df_fletes['tipo_ruta']=""
df_fletes['validacion_24h']=""
df_fletes['valor_bot']=""
df_fletes['valor_original_bot']=""

# definición de las hojas que serán traidas.
str_nombre_hoja2 = 'TIPO RUTA'
str_nombre_hoja3 = 'TARIFA CLIENTE'
str_nombre_hoja4 = 'TARIFA PROVEEDOR'
str_nombre_hoja5 = 'TARIFA P y V'
str_nombre_hoja6 = 'CODIGO FLETE'

# creación de los dataframes con valores estandarizados que serán necesarios.
df_tipo_ruta = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja2)
df_tarifa_cliente = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja3)
df_tarifa_proveedor = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja4)
df_tarifa_pv = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja5)
df_codigo_flete = pd.read_excel(str_ruta, sheet_name=str_nombre_hoja6)

# Definición de todos las filas con la palabra "PERIFERIA"
df_fletes['tipo_ruta'] = 'PERIFERIA'

# Iteración a través de las filas del dataframe df_fletes y comparación con el dataframe df_tipo_ruta
for i, fila in df_fletes.iterrows():
    punto = fila['punto']
    ciudad = fila['nombre_ciudad']

    # Verificación de coincidencias en df_tipo_ruta y asignación de la palabra "LOCAL" en las filas necesarias
    if any((df_tipo_ruta['CEDIS'] == punto) & (df_tipo_ruta['CIUDAD'] == ciudad)):
        df_fletes.at[i, 'tipo_ruta'] = 'LOCAL'

# Creación de grupos por respectivos filtros para despachos y recogidas
filtro = (df_fletes['tipo_ruta'] == 'LOCAL') & ((df_fletes['tipo_despacho'] == 'DESPACHO') | (df_fletes['tipo_despacho'] == 'RECOGIDA'))
df_dr_locales = df_fletes[filtro].groupby(['punto', 'fecha_entrega', 'proveedor', 'identificacion'])


# Tipos de despachos que hay por cada una de las agrupaciones
valores_unicos_despachos = df_dr_locales['tipo_despacho'].apply(lambda x: x.unique())

############ Descomentar si se desea ver los grupos ################
"""for indice, datos in df_grupo_locales:
  print("....indice={}".format(indice))
  print("--------datos-------")
  print(datos)"""

# Conversión de los tipos de despacho por grupo a un dataframe para su mejor manipulación
df_tipo_liquidar = valores_unicos_despachos.to_frame(name='tipo')

# Creación de nueva columna dentro del dataframe df_tipo_grupo_ruta
df_tipo_liquidar["tipo_grupo_ruta"] = ""
df_tipo_liquidar["numero_despachos"] = ""
df_tipo_liquidar["transportador"] = ""
df_tipo_liquidar['codigos_flete'] = ""

# Función para clasasificar los grupos por tipos de despacho
def asignar_valor(row):
    if set(row['tipo']) == set(['DESPACHO']):
        return 1
    elif set(row['tipo']) == set(['RECOGIDA']):
        return 2
    elif set(row['tipo']) == set(['RECOGIDA','DESPACHO']):
        return 3
    else:
        return 0

# Asignación de la clasificación a la columna "tipo_grupo_ruta" dentro del dataframe df_tipo_grupo_ruta
df_tipo_liquidar['tipo_grupo_ruta'] = df_tipo_liquidar.apply(asignar_valor, axis=1)

# conteo de despachos por agrupación
conteo_despacho = df_dr_locales['despacho'].agg(lambda x: x.nunique())
conteo_a_lista = conteo_despacho.tolist()

# Asignación de conteo a dataframe df_tipo_grupo_ruta
df_tipo_liquidar['numero_despachos'] = conteo_a_lista

# valor de transportador por despacho
valores_transportador = df_dr_locales['transportador'].apply(lambda x: x.unique())
valores_a_lista = valores_transportador.tolist()

# Asignación de valores a dataframe df_tipo_grupo_ruta
df_tipo_liquidar['transportador'] = valores_a_lista

# valores de codigo de flete por despacho cada despacho
valores_codigo_flete = df_dr_locales['codigo_flete'].apply(lambda x: x.unique())
valores_codigo_a_lista = valores_codigo_flete.tolist()

# Asignación de valores a dataframe df_tipo_grupo_ruta
df_tipo_liquidar['codigos_flete'] = valores_codigo_a_lista