import requests
import re
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px
import webbrowser

# A fájl URL-je
url = 'http://192.168.100.73'

# HTTP GET kérés a fájl letöltéséhez
response = requests.get(url)
time = datetime.now()

# Ellenőrizze, hogy a kérés sikeres volt-e
if response.status_code == 200:
    file_content = response.text
else:
    print("Hiba történt a letöltés során: ", response.status_code)

# Reguláris kifejezés a kívánt adatokhoz
pattern = r'1-0:2\.8\.0\((\d+\.\d+)\*kWh\)|1-0:1\.8\.0\((\d+\.\d+)\*kWh\)'

# Keresés a szövegben
results = re.findall(pattern, file_content)

if not results:
    print('Az adott IP címen nem található megfelelő információ')

# Üres stringek figyelmen kívül hagyása és 'in' és 'out' értékek kinyerése
in_val = ""
out_val = ""
for result in results:
    if result[0]:  # 1-0:2.8.0 értékek (out)
        out_val = result[0]
    if result[1]:  # 1-0:1.8.0 értékek (in)
        in_val = result[1]

# Fájl ellenőrzése és DataFrame létrehozása vagy betöltése
file_name = 'data/data.csv'
if os.path.exists(file_name):
    df = pd.read_csv(file_name)
else:
    df = pd.DataFrame(columns=['date', 'in', 'out'])

# Új sor hozzáadása
new_line = {'date': time.strftime('%Y-%m-%d %H:%M:%S'), 'in': in_val, 'out': out_val}
df = df._append(new_line, ignore_index=True)

df['in']=df['in'].astype(float)
df['out']=df['out'].astype(float)


# Eltérések hozzáadása az előző értékekhez képest
df['in_prev'] = df['in'].shift(1).astype(float)
df['out_prev'] = df['out'].shift(1).astype(float)

df['in_diff'] = df['in']-df['in_prev']
df['out_diff'] = df['out']-df['out_prev']
df=df.fillna(0)
print(df)

# Az előző sorok dátumának kinyerése (shift metódus használata)
df['previous_date'] = df['date'].shift(1)
df['elapsed_time_since_previous'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['previous_date'])).dt.total_seconds() / 3600


df['in_per_hour']=df['in_diff']/df['elapsed_time_since_previous']
df['out_per_hour']=df['out_diff']/df['elapsed_time_since_previous']


df_val=df[['date', 'in_per_hour', 'out_per_hour']]

print(df_val)

# DataFrame mentése
df.to_csv(file_name, index=False)

# Grafikon készítése hosszú formátumú DataFrame alapján
fig = px.line(df_val, x='date', y=['out_per_hour','in_per_hour'], title='Energiafogyasztás időbeli alakulása')
graph = 'energy_consuption_graph.html'
fig.write_html(graph)

# Grafikon megnyitása
webbrowser.open_new_tab(graph)
