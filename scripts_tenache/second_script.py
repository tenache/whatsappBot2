print("Up to line one, we're fine")
import llama_cpp
import os
import sys
# import FastAPI
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from auxiliary_funcs import extract_json_from_string, extract_from_database, transform_to_datetime, get_info_for_ai



print("Up to line 12, we're fine")

response_path = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp","scripts_tenache")
# response_path = r'C:\Users\tenache89\Desktop\llama.cpp\build\bin\Release\scripts\mensaje.txt'
# with open(response_path,'w') as file:
#     file.write('hola')

table = None
columnas = None
informacion = None
TELEFONO = '3875377223'
WAIT_TIME = "-5 minutes"
TABLE = "messages"
# app = FastAPI(
#     title="Chatbot server",
#     version="1.0",
#     description="A simple api server using llama's piRunnable interfaces",
# )

print("up to line 30, we're fine")
model_folder = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp", "build", "bin", "Release") 
# model_name = 'llama-2-13b-chat.Q5_K_M.gguf'
model_name = 'EVAESPANIOLBIENTurdus-trained-20-int8.gguf'
model_path = os.path.join(model_folder, model_name)
database_folder = os.path.join("\\","Users","tenache89", "Desktop","llama.cpp","scripts_tenache")
database_name = "whatsapp3.db"
database_path = os.path.join(database_folder,database_name)

print("up to line 39, we're fine")

model = llama_cpp.Llama(
    model_path=model_path,
    chat_format="llama-2",
    verbose=False,
    n_ctx=800
)

print(f"database_path is {database_path}")



all_user_messages, all_ai_messages, all_user_times, all_ai_times, message_info = extract_from_database(database_path, TABLE, WAIT_TIME)

all_user_times, all_ai_times = transform_to_datetime(all_user_times, all_ai_times)

print("up to line 76, we're fine")
all_user_messages_grouped = ""
next_start = 0

if len(all_ai_times):
  sections = len(all_ai_times)
else:
  sections = 1

all_user_messages = pd.Series(all_user_messages)


for i in range(sections):
  all_user_messages_grouped += "\n"
  index = all_user_times - all_ai_times[i] > timedelta(days=0)
  
  messages_now = all_user_messages[next_start:][index[next_start:]]
  next_start = len(messages_now)
  for j in range(messages_now.shape[0]):
    all_user_messages_grouped+= messages_now.iloc[j][-1]
    
# for message in all_user_messages:
#   all_user_messages_grouped += message[-1]
  
    

print("up to line 97 we're fine")



messages0 =[
  {
    "role": "system",
    "content": """
    Eres el asistente de Thomas. Tu tarea es interactuar con personas y determinar si puedes ayudarlos o no a partir de la informacion que tienes
    Dispones de las siguientes categorias de informacion: {Amigos, Gustos, Hobbies, Horarios, LibrosFavoritos, PeliculasFavoritas}. 
    Debes determinar si puedes ayudar con la pregunta, cual de las categorias responderia la pregunta, y si se requieren preguntas adicionales
    Debes responder en format json, con las claves:
    es_pregunta?: donde el valor sera un booleano (true o false). Esto sera verdadero si el usuario no hizo una pregunta concreta. 
        
    puedo_ayudar: donde el valor sera un booleano: true o false. Si el valor de es_pregunta? es false, puedo_ayudar tambien debe
    informacion_requerida: null si ninguna de las categorias ayudara a responder la pregunta. De lo contrario, responde con una de las categorias.        
    Responde solo el objeto JSON, en el siguiente formato. 
    {"es_pregunta?":bool, "puedo_ayudar":bool,"informacion_requerida":str}
    """  
    },
  {
    "role":"user",
    "content":all_user_messages_grouped
  }
]
print("up to line 129, we're fine")

start = datetime.now()
chat_completion0 = model.create_chat_completion(
    messages= messages0,
    temperature=0,
    stop=["."],
    max_tokens=50, 
    response_format={"type":"json_object"}
)

time_to_boot = datetime.now() - start
print(f"It took {time_to_boot} to start the model")

print(f"La LLM tomo {datetime.now() - start}")
response0_no_strip = chat_completion0['choices'][0]['message']['content']
response0 = chat_completion0['choices'][0]['message']['content'].strip()


  
response0 = extract_json_from_string(response0)

messages_json = [
  {
    "role":"system",
    "content":"""Tu funcion es devolver un objeto JSON a partir de los datos que se te brindaran.
   El objeto JSON debe tener la siguiente estructura:
   {"es_pregunta?":bool, "puedo_ayudar":bool,"informacion_requerida":str}
   Algunos ejemplos :
   {"es_pregunta?":true,"puedo_ayudar":true,"informacion_requerida":Horarios}
   {"es_pregunta?":false,"puedo_ayudar":false,"informacion_requerida":null}
   {"es_pregunta?":true,"puedo_ayudar":false,"informacion_requerida":null}
   {"es_pregunta?":false,"puedo_ayudar":true,"informacion_requerida":null}
   {"es_pregunta?":true,"puedo_ayudar":true,"informacion_requerida":Gustos}
   Recuerda hacerlo a partir de la informacion que te brinde el usuario
   """
   },
  {
    "role":"user",
    "content":f"{response0}"
  }
]


for _ in range(2):
  try:
    json_dict = json.loads(response0)
    break
  except Exception as err:
    print(err)
    print(f"response0 is {response0}")
    print(f"trying to extract from json")
    response0 = model.create_chat_completion(
      messages = messages_json,
      temperature=0.25,
      max_tokens=5000
    )['choices'][0]['message']['content'].strip()
    extract_json_from_string(response0)
    json_dict = {}

print(f"response0 is {response0}")

if json_dict:
  table = json_dict['informacion_requerida']
  
info_data_name = 'info.db'
info_data_path = os.path.join(database_folder, info_data_name)

if table: 
  informacion, columnas = get_info_for_ai(info_data_path, table)


messages_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Para responder a la pregunta, tendras la siguiente informacion:
    Debes responder con la siguiente informacion. Estas respondiendo sobre
    {table}
    Informacion requerida (tienes columnas mas informacion):
    {columnas}
    {informacion}
    Contesta en menos de 50 palabras. 
    Empieza con Soy la IA de Thomas
    """
  },
  {
    "role":"user",
    "content": all_user_messages_grouped
  }
]

messages_no_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Debes explicarle a la persona que no tienes la informacion requerida para ayudar a la persona. 
    Diles que se comuniquen al numero: {TELEFONO}. 
    Contesta en menos de 40 palabras. 
    Recuerda ser amable a toda costa. 
    Empieza con 'Soy la IA de Thomas' 
    """
  },
  {
    "role":"user",
    "content": all_user_messages_grouped
  }
]

messages_more_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Todavia no sabes cual es la pregunta del usuario, y tu tarea es determinarla. 
    Esta es la informacion que hay disponible: 
    {{Amigos, Gustos, Hobbies, Horarios, LibrosFavoritos, PeliculasFavoritas}}
    La categoria LibrosFavoritos contiene una lista de libros favoritos y sus autores. 
    La categoria PeliculasFavoritas contiene una lista de peliculas favoritas y sus directores
    Haz mas preguntas para determinar si puedes ayudar con la informacion que tienes.
    Empieza con: 'Soy la IA de Thomas' 
    """
  },
  {
    "role":"user",
    "content": all_user_messages_grouped
  }
]
  
print("The second completion is underway . . .")

start = datetime.now()

if table: 
  chat_completion = model.create_chat_completion(
    messages = messages_info,
    temperature = 0,
    max_tokens=5000
  )
elif not json_dict.get('es_pregunta?', False):
    chat_completion = model.create_chat_completion(
    messages = messages_more_info,
    temperature=0.25,
    max_tokens=5000
  )
  
else:
  chat_completion = model.create_chat_completion(
    messages = messages_no_info,
    temperature=0.25,
    max_tokens=5000
  )
  

print(f"La segunda LLM tomo {datetime.now()-start}")

response = chat_completion['choices'][0]['message']['content'].strip()
print(f"response is {response}")


#info.id, info.user_id, 0, 1, response,


# DO NOT ELIMINATE FOLLOWING LINES!!!!!!
#### THE FOLLOWING LINES INSERT THE RESPONSE INTO THE DATABASE
message_id = message_info[0] + "_ai"
# print(f"response is {response}")
values = (message_id,message_info[1],message_info[2],0,1,response)
with sqlite3.connect(database_path) as conn:
    c = conn.cursor()
    c.execute(f'''INSERT INTO messages (id, user_id, user_name, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?, ?);''', values)
## DO NOT ELIMINATE !!!!!

response_path = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp","scripts_tenache")
# response_path = r'C:\Users\tenache89\Desktop\llama.cpp\build\bin\Release\scripts\mensaje.txt'
# with open(response_path,'w') as file:
#     file.write(response)


# print(model("The quick brown fox jumps ", stop=["."])["choices"][0]["text"])
