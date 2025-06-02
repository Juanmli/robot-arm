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
    tiempo_filtro = filtros['time_filter']
    if tiempo_filtro == "hora":
        df = dataframe
    else:
        df = dataframe.resample(sample[tiempo_filtro]).size().rename('amount').to_frame()
    print("listo")
    return df
    

#def analizar_modes(dataframe,filtros):
    print("analizando modos")
    tiempo_filtro = filtros['time_filter']
    if tiempo_filtro == "hora":
        messages = []
        for i in range(len(dataframe.index)):
            message = dataframe.iloc[i]["message"]
            if message not in messages:
                messages.append(message)      


        messages_dict_map = dict()
        for i in range(len(messages)):
            messages_dict_map[messages[i]] = i
         
        dataframe['message_mapped'] = dataframe['message'].copy().map(messages_dict_map)
    
    else:
        dataframe= dataframe.resample(sample[tiempo_filtro]).size().rename('amount').to_frame()
    print("listo")
    return dataframe

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
        print(row["message"])
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
        print(i)           
        
    df_prod = pd.DataFrame(tiempos, columns=["start", "status", "duration"])
    df_prod["start"] = pd.to_datetime(df_prod["start"])
    df_prod["duration"] = pd.to_timedelta(df_prod["duration"], unit = "s")    
    df_prod = df_prod.set_index("start")#,drop = False)

    if filtros["time_filter"] == "hora":      
        return df_prod

    if filtros["time_filter"] == "diario":
        df_prod.index = pd.to_datetime(df_prod.index)
        df_prod["date"]=df_prod.index.date
        if not pd.api.types.is_numeric_dtype(df_prod['duration']):
            df_prod['duration'] = pd.to_timedelta(df_prod['duration']).dt.total_seconds()
        df_agrupado = df_prod.groupby(['date', 'status'])['duration'].sum().unstack(fill_value=0)
        df_agrupado.index = pd.to_datetime(df_agrupado.index)
        return df_agrupado

def agrupar_dataframe(dataframe,filtros):
    pass

def limpiar_mensaje(mensaje):
    if "to: " in mensaje:
        return mensaje.split("to: ")[1]

def analizar_programas(dataframe,filtros):#TODO
    print("analizando programas")
    tiempo_filtro = filtros['time_filter']
    
    if tiempo_filtro == "hora":       

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
                while j < len(dataframe.index):
                    message = dataframe.iloc[j]["message"]
                    if ("Completed" in message) and  limpiar_nombre(message) == limpiar_nombre(row["message"]):
                        #print("programa terminado!")
                        program_name = limpiar_nombre(message)
                        end = dataframe.iloc[j].name                   
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
                        break
                    j += 1
                i += 1
            else:
                i += 1
                    
        df_progs = pd.DataFrame(tiempos, columns=["start", "name", "duration"])
        df_progs["start"] = pd.to_datetime(df_progs["start"])
        df_progs["duration"] = pd.to_timedelta(df_progs["duration"], unit = "s")    
        df_progs = df_progs.set_index("start",drop = False)      
        return df_progs

    else:            
        df_progs = dataframe[dataframe["message"].str.contains("Completed", na=False)]
        df_progs = df_progs.resample(sample[tiempo_filtro]).size().rename('amount').to_frame()
        #dataframe = dataframe.groupby("message").size().rename("amount").to_frame()

        print("listo")
        return dataframe

def limpiar_nombre(nombre:str):
    if (":\\") in nombre:
        nombre = nombre.split(":\\")[1].split(".")[0]
    if ("\\") in nombre:
        nombre = nombre.split("\\")[1]
    return nombre

def calcular_tiempo_activo(df_prod,filtros):
    print("calculando tiempo activo")
    tiempos = []
    i = 0
    while i < len(df_prod): 
        row = df_prod.iloc[i]        
        if "Active" in row["message"]:
            start = row.name
            j = i + 1
            while j < len(df_prod):
                msg = df_prod.iloc[j]["message"]                
                if "Active" not in msg:                   
                    end = df_prod.iloc[j].name
                    if (end.date() == start.date()):
                        tiempos.append((start.date(), (end - start).total_seconds()))                    
                    else:
                        end_day = pd.Timestamp.combine(start, pd.Timestamp("23:59:59").time())
                        tiempos.append((start.date(), (end_day-start).total_seconds()))
                        dia_actual = (start+timedelta(days=1)).date()
                        while dia_actual != end.date():
                            inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                            T = timedelta(days=1)
                            tiempos.append((inicio_aux.date(),T))
                            dia_actual = dia_actual + timedelta(days=1)
                        inicio_aux = pd.Timestamp.combine(dia_actual, pd.Timestamp("00:00:00").time())
                        T = (end -inicio_aux).total_seconds()
                        tiempos.append((inicio_aux.date(),T))

                        '''                            
                        end_day = pd.Timestamp.combine(start.date(),pd.Timestamp("23:59").time())
                        tiempos.append((start.date(), (end_day - start).total_seconds()))
                        start_day = pd.Timestamp.combine(end.date(),pd.Timestamp("00:01").time())
                        tiempos.append((start_day.date(), (end - start_day).total_seconds()))'''
                    break
                j += 1
            i = j
        else:
            i += 1
    df_tiempos = pd.DataFrame(tiempos, columns=["date", "tiempo"])
    df_tiempos["date"] = pd.to_datetime(df_tiempos["date"])
    tiempo_activo = agrupar_por_tiempo(df_tiempos, filtros["time_filter"])
    return tiempo_activo

    
def agrupar_por_tiempo(df, filtro):
    if filtro == "mensual":
        agrupado = df.groupby(df["date"].dt.to_period("M"))["tiempo"].sum()
        agrupado.index = agrupado.index.to_timestamp()
    elif filtro == "anual":
        agrupado = df.groupby(df["date"].dt.to_period("Y"))["tiempo"].sum()
        agrupado.index = agrupado.index.to_timestamp()
    else:  # diario
        agrupado = df.groupby(df["date"].dt.floor("D"))["tiempo"].sum()
    return agrupado.to_frame(name="tiempo")



