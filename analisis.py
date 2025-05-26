import pandas as pd
from matplotlib.figure import Figure
import os
from datetime import datetime
import openpyxl

#Se crea un diccionario con los nombres de los archivos como valor. 
CARPETA_CSV = "data"
ARCHIVOS = {
    "errors": "errors.csv",
    "modes": "modes.csv",
    "productivity": "productivity.csv",
    "programs": "programs.csv"
}

# Cargar archivos CSV con estructura (timestamp, mensaje)
def cargar_csv(nombre_archivo,start, end):
    #crea una dirección absouluta / ... /CARPETA_CSV/archivo.csv
    path = os.path.join(CARPETA_CSV, nombre_archivo)
    #Crea un df del archivo nombre_archivo y nombra los campos como timestamp y message
    df = pd.read_csv(path,header=None, names=["timestamp", "message"], on_bad_lines='skip')
    #formatea los timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    #Crea un campo 'date' con la fecha de cada timestamp. 
    df['date'] = df['timestamp'].dt.date
    df = df[(df['timestamp']>= start) & (df['timestamp'] <=end)]
    return df


def generar_dfs(start,end):
    # === ERRORES ===
    df_errors = cargar_csv(ARCHIVOS["errors"],start,end)
    errores_por_dia = df_errors.groupby('date').size().rename("Err")

    # === MODOS ===
    df_modes = cargar_csv(ARCHIVOS["modes"],start,end)
    df_aut = df_modes[df_modes["message"].str.contains("#AUT", na=False)]
    aut_por_dia = df_aut.groupby('date').size().rename("Modifiche a #AUT")

    # === PROGRAMS ===
    df_programs = cargar_csv(ARCHIVOS["programs"],start,end)
    inicios = df_programs[df_programs["message"].str.startswith("Starting program")]
    programas_por_dia = inicios.groupby('date').size().rename("Programmi avviati")

    # === PRODUCTIVIDAD ===
    df_prod = cargar_csv(ARCHIVOS["productivity"],start,end)
    df_prod = df_prod.sort_values("timestamp").reset_index(drop=True)   

    tiempos = []
    i = 0


    while i < len(df_prod): 
        row = df_prod.iloc[i]
        if "Active" in row["message"]:
            start = row["timestamp"]
            j = i + 1
            while j < len(df_prod):
                msg = df_prod.iloc[j]["message"]
                date = df_prod.iloc[j]["timestamp"].date()
                if "Active" not in msg:
                    end = df_prod.iloc[j]["timestamp"]
                    if (end.date() == start.date()):
                        tiempos.append((start.date(), (end - start).total_seconds()))                    
                    else:
                        with open ("anomalies", "a") as anomalies:
                            anomalies.write(f'Robot started at {start} and ended at {end},({round((end - start).total_seconds()/3600,2)}hours) \n so the time was splitted like this:\n')
                            end_day = pd.Timestamp.combine(start.date(),pd.Timestamp("23:59").time())                   
                            tiempos.append((start.date(), (end_day - start).total_seconds()))
                            anomalies.write(f'start = {start}, end = {end_day}, ({round((end_day - start).total_seconds()/3600,2)} hours and then: \n')
                            start_day = pd.Timestamp.combine(end.date(),pd.Timestamp("00:01").time())
                            anomalies.write(f'started again at {start_day} and ended at {end}({round((end - start_day).total_seconds()/3600,2)}hours)\n \n ')
                            tiempos.append((start_day.date(), (end - start_day).total_seconds()))
                        
                        
                    break
                j += 1
            i = j
        else:
            i += 1



    df_tiempos = pd.DataFrame(tiempos, columns=["date", "tiempo_activo_s"])
    tiempo_activo_por_dia = df_tiempos.groupby("date")["tiempo_activo_s"].sum().rename("actividad")
    # === COMBINAR TODO ===

    df_final = pd.concat([errores_por_dia, aut_por_dia, programas_por_dia, tiempo_activo_por_dia], axis=1).fillna(0)
    df_final = df_final.sort_index()
    return df_final

# === EXPORTAR ===
def generar_reporte(filtros:dict):
        
    start = filtros['tiempo_inicial']
    end = filtros['tiempo_final']
    df = generar_dfs(start,end)
    excel_path = "rapporto completo.xlsx"
    df.to_excel(excel_path)
    print(f"✅ Reporte generado: {excel_path}")

def generar_grafico(filtros: dict):
    # leer archivos, filtrar según filtros, etc.
    # hacer los gráficos en una Figure

    fig = Figure(figsize=(12, 6), dpi=100)
    ax = fig.add_subplot()
    start = filtros['tiempo_inicial']
    end = filtros['tiempo_final']

    df = generar_dfs(start,end)

    ax.plot(df)  # o lo que sea
    ax.set_title("Actividad del robot")
    ax.legend(df.columns)
    ...
    return fig
