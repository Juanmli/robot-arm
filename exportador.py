from analisis import  agrupar_productividad, agrupar_errores
import pandas as pd
import os


carpeta_reportes = 'reports'


def generar_reporte(dfs,filtros):


    
    #Se filtran por fecha
    start = pd.to_datetime(filtros['tiempo_inicial'])
    end = pd.to_datetime(filtros['tiempo_final'])   
    time_filter = filtros["time_filter"]
    dataframes = dfs


    for nombre in list(dataframes.keys()):
        if not filtros[nombre]:
            del(dataframes[nombre])

    for nombre in list(dataframes.keys()):
        df = dataframes[nombre]
        df_filtrado = df[(df.index >= start) & (df.index <= end)]
        df_final = aplicar_timefilter(nombre, df_filtrado, filtros)
        print("así llega el df al exportador. ")
        print(nombre, df_final)
        dataframes[nombre] = df_final
             
    nombre_archivo = f"{start}-{end}.xlsx"
    excel_path = os.path.join(carpeta_reportes, nombre_archivo)
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        for nombre in list(dataframes.keys()):
            df = dataframes[nombre]           

            df.to_excel(writer,sheet_name=nombre)
              

    print(f"✅ Reporte generado: {excel_path}")


def aplicar_timefilter(nombre, dataframe, filtros):    
    time_filter = filtros["time_filter"]
    if time_filter == 'hora':
        return dataframe
    
    if nombre == 'errors':
        df = agrupar_errores(dataframe, filtros)
        df.index = df.index.date

    else:
        df = agrupar_productividad(dataframe, filtros)
        df.index = df.index.date
        for column in df.columns:
            df[column]=df[column]/3600
        

    return df