# ArgueTutor (Update 2022-04-05)
*Installation:*

1. Python 3.8 installieren
2. Neues Environment erzeugen und starten: 
   1. python -m venv <environment_name>
   2. <environment_name>\Scripts\activate
3. 4. Requirements installieren: 
   1. Run requirements_installer.py (Installs requirements from the script): python .\requirements_installer.py
4. Fehler in sqlalchemy file beheben:
   1. Open: example_venv/Lib/site-packages/sqlalchemy/util/compat.py
   2. Replace line 264 with: time_func = time.perf_counter()
5. Server starten: python3 ArgueTutor.py
6. Server stoppen: Strg+C

*Änderungen an dialog.yml:*
1. Änderung durchführen und speichern; Make change and save
2. Zeile #bot.storage.drop() einkommentieren; Comment in line #bot.storage.drop()
3. Server starten: python3 EvaluationBot.py; Start server: python3 EvaluationBot.py
4. Server stoppen: Strg+C; Stop server: Ctrl+C
5. Zeile bot.storage.drop() auskommentieren; Comment out line bot.storage.drop()
6. Server starten: python3 EvaluationBot.py; Start server: python3 EvaluationBot.py

*Auf Python Anywhere installieren*
1. Einloggen
2. Dateien hochladen: Dashboard -> Browse files -> Upload a new file
3. Neue Webapp erstellen: Dashboard -> All Web apps -> Add new Web app
4. Wizard benutzen
** Dateipfad angeben, in dem sich die .py Datei befindet
** Python 3.8 auswählen
5. Web app starten: Reload Button
6. Website aufrufen über Link
