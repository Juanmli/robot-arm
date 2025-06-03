from matplotlib.figure import Figure
from analisis import crear_dataframes, agrupar_productividad, agrupar_errores
import matplotlib.dates as mdates
import pandas as pd
import random
import numpy as np

max_xticks = 5

def crear_graficos(dfs, filtros):

    start = pd.to_datetime(filtros['tiempo_inicial'])
    end = pd.to_datetime(filtros['tiempo_final'])     
    #crear_dataframes devuelve un diccionario con el nombre del dataframe como clave, y el 
    #propio df como valor. 
    #dataframes = crear_dataframes(filtros)
    dataframes = dfs.copy()     
    #Elimino dfs que no están en el filtro
    for nombre in list(dataframes.keys()):
        if not filtros[nombre]:
            del(dataframes[nombre])
    #Filtro por fechas
    for nombre, dataframe in dataframes.items():
        dataframes[nombre] = dataframes[nombre][
            (dataframe.index <= end)  & (dataframe.index >= start)
        ]     

    i = 0 
    n = len(dataframes.items())

    fig = Figure(figsize=(12, n+8))
    for nombre, dataframe in dataframes.items():      
        if i==0:                
            ax = fig.add_subplot(n, 1, i+1)
            first_ax = ax
        else:
            ax = fig.add_subplot(n, 1, i+1, sharex=first_ax)      
      
      # Para cada tipo de filtro, el tipo de gráfico puede variar.
  
        if (nombre == 'productivity'):            
            graficar_productividad(ax,dataframe,filtros)            
          
        elif(nombre == 'errors'):
            graficar_errores(ax,dataframe,filtros)
           
        elif(nombre == 'modes'):
            graficar_modes(ax,dataframe,filtros)
            
        elif nombre == "programs":
            graficar_programs(ax,dataframe,filtros)    
        

        ax.set_ylabel(nombre)         
        #Solo el último gráfico tiene xtick
        if i < n - 1:
            ax.tick_params(labelbottom=False)
        i+=1
    print("Figura creada")
    fig.subplots_adjust(bottom=0.3) 
    return fig



def graficar_productividad(ax,dataframe, filtros):
    print('graficando productividad')
    if filtros['time_filter'] == 'hora':
        status_dict = dict()
        i = 0
        while i < len(dataframe.index):
            row = dataframe.iloc[i]
            if row["name"] not in status_dict.keys():                
                status_dict[row["name"]] = list([(dataframe.index[i], row["duration"])])
            else:
                status_dict[row["name"]].append((dataframe.index[i],row["duration"]))
            i +=1
        
        i = 0
        for programa, actividad in status_dict.items():
            color_hex = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            ax.broken_barh( actividad,(i-0.5,1), color=color_hex)
            ax.set_yticks(range(len(status_dict.keys())), labels = status_dict.keys())            
            i += 1
    else:
        dataframe = agrupar_productividad(dataframe, filtros)
        graficar_filtrado(ax,dataframe) 

def graficar_filtrado(ax,dataframe):

    # Eje X: días
    fechas = dataframe.index.date.astype(str)
    x = np.arange(len(fechas))  # posiciones de cada grupo
    # Ancho de cada barra individual
    width = 0.5
    # Columnas a graficar
    flags = dataframe.columns
    #Para cada estado, desplazamos las barras
    for i, flag in enumerate(flags):
        #ax.bar(x + i * width, dataframe[flag]/3600, width=width, label=flag)
        ax.bar(x+i*width/5 , dataframe[flag]/3600, width=width, label=flag)
    
    # 🔸 Ahora calculás los puntos intermedios entre los días
    puntos_medios = (x[:-1] + x[1:])/2+width/5   # entre 0 y 1 → 0.5, entre 1 y 2 → 1.5, etc.

    # 🔸 Dibujás líneas punteadas verticales
    for punto in puntos_medios:
        ax.axvline(x=punto, linestyle='--', color='gray', alpha=0.5)
    # Seteo del eje X
    ax.set_xticks(x + width/5 * (len(flags) - 1) / 2)
    ax.set_xticklabels(fechas, rotation=90)        
    ax.set_xlabel('Fecha')       
    ax.legend()
    #ax.grid(True)



def graficar_errores(ax,dataframe, filtros):
    print('graficando errores')
    if filtros["time_filter"] == "hora":
        ax.eventplot(dataframe.index)
    else:
        dataframe = agrupar_errores(dataframe, filtros)
       
        fechas = dataframe.index.date.astype(str)
        x = np.arange(len(fechas))  # posiciones de cada grupo
        # Ancho de cada barra individual
        width = 0.5
          
        puntos_medios = (x[:-1] + x[1:])/2
        ax.bar(x, dataframe["message"], width=width, label="Errors")
        for punto in puntos_medios:
            ax.axvline(x=punto, linestyle='--', color='gray', alpha=0.5)

        ax.set_xticks(x / 2)
        ax.set_xticklabels(fechas, rotation=90)        
        ax.set_xlabel('Fecha')       
        ax.legend()
        #ax.grid(True)

def graficar_modes(ax,dataframe,filtros):
    print('graficando productividad')
    if filtros['time_filter'] == 'hora':            

        status_dict = dict()
        i = 0
        while i < len(dataframe.index):
            row = dataframe.iloc[i]
            if row["name"] not in status_dict.keys():
                #status_dict[row["status"]] = list([(row["start"], row["duration"])])
                status_dict[row["name"]] = list([(dataframe.index[i], row["duration"])])
            else:                   
                #status_dict[row["status"]].append((row["start"],row["duration"]))
                status_dict[row["name"]].append((dataframe.index[i],row["duration"]))
            i +=1
        
        i = 0
        for programa, actividad in status_dict.items():
            color_hex = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            ax.broken_barh( actividad,(i-0.5,1), color=color_hex)
            ax.set_yticks(range(len(status_dict.keys())), labels = status_dict.keys())            
            i += 1

    else:
        dataframe = agrupar_productividad(dataframe, filtros)                                 
        graficar_filtrado(ax,dataframe)

def graficar_programs(ax,dataframe,filtros):  
    print('graficando programas')
    "llega una secuencia del tipo: (start, nombre, duración)"  
    if filtros["time_filter"] == "hora":
        programs_dict = dict()
        i = 0
        while i < len(dataframe.index):
            row = dataframe.iloc[i]
            if row["name"] not in programs_dict.keys():
                programs_dict[row["name"]] = list([(row["start"], row["duration"])])
            else:                   
                programs_dict[row["name"]].append((row["start"],row["duration"]))
            i +=1
        
        i = 0
        for programa,actividad in programs_dict.items():
            color_hex = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            ax.broken_barh(actividad,(i-0.5,1), color=color_hex)
            ax.set_yticks(range(len(programs_dict.keys())), labels =programs_dict.keys())            
            i += 1
    else:
        dataframe = agrupar_productividad(dataframe, filtros)
        graficar_filtrado(ax,dataframe)

