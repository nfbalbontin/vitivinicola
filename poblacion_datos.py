from entidades import * 
import pandas as pd

lotes = {}
wines = pd.read_excel('docs/vinos_1_Enviado.xlsx', sheet_name='vinos', encoding="utf-8", usecols='A:H', dtype={'Lote COD': str, 'Tipo UVA': str, 'Tn': int, 'Dia optimo cosecha': int, 'p_01': float, 'p_11': float, 'km a planta': int, '$/kg': float})
print(wines.iloc[0,0])
for row in range(wines['Lote COD'].count()): 
    lotes[wines.iloc[row, 0]] = Lote(wines.iloc[row, 0], wines.iloc[row, 1], 
                                                wines.iloc[row, 2], 
                                                wines.iloc[row, 3],
                                                wines.iloc[row, 4], 
                                                wines.iloc[row, 5], 
                                                wines.iloc[row, 6],  
                                                wines.iloc[row, 7])
print(lotes)