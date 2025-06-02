from matplotlib.figure import Figure
from analisis import crear_dataframes
import matplotlib.dates as mdates
import pandas as pd
import random

max_xticks = 5

def crear_graficos(dfs, filtros):

    start = pd.to_datetime(filtros['tiempo_inicial'])
    end = pd.to_datetime(filtros['tiempo_final']) 

    print("Creando figura")
    fig = Figure(figsize=(12,6))
    #crear_dataframes devuelve un diccionario con el nombre del dataframe como clave, y el 
    #propio df como valor. 
    #dataframes = crear_dataframes(filtros)
    dataframes = dfs.copy()     
    i = 0 
    n = len(dataframes.items())

    for nombre in list(dataframes.keys()):
        if not filtros[nombre]:
            del(dataframes[nombre])
    for nombre, dataframe in dataframes.items():
        dataframes[nombre] = dataframes[nombre][
            (dataframe.index <= end)  & (dataframe.index >= start)
        ]     

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
     
    return fig



def graficar_productividad(ax,dataframe, filtros):
    print('graficando productividad')
    if filtros['time_filter'] == 'hora':
        status_dict = dict()
        i = 0
        while i < len(dataframe.index):
            row = dataframe.iloc[i]
            if row["status"] not in status_dict.keys():
                #status_dict[row["status"]] = list([(row["start"], row["duration"])])
                status_dict[row["status"]] = list([(dataframe.index[i], row["duration"])])
            else:                   
                #status_dict[row["status"]].append((row["start"],row["duration"]))
                status_dict[row["status"]].append((dataframe.index[i],row["duration"]))
            i +=1
        
        i = 0
        for programa, actividad in status_dict.items():
            color_hex = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            ax.broken_barh( actividad,(i-0.5,1), color=color_hex)
            ax.set_yticks(range(len(status_dict.keys())), labels = status_dict.keys())            
            i += 1

    # else:                                 
    #     bars=ax.bar(dataframe.index, dataframe["tiempo"]/3600 )
    #     if len(dataframe.index)<= max_xticks:
    #         ax.bar_label(bars, fmt="%.1f", padding=3)
    elif filtros["time_filter"] == "diario":
        import numpy as np

        # Eje X: días
        
        fechas = dataframe.index.date.astype(str)
        x = np.arange(len(fechas))  # posiciones de cada grupo

        # Ancho de cada barra individual
        width = 0.25

        # Columnas a graficar
        flags = dataframe.columns

        # Para cada estado, desplazamos las barras
        for i, flag in enumerate(flags):
            ax.bar(x + i * width, dataframe[flag]/3600, width=width, label=flag)
            

        # Seteo del eje X
        ax.set_xticks(x + width * (len(flags) - 1) / 2)
        ax.set_xticklabels(fechas, rotation=45)
        ax.set_ylabel('Duración (s)')
        ax.set_xlabel('Fecha')       
        ax.legend()
        ax.grid(True)





def graficar_errores(ax,dataframe, filtros):
    print('graficando errores')
    if filtros["time_filter"] == "hora":
        ax.eventplot(dataframe.index)
    else:
        bars = ax.bar(dataframe.index, dataframe['amount'],edgecolor='white',linewidth = 0.7)
        if len(dataframe.index)<= max_xticks:
            ax.bar_label(bars, fmt="%.1f", padding=3)           


# def graficar_modes(ax,dataframe,filtros):
#     print('graficando modos')    
#     if filtros["time_filter"] == "hora":
#         ax.step(dataframe.index, dataframe["message_mapped"], where="post")
        
#         codes=[]
#         messages=[]
#         for j in range(len(dataframe.index)):
#             code = dataframe.iloc[j]["message_mapped"]
#             message = dataframe.iloc[j]["message"]
#             if ":" in message :
#                 message = message.split(":")[1]
#             if code not in codes:
#                 codes.append(code)
#                 messages.append(message)

#         ax.set_yticks(codes)
#         ax.set_yticklabels(messages)
#     else:
#         bars = ax.bar(dataframe.index, dataframe['amount'],edgecolor='white',linewidth = 0.7, grid =True)
#         if len(dataframe.index)<= max_xticks:
#             ax.bar_label(bars, fmt="%.1f", padding=3)         

def graficar_modes(ax,dataframe,filtros):
    print('graficando productividad')
    if filtros['time_filter'] == 'hora':            

        status_dict = dict()
        i = 0
        while i < len(dataframe.index):
            row = dataframe.iloc[i]
            if row["status"] not in status_dict.keys():
                #status_dict[row["status"]] = list([(row["start"], row["duration"])])
                status_dict[row["status"]] = list([(dataframe.index[i], row["duration"])])
            else:                   
                #status_dict[row["status"]].append((row["start"],row["duration"]))
                status_dict[row["status"]].append((dataframe.index[i],row["duration"]))
            i +=1
        
        i = 0
        for programa, actividad in status_dict.items():
            color_hex = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            ax.broken_barh( actividad,(i-0.5,1), color=color_hex)
            ax.set_yticks(range(len(status_dict.keys())), labels = status_dict.keys())            
            i += 1

    else:                                 
        bars=ax.bar(dataframe.index, dataframe["tiempo"]/3600 )
        if len(dataframe.index)<= max_xticks:
            ax.bar_label(bars, fmt="%.1f", padding=3)

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




