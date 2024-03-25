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
        get_rid_old_messages, thomaschain, cut_ai_messages
import logging
# -----------------------------------------------MODELS ------------------------------------------------------
    # model_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache","models") 
    # model_name = 'Turdus-trained-20-int8WORKS.gguf'
    # model_name = 'dolphin-2.7-mixtral-8x7b.Q4_K_M.gguf'
    # model_name = 'WestLake-10.7b-v2-Q8_0.gguf'
    # model_name = "mistral-7b-instruct-v0.2.Q6_K.gguf"
    # model_name = 'LewdGem-40B.q8_0.gguf'
    # model_name = 'emerhyst-20b.Q8_0.gguf'
    # model_name = 'c4ai-command-r-v01-Q8_0.gguf'
    # model_name = 'LewdGem-40B.q8_0.gguf'
# ---------------------------------------------------------------------------------------------------------------

# TODO : HACER QUE ALGUNAS RTTAS. SEAN AUTOMATICAS, QUE NO PASEN POR LA IA
# VER QUE MAS PUEDO AGREGAR A LA DEMO, COMO PARA ARREGLAR. 

# TODO: probar mas modelos para ver si alguno es mejor, especialmente para conversaciones un poco mas largas... 

def ai_respond(
        STRINGS = ["INST", "ASSISTANT","SYS"],
        response_path = "/Users/tenache89/Desktop/llama.cpp/scripts_tenache",
        table=None,
        columnas=None,
        informacion=None,
        consts = {'TELEFONO':'4212368','CELULAR':'387528693','WHATSAPP':'https://wa.me/5493875286093'},
        WAIT_TIME = "-5 minutes",
        TABLE = "messages",
        model_folder= "/home/tenache/whatsappBot2/scripts_tenache/models",
        model_name = 'Kunoichi-DPO-v2-7B-Q8_0-imatrix.gguf',
        info_data_name = 'info_ofreser_fict2.db',
        config_folder = "/home/tenache/whatsappBot2/scripts_tenache",
        config_name = "ofreser_config.yaml",
        key_strings_keys = ['Lamentablemente, no dispongo de toda la información necesaria para ayudarlo directamente.',
        'Soy la IA de O.FRE.SER -Gestión Integral de Plagas. \nEstoy aquí para entender tus necesidades'],
        database_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache","databases"),
        database_name = "whatsapp3.db"

):

    logging.basicConfig(level=logging.DEBUG)
    response_path = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp","scripts_tenache")

    # HERE ARE SOME OF THE PATHS WE WILL BE USING

    model_path = os.path.join(model_folder, model_name)
    database_path = os.path.join(database_folder,database_name)
    info_data_path = os.path.join(database_folder, info_data_name)
    config_path = os.path.join(config_folder, config_name)

    with open(config_path) as conf:
        config_messages = yaml.safe_load(conf)

    all_user_messages, all_ai_messages, all_user_times, all_ai_times, all_ai_messages, all_ai_times, all_user_messages_grouped, message_info = \
        get_messages_format(database_path, TABLE, WAIT_TIME)

    start = datetime.now()

    n_ctx, all_ai_messages, all_user_messages_grouped = get_rid_old_messages(all_user_messages_grouped, all_ai_messages,model_path, config_messages)

    key_strings = {
        key_strings_keys[0]:config_messages['no_info_replace'],
        key_strings_keys[1]:config_messages['more_info_replace']
    }

    all_ai_messages = cut_ai_messages(all_ai_messages, key_strings, config_messages)

    logging.debug(f"first model and tokenization took {datetime.now() - start}") 

    model = llama_cpp.Llama(
        model_path=model_path,
        chat_format="llama-2",
        verbose=False,
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
    logging.debug(f"It took about {posta2 - posta1} to complete the first response")

    correct_keys = {"es_duda?","es_saludo","puedo_ayudar", "informacion_requerida"}
    messages_json = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_json'])
    answer_dict = extract_json_from_string(chat_completion0, model, messages_json, correct_keys, STRINGS)

    logging.debug(f"This JSON will be passed on to the next AI: {answer_dict}")
    logging.debug(f"This is what is trying to be answered: {all_user_messages_grouped[0]}")

    if answer_dict:
        table = answer_dict['informacion_requerida']
    if table:
        informacion, columnas = get_info_for_ai(info_data_path, table)
        
    posta3 = datetime.now()

    logging.debug(f"The second completion is underway")

    message_id = message_info[0] + "_ai"
    chat_completion = thomaschain(
        answer_dict, 
        all_user_messages_grouped,
        all_ai_messages,config_messages,
        table, 
        columnas, 
        informacion,
        STRINGS,
        info_data_path, 
        model,
        consts,
        message_info
        )

    logging.debug(f"The AI responded: \n{chat_completion}")

    values = (message_id,message_info[1],message_info[2],0,1,chat_completion)

    insert_into_database(values, database_path)

    logging.debug(f"The whole process took {datetime.now()-start}")
    
if __name__ == "__main__":
    ai_respond()
