import pandas as pd

# Crear un DataFrame de ejemplo
data = {'Columna1': [1, 2, None, 4, 5],
        'Columna2': ['A', 'B', '', 'D', 'E']}
df = pd.DataFrame(data)

# Validar si una celda está en blanco (nulo o vacío)
for index, row in df.iterrows():
    if pd.isna(row['Columna1']):
        print(f'La celda en la fila {index} de Columna1 está en blanco (nula).')
    if pd.isna(row['Columna2']) or row['Columna2'] == '':
        print(f'La celda en la fila {index} de Columna2 está en blanco o vacía.')


