from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import uvicorn
import sqlite3

# with sqlite3.connect(database_path) as conn:
#     c = conn.cursor()
#     c.execute("DELETE FROM messages WHERE content = ? AND created_at = ?",(last_ai_message[5],last_ai_time[0]))
def create_sql_tables(tables_info, database_name):
    for table_id, table_info in tables_info.items():
        create_table= f"""CREATE TABLE IF NOT EXISTS {table_info['name']} (
        id integer PRIMARY KEY, 
        );
"""
        for column_key, column in table_info.items():
            create_table += f"{column['name']} TEXT,"
        create_table += ";"
        with sqlite3.connect(database_name) as conn:
            c = conn.cursor()
            c.execute(create_table)
            
            for column_key, column in table_info.items():
                question_marks = "?" * len(column) + ")"

                insert_info = f"INSERT INTO {table_info['name']} (column) values (" 
                
                # for info in column['info'][:-1]:
                #     insert_info += info + ","
                # insert_info += column['info'][-1] + ")"
                values = tuple(column)
                c.execute(insert_info, values)


    # with sqlite3.connect(database_name) as conn:
    #     c = conn.cursor()


app = FastAPI()
templates = Jinja2Templates(directory="scripts_tenache/templates")
@app.get("/submit_tables")
async def submit_tables(request: Request):
    return templates.TemplateResponse("form.html", {"request":request})

@app.post("/create_tables")
async def create_tables(request: Request):
    form_data = await request.form()
    tables_info = {}
    
    for key, value in form_data.items():
        if key == "nombre_de_empresa":
            database_name = value
        if key.startswith('table_'):
            key_split = key.split('_')
            table_id = key_split[1]
            if table_id not in tables_info:
                tables_info[table_id] = {}
            attr = key_split[2]
            if attr.startswith('col'):
                # TODO: this is probably all super wrong. fix
                if 'col' not in tables_info[table_id]:
                    tables_info[table_id]['col'] = []
                tables_info[table_id]['col'].append(value)
            
            if len(key_split) > 3:
                attr2 = key_split[3]
                if attr not in tables_info[table_id]:
                    tables_info[table_id][attr] = {}
                if attr2.startswith("info"):
                    if "info" not in tables_info[table_id][attr]:
                        tables_info[table_id][attr]['info'] = []
                    tables_info[table_id][attr]['info'].append(value)
                else:
                    tables_info[table_id][attr][attr2] = value 
            else:
                tables_info[table_id][attr] = value
    create_sql_tables(tables_info, database_name)

    # Process the tables_info dictionary to create tables
    return JSONResponse(content=tables_info)


# @app.get("/create_tables")
# def create_tables():
if __name__ == "__main__":
    uvicorn.run("scripts_tenache/main_app:app", host="0.0.0.0", port=8000)
