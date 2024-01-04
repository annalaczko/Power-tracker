import requests
import re
import pandas as pd
from datetime import datetime
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

# DataFrame mentése
df.to_csv(file_name, index=False)

# Grafikon készítése
fig = px.line(df, x='date', y=['in', 'out'], title='Energiafogyasztás időbeli alakulása')
graph = 'energy_consuption_graph.html'
fig.write_html(graph)

# Grafikon megnyitása
webbrowser.open_new_tab(graph)

# Várakozás felhasználói inputra a kilépéshez
input("Nyomj Enter-t a kilepeshez...")
