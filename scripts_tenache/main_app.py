import sys
import os

from make_config import make_config

from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import uvicorn
import sqlite3
import subprocess
import json
from fastapi import Response

# todo. pasar de tables_info a config.yaml
# Lets try this, ok? The idea is to generate the yaml file from the database. We can do this. I think we have to start a new python
def create_sql_tables(tables_info, database_name):
    database_name += ".db"
    for table_id, table_info in tables_info.items():
        create_table= f"""CREATE TABLE IF NOT EXISTS "{table_info['name']}" (
        id integer PRIMARY KEY
        """
        try:
            for column in table_info['cols'][:-1]:
                create_table += f""","{column['name']}" TEXT"""
            create_table += f""", "{table_info['cols'][-1]['name']}" TEXT);"""

        except IndexError:
            create_table += ");"

        with sqlite3.connect(database_name) as conn:
            c = conn.cursor()
            print(f"database_name is {database_name}")
            print(f"Create_table is :\n{create_table}")
            c.execute(create_table)
            # Do I need this line in order to actually execute the table? 

            # Step 1: Determine the maximum number of rows across all columns
            max_rows = max(len(col['info']) for col in table_info['cols'])

            # Step 2: Pad shorter columns with None (which translates to NULL in SQL)
            for col in table_info['cols']:
                col['info'] += [None] * (max_rows - len(col['info']))

            # Building the INSERT statement (as before)
            insert_info = f"""INSERT INTO "{table_info['name']}" ("""
            column_names = [f'"{col["name"]}"' for col in table_info['cols']]
            insert_info += ', '.join(column_names) + ') VALUES '
            placeholders = ', '.join(['?' for _ in range(len(table_info['cols']))])
            insert_info += f"({placeholders});"

            # Preparing the values (now straightforward since all columns are aligned)
            values = []
            for i in range(max_rows):
                row = tuple(col['info'][i] for col in table_info['cols'])
                values.append(row)

            # Debug output
            print(f"insert_info: {insert_info}")
            for value in values:
                print(f"Row values: {value}")

            # Inserting the data
            c.executemany(insert_info, values)

app = FastAPI()
templates = Jinja2Templates(directory="/home/tenache/whatsappBot2/scripts_tenache/templates")
@app.get("/submit_tables")
async def submit_tables(request: Request):
    return templates.TemplateResponse("form.html", {"request":request})

@app.post("/create_tables")
async def create_tables(request: Request):
    form_data = await request.form()
    tables_info = {}
    last_table = ""
    print(form_data)

    for key, value in form_data.items():
        if key == "nombre_de_empresa":
            database_name = value
        if key.startswith('table_'):
            key_split = key.split('_')
            table_id = key_split[1]
            if table_id != last_table:
                last_table = table_id
                last_col = ""
                
            if table_id not in tables_info:
                tables_info[table_id] = {}
                tables_info[table_id]['cols']= []
            attr = key_split[2]
            if attr.startswith('name'):
                tables_info[table_id]['name'] = value
            if attr.startswith('col'):
                if attr[3] != last_col:
                    last_col = attr[3]
                    tables_info[table_id]['cols'].append({})
            if attr.startswith('description'):
                tables_info[table_id]['description'] = value
                # print(f"hey look at meeeee!!!!!!!! tables_info[table_id]['description'] is {tables_info[table_id]['description']}")
           
            if len(key_split) > 3:
                attr2 = key_split[3]
                if attr2 == "name":
                    tables_info[table_id]['cols'][-1]['name'] = value
                elif attr2 == "type":
                    tables_info[table_id]['cols'][-1]['type'] = value
                elif attr2.startswith('info'):
                    if not tables_info[table_id]['cols'][-1].get('info'):
                        tables_info[table_id]['cols'][-1]['info'] = []
                    tables_info[table_id]['cols'][-1]['info'].append(value)
    create_sql_tables(tables_info, database_name)
    # todo: make yaml from tables_info
    # look at tables_info, how it looks, and try to apply it the the yaml. 
    # make a tables with lots of information. 
    # estoy por probar algo y estoy nervioso. 
    # its really hard to focus. My head is somewhere else. 
    # one thing: I need to run the thing and see the dictionary created. thats all. 
    informacion_disponible = ""
    for table_name, table in tables_info.items():
        informacion_disponible = f"""* {table['name']}:{table['description']}\n"""
    informacion_de_contacto = """ 
            📞   Telefono: {TELEFONO}. \n

        📱  Celular: {CELULAR}\n

        U+F618 Whatsapp: {WHATSAPP}\n
    """
    data = {
        'nombre_de_empresa': "O.FRE.SER - Gestión Integral de Plagas",
        'informacion_disponible':informacion_disponible,
        'informacion_de_contacto':informacion_de_contacto, 
    }
        
    # todo: 
    make_config(
        "config_template.yaml",
        informacion_disponible,
        informacion_de_contacto, 
        data, 
        "config_out.yaml"
    )

    # Process the tables_info dictionary to create tables
    tables_info_str = json.dumps(tables_info, indent=4, default=str)
    return Response(content=tables_info_str, media_type='application/json')

@app.get("run_node_script")
def run_node_script():
    print("this is running")
    try:
        result = subprocess.run(["node","/home/tenache/whatsappBot2/scripts_tenache/hello.js"], capture_output=True, text=True, check=True)
        return {"message": result.stdout.strip()}
    except subprocess.CalledProcessError as e: 
        return {"error":e.stderr.strip()}
# @app.get("/create_tables")
# def create_tables():
if __name__ == "__main__":
    uvicorn.run("main_app:app", host="0.0.0.0", port=8000, reload=True)
