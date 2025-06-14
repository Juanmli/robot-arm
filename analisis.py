import pandas as pd
import os
from datetime import datetime, timedelta
import openpyxl



#Se crea un diccionario con los nombres de los archivos como valor. 
CARPETA_CSV = "data"
ARCHIVOS = {
    "programs": "programs.csv",
    "errors": "errors.csv",
    "productivity": "productivity.csv",
    "modes": "modes.csv",
}
sample:dict = {
    'hora':'h',
    'diario': 'D',
    'mensual': 'm',
    'anual' : 'Y'
}  

# Cargar archivos CSV con estructura (timestamp, mensaje)
def cargar_csv(nombre_archivo): 

    path = os.path.join(CARPETA_CSV, nombre_archivo)  
    df = pd.read_csv(path,header=None, names=["timestamp", "message"], on_bad_lines='skip')
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    df['date'] = df['timestamp'].dt.date
    
    return df


def crear_dataframes(filtros):
    
    dataframes:dict = {}    

    for clave,valor in ARCHIVOS.items():
        if True:#filtros[clave] == True:
            dataframes[clave] = cargar_csv(valor) 
            dataframes[clave].set_index("timestamp", inplace=True)            
            dataframes[clave].index = pd.to_datetime(dataframes[clave].index)           

    for nombre, dataframe in dataframes.items():
        if nombre == 'errors':                        
            dataframes[nombre] = analizar_errores(dataframe, filtros)
        elif nombre == 'modes':
            dataframes[nombre] = analizar_modes(dataframe, filtros)
        elif nombre == 'productivity':
            dataframes[nombre] = analizar_productividad(dataframe, filtros)
        else:#nombre == 'programs'
            dataframes[nombre] = analizar_programas(dataframe, filtros)

    return dataframes

def analizar_errores(dataframe,filtros):#TODO
    print('analizando errores')     
    
    df = pd.DataFrame(dataframe["message"])
    return df

def analizar_modes(dataframe,filtros):
    df = analizar_productividad(dataframe,filtros)
    return df


def analizar_productividad(dataframe, filtros):
    '''
    Start = timestamp de inicio de actividad
    signal = puede ser free, stop, active, reset
    duration = cantidad de segundos entre señales.     
    '''
    tiempos = []
    i = 0 
    while i < len(dataframe.index):
        row = dataframe.iloc[i]        
        start = row.name
        j = i+ 1
        while j < len(dataframe.index):
            message = dataframe.iloc[j]["message"]           
            if message != row["message"]:
                end = dataframe.iloc[j].name                   
                if (start.date() == end.date()):                    
                    tiempos.append((start, limpiar_mensaje(row["message"]) ,(end-start).total_seconds()))                    
                else:
                    end_day = pd.Timestamp.combine(start, pd.Timestamp("23:59:59").time())
                    tiempos.append((start,limpiar_mensaje(row["message"]), (end_day-start).total_seconds()))
                    dia_actual = (start+timedelta(days=1)).date()
                    while dia_actual != end.date():
                        inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                        T = timedelta(days=1)
                        tiempos.append((inicio_aux,limpiar_mensaje(row["message"]),T))
                        dia_actual = dia_actual + timedelta(days=1)
                    inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                    T = (end -inicio_aux).total_seconds()
                    tiempos.append((inicio_aux,limpiar_mensaje(row["message"]),T))
                break
            j += 1
        i += 1                 
        
    df_prod = pd.DataFrame(tiempos, columns=["start", "name", "duration"])
    df_prod["start"] = pd.to_datetime(df_prod["start"])
    df_prod["duration"] = pd.to_timedelta(df_prod["duration"], unit = "s")    
    df_prod = df_prod.set_index("start")
      
    return df_prod


def agrupar_productividad(dataframe,filtros):
    time_filter = filtros["time_filter"]
    df_prod = dataframe.copy()
    df_prod.index = pd.to_datetime(df_prod.index)
    df_prod["date"] = df_prod.index.date
    if not pd.api.types.is_numeric_dtype(df_prod['duration']):
        df_prod['duration'] = pd.to_timedelta(df_prod['duration']).dt.total_seconds()
    df_agrupado = df_prod.groupby([pd.Grouper(freq=sample[time_filter]), 'name'])['duration'].sum().unstack(fill_value=0)
    df_agrupado.index = pd.to_datetime(df_agrupado.index)
    df_agrupado = completar_fechas_faltantes(df_agrupado, filtros)#---------------------------------------------------------------------------ojo acá


    print(df_agrupado)
    
    return df_agrupado

def agrupar_errores(dataframe,filtros):
    print("agrupando errores")    
    time_filter = filtros["time_filter"]
    df = dataframe.copy()    
    df.index = pd.to_datetime(df.index)
    df = dataframe.copy()    
    df.index = pd.to_datetime(df.index)
    df_agrupado = df["message"].groupby(pd.Grouper(freq=sample[time_filter])).size().to_frame()
    df_agrupado.index = pd.to_datetime(df_agrupado.index)
    df_agrupado = df_agrupado.rename(columns={"message": "errors"})
    df_agrupado.index.name = "date"
    df_agrupado = completar_fechas_faltantes(df_agrupado, filtros)
    return df_agrupado

def limpiar_mensaje(mensaje):
    if "to: " in mensaje:
        return mensaje.split("to: ")[1]

def analizar_programas(dataframe, filtros):
    print("analizando programas")
    tiempo_filtro = filtros['time_filter']      

    #Se crea un df que contiene:
    '''
    Start = un timestamp de inicio de un programa
    Name = el nombre del programa sin path ni extensión
    Duration = la cantidad de segundos que estuvo activo el programa      
    
    '''

    tiempos = []
    i = 0
    while i < len(dataframe.index):
        row = dataframe.iloc[i]
        if "Starting" in row["message"]:               
            start = row.name                
            j = i + 1 
            if j < len(dataframe.index):
                message = dataframe.iloc[j]["message"]
                end = dataframe.iloc[j].name 
                program_name = limpiar_nombre(message)
                if (start.date() == end.date()):
                    tiempos.append((start,program_name ,(end-start).total_seconds()))
                else:
                        end_day = pd.Timestamp.combine(start, pd.Timestamp("23:59:59").time())
                        tiempos.append((start,program_name, (end_day-start).total_seconds()))
                        dia_actual = (start+timedelta(days=1)).date()
                        while dia_actual != end.date():
                            inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                            T = timedelta(days=1)
                            tiempos.append((inicio_aux,program_name,T))
                            dia_actual = dia_actual + timedelta(days=1)
                        inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                        T = (end -inicio_aux).total_seconds()
                        tiempos.append((inicio_aux,program_name,T))
            i += 1
        else:
            i += 1

    df_progs = pd.DataFrame(tiempos, columns=["start", "name", "duration"])
    df_progs["start"] = pd.to_datetime(df_progs["start"])
    df_progs["duration"] = pd.to_timedelta(df_progs["duration"], unit = "s")    
    df_progs = df_progs.set_index("start")
    print("progs recióen analizados:---------------------------------------------------------")
    print(df_progs)  
    return df_progs











def limpiar_nombre(nombre:str):
    if (":\\") in nombre:
        nombre = nombre.split(":\\")[1].split(".")[0]
    if ("\\") in nombre:
        nombre = nombre.split("\\")[1]
    return nombre



    #Completar fechas faltantes:
def completar_fechas_faltantes(dataframe, filtros):
    fecha_inicio = filtros["tiempo_inicial"].date()
    fecha_fin = filtros["tiempo_final"].date()
    rango_fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq=sample[filtros["time_filter"]])
    df_completo = dataframe.reindex(rango_fechas, fill_value=0)
    return df_completo

