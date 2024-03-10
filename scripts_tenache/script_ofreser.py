import llama_cpp
import os
import sys
# import FastAPI
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yaml
from auxiliary_funcs import get_info_for_ai, extract_json_from_string, extract_from_database, \
  transform_to_datetime, complete_messages, group_user_messages, insert_into_database,check_extra_ai_message, check_chat_completion

response_path = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp","scripts_tenache")

table = None
columnas = None
informacion = None

# HERE ARE SOME OF THE CONSTANTS WE WILL BE USING
TELEFONO = '4212368'
CELULAR = '387528693'
WHATSAPP = 'https://wa.me/5493875286093'
WAIT_TIME = "-10 minutes"
TABLE = "messages"


# HERE AER SOME OF THE PATHS WE WILL BE USING

model_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache") 
model_name = 'Turdus-trained-20-int8.gguf'
model_path = os.path.join(model_folder, model_name)
database_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache")
database_name = "whatsapp3.db"
database_path = os.path.join(database_folder,database_name)
info_data_name = 'info_ofreser_fict2.db'
info_data_path = os.path.join(database_folder, info_data_name)
config_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache")
config_name = "ofreser_config.yaml"
config_path = os.path.join(config_folder, config_name)

with open(config_path) as conf:
    config_messages = yaml.safe_load(conf)


start = datetime.now()
model = llama_cpp.Llama(
    model_path=model_path,
    chat_format="llama-2",
    verbose=False,
    n_ctx=2000
)

posta1 = datetime.now()
print(f"it took {posta1-start} to fire up the model")

all_user_messages, all_ai_messages, all_user_times, all_ai_times, message_info = extract_from_database(database_path, TABLE, WAIT_TIME)

all_ai_messages, all_ai_times, all_user_times, database_path = check_extra_ai_message(all_ai_messages, all_ai_times, all_user_times, database_path)
        

all_user_times, all_ai_times = transform_to_datetime(all_user_times, all_ai_times)

all_user_messages_grouped = group_user_messages(all_user_messages, all_ai_times, all_user_times)
# Tengo que cambiar esto por user_ai_user_ai  . . . . 





# messages0 =[
#   {
#     "role": "system",
#     "content": """
#     Eres el asistente de la compañía O.FRE.SER - Gestión Integral de Plagas. 
#     Interactuaras con un cliente que recibirá un servicio de de control de plagas. 
#     Dispones de las siguientes categorias de información:
#     * Servicios_programados:Tienes informacion sobre el domicilio y el horario del servicio. 
#     * Horario_pub :Horarios de atención al público.
#     * Contactos: telefonos de contacto.
      
#     Tu tarea es  determinar si puedes ayudarlos o no a partir de la informacion que tienes. 
#     Debes determinar si puedes ayudar con la pregunta, cual de las categorias responderia la pregunta, y si se requieren preguntas adicionales
#     Debes responder en format json, con las claves:
#     es_duda?: donde el valor sera un booleano (true o false). Esto sera verdadero si el usuario no hizo una pregunta concreta. 
#     puedo_ayudar: donde el valor sera un booleano: true o false. Si el valor de es_duda?? es false, puedo_ayudar tambien debe
#     informacion_requerida: Responde con UNA SOLA categoria de informacion que piensas que ayudara a responder la duda del cliente 
#     entre las mencionadas anteriormente. 
#     Responde solo el objeto JSON, en el siguiente formato. 
#     {"es_duda??":bool, "puedo_ayudar":bool,"informacion_requerida":str}
#     """  
#     }
# ]



# messages_no_info = [
#   {
#     "role":"system",
#     "content":f"""
#     Eres el asistente de 'O.FRE.SER - Gestión Integral de Plagas.
#     Debes responder de manera amable a un cliente. 
#     Debes explicarle a la persona que no tienes la informacion requerida para ayudar a la persona. 
#     Pasales la siguiente informacion de contacto
#     Telefono: {TELEFONO}. 
#     Celular: {CELULAR}
#     Whatsapp: {WHATSAPP}
#     Donde sera atendido por un empleado de la empresa. 
#     Contesta en menos de 50 palabras. 
#     Recuerda que como IA, debes ser amable con el usuario siempre. 
#     Empieza con 'Soy la IA de 'O.FRE.SER - Gestión Integral de Plagas' 
#     """
#   }
# ]

# messages_more_info = [
#   {
#     "role":"system",
#     "content":f"""
#     Eres el asistente de O.FRE.SER - Gestión Integral de Plagas.
#     Debes responder de manera amable a una persona que quiere información. 
#     Todavía no sabes cual es la pregunta del usuario, y tu tarea es determinarla. 
#     Esta es la informacion que hay disponible: 
#     * Domicilio: Domicilio donde se realizará el servicio, según la información de la empresa.
#     * Horario_ser : Horario programado del servicio.
#     * Atencion_pub : Horarios de atención al público.
#     * Tels: telefonos de contacto.
#     Los nombres 'Horarios_ser' y 'Atencion_pub' son referencias internas que no deben ser mencionadas al publico. 

#     Haz mas preguntas para determinar si puedes ayudar con la informacion que tienes.
#     Empieza con: 'Soy la IA de O.FRE.SER - Gestión Integral de Plagas' 
#     """
#   }
# ]




messages0 = config_messages['messages0']
messages0_ = complete_messages(all_user_messages_grouped, all_ai_messages, messages0)

# This part determines if the AI thinks it can help or not. 
# Returns a JSON Object


chat_completion0 = model.create_chat_completion(
  messages= messages0_,
  temperature=0,
  stop=["."],
  max_tokens=70, 
  response_format={"type":"json_object"}
)['choices'][0]['message']['content'].strip()

posta2 = datetime.now()
print(f"It took about {posta2 - posta1} to complete the first response")

# messages_json = [
#   {
#     "role":"system",
#     "content":"""Tu funcion es devolver un objeto JSON a partir de los datos que se te brindaran.
#    El objeto JSON debe tener la siguiente estructura:
#    {"es_duda??":bool, "puedo_ayudar":bool,"informacion_requerida":str}
#    Algunos ejemplos :
#    {"es_duda??":true,"puedo_ayudar":true,"informacion_requerida":Horarios}
#    {"es_duda??":false,"puedo_ayudar":false,"informacion_requerida":null}
#    {"es_duda??":true,"puedo_ayudar":false,"informacion_requerida":null}
#    {"es_duda??":false,"puedo_ayudar":true,"informacion_requerida":null}
#    {"es_duda??":true,"puedo_ayudar":true,"informacion_requerida":Gustos}
#    Recuerda hacerlo a partir de la informacion que te brinde el usuario
#    """
#    },
#   {
#     "role":"user",
#     "content":f"{chat_completion0}"
#   }
# ]
correct_keys = {"es_duda?","puedo_ayudar", "informacion_requerida"}
messages_json = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_json'])
answer_dict = extract_json_from_string(chat_completion0, model, messages_json, correct_keys)

print(f"This JSON will be passed on to the next AI: {answer_dict}")

if answer_dict:
    table = answer_dict['informacion_requerida']
if table:
    informacion, columnas = get_info_for_ai(info_data_path, table)
    
# messages_info = [
#   {
#     "role":"system",
#     "content":f"""
#     Eres el asistente de O.FRE.SER - Gestión Integral de Plagas.
#     Debes responder de manera amable a una persona que quiere saber de la empresa. 
#     Para responder a la pregunta, tendras la siguiente informacion:
#     Debes responder con la siguiente informacion. Estas respondiendo sobre
#     {table}
#     Informacion requerida (tienes columnas mas informacion):
#     {columnas}
#     {informacion}
#     Contesta en menos de 50 palabras. 
#     Empieza con Soy la IA de O.FRE.SER - Gestión Integral de Plagas
#     """
#     }
# ]

posta3 = datetime.now()



print(f"The second completion is underway")

if not answer_dict["puedo_ayudar"]:
    messages_no_info = complete_messages(all_user_messages_grouped, all_ai_messages, config_messages['messages_no_info'])
    chat_completion = model.create_chat_completion(
        messages = messages_no_info,
        temperature=0.25,
        max_tokens=5000
  )['choices'][0]['message']['content'].strip()         
elif table:
    if table == "Horarios_ser" and answer_dict["es_duda?"]:
        informacion, columnas = get_info_for_ai(info_data_path, table,columns="Domicilio, Horario_ser", conditions="telefono_cliente=?",variables=(message_info[1]))
        config_messages['messages_info'][0]['content'] = config_messages['messages_info'][0]['content'].format(table=table,columnas=columnas,informacion=informacion)
        messages_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_info'])
        chat_completion = model.create_chat_completion(
            messages=message_info,
            temperature=0,
            max_tokens=5000
        )['choices'][0]['message']['content'].strip() 
        if not informacion or not columnas:
            chat_completion = f"Hubo algun problema. Por favor, comunicate con un humano al\n numero de telefono:\
                {TELEFONO}\n whatsapp:{WHATSAPP}\n, o celular {CELULAR}"
    elif answer_dict["es_duda?"] and answer_dict["puedo_ayudar"]:
        config_messages['messages_info'][0]['content'] = config_messages['messages_info'][0]['content'].format(table=table,columnas=columnas,informacion=informacion)
        messages_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_info'])
        chat_completion = model.create_chat_completion(
        messages = messages_info,
        temperature = 0,
        max_tokens=5000
    )['choices'][0]['message']['content'].strip()
    
    elif answer_dict["puedo_ayudar"] and not answer_dict["es_duda?"]:
        messages_more_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_more_info'])
        chat_completion = model.create_chat_completion(
        messages = messages_more_info,
        temperature=0,
        max_tokens=5000)
        chat_completion = chat_completion['choices'][0]['message']['content'].strip() 
    else:
        chat_completion = f"Hubo algun problema. Por favor, comunicate con un humano al\n numero de telefono:\
                {TELEFONO}\n whatsapp:{WHATSAPP}\n, o celular {CELULAR}"       

elif not answer_dict.get('es_duda?', False):
    messages_more_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_more_info'])
    chat_completion = model.create_chat_completion(
    messages = messages_more_info,
    temperature=0.25,
    max_tokens=5000
  )
    chat_completion = chat_completion['choices'][0]['message']['content'].strip()
  
else:
  messages_no_info = complete_messages(all_user_messages_grouped, all_ai_messages, config_messages['messages_no_info'])
  chat_completion = model.create_chat_completion(
    messages = messages_no_info,
    temperature=0.25,
    max_tokens=5000
  )
  chat_completion = chat_completion['choices'][0]['message']['content'].strip()

message_id = message_info[0] + "_ai"

chat_completion = check_chat_completion(chat_completion)

print(f"The AI responded: \n{chat_completion}")
# print(f"response is {response}")

values = (message_id,message_info[1],message_info[2],0,1,chat_completion)

insert_into_database(values, database_path)


print(f"The whole process took {datetime.now()-start}")
  


















    
