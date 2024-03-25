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
  transform_to_datetime, complete_messages, group_user_messages, insert_into_database,\
    check_extra_ai_message, check_chat_completion, get_messages_format,\
        get_rid_old_messages

STRINGS = ["INST", "ASSISTANT","SYS"]

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

# HERE ARE SOME OF THE PATHS WE WILL BE USING

model_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache","models") 
# model_name = "mistral-7b-instruct-v0.2.Q6_K.gguf"
model_name = 'Turdus-trained-20-int8.gguf'
model_path = os.path.join(model_folder, model_name)
database_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache","databases")
database_name = "whatsapp3.db"
database_path = os.path.join(database_folder,database_name)
info_data_name = 'info_ofreser_fict2.db'
info_data_path = os.path.join(database_folder, info_data_name)
config_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache")
config_name = "ofreser_config.yaml"
config_path = os.path.join(config_folder, config_name)

with open(config_path) as conf:
    config_messages = yaml.safe_load(conf)

all_user_messages, all_ai_messages, all_user_times, all_ai_times, all_ai_messages, all_ai_times, all_user_messages_grouped, message_info = \
    get_messages_format(database_path, TABLE, WAIT_TIME)

start = datetime.now()

n_ctx, all_ai_messages, all_user_messages_grouped = get_rid_old_messages(all_user_messages_grouped, all_ai_messages,model_path, config_messages)

print(f"first model and tokenization took {datetime.now() - start}") 

model = llama_cpp.Llama(
    model_path=model_path,
    chat_format="llama-2",
    verbose=True,
    n_ctx = n_ctx
)

posta1 = datetime.now()
print(f"it took {posta1-start} to fire up the model")

# This part determines if the AI thinks it can help or not. 
# Returns a JSON Object

messages0 = config_messages['messages0']
messages0_ = complete_messages(all_user_messages_grouped, all_ai_messages, messages0)

chat_completion0 = model.create_chat_completion(
  messages= messages0_,
  temperature=0,
  stop=["."],
  max_tokens=70, 
  response_format={"type":"json_object"}
)['choices'][0]['message']['content'].strip()

posta2 = datetime.now()
print(f"It took about {posta2 - posta1} to complete the first response")


correct_keys = {"es_duda?","puedo_ayudar", "informacion_requerida"}
messages_json = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_json'])
answer_dict = extract_json_from_string(chat_completion0, model, messages_json, correct_keys, STRINGS)

print(f"This JSON will be passed on to the next AI: {answer_dict}")
print(f"This is what is trying to be answered: {all_user_messages_grouped[-1]}")

if answer_dict:
    table = answer_dict['informacion_requerida']
if table:
    informacion, columnas = get_info_for_ai(info_data_path, table)
    
posta3 = datetime.now()

print(f"The second completion is underway")

# 

if not answer_dict.get("puedo_ayudar", False):
    messages_no_info = complete_messages(all_user_messages_grouped, all_ai_messages, config_messages['messages_no_info'])
    messages_no_info[0]['content'] = messages_no_info[0]['content'].format(TELEFONO=TELEFONO, CELULAR=CELULAR,WHATSAPP=WHATSAPP)
    chat_completion = model.create_chat_completion(
        messages = messages_no_info,
        temperature=0.25,
        max_tokens=5000
  )['choices'][0]['message']['content'].strip()   
          
elif table:
    if table == "Servicios_programados" and answer_dict["es_duda?"]:
        informacion, columnas = get_info_for_ai(info_data_path, table,columns="Domicilio, Horario_ser", conditions=["telefono_cliente=?"],variables=(message_info[1],))
        config_messages['messages_info'][0]['content'] = config_messages['messages_info'][0]['content'].format(table=table,columnas=columnas,informacion=informacion)
        messages_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_info'])
        chat_completion = model.create_chat_completion(
            messages=messages_info,
            temperature=0,
            max_tokens=5000
        )
        chat_completion = chat_completion['choices'][0]['message']['content'].strip() 
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

chat_completion = check_chat_completion(chat_completion, STRINGS)

print(f"The AI responded: \n{chat_completion}")
# print(f"response is {response}")

values = (message_id,message_info[1],message_info[2],0,1,chat_completion)

insert_into_database(values, database_path)

print(f"The whole process took {datetime.now()-start}")














    
