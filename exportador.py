from analisis import crear_dataframes

def generar_reporte(filtros:dict):
        
    start = filtros['tiempo_inicial']
    end = filtros['tiempo_final']
    df = generar_dfs(start,end)
    excel_path = "rapporto completo.xlsx"
    df.to_excel(excel_path)
    print(f"✅ Reporte generado: {excel_path}")