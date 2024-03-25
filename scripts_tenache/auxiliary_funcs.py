import pandas as pd
import sqlite3
from datetime import timedelta
import json
import random as rr
from datetime import datetime
import llama_cpp

MAX_TOKENS = 3000
def thomaschain(answer_dict, all_user_messages_grouped,all_ai_messages,config_messages, \
                table, columnas, informacion, STRINGS, info_data_path, model, consts, message_info, \
                    extra_info_tables={'Servicios_programados':{"columnas":"Domicilio ,Horario_ser","conditions":"telefono_cliente=?"}}):
    TELEFONO = consts['TELEFONO']
    WHATSAPP = consts['WHATSAPP']
    CELULAR = consts['CELULAR']

    if not answer_dict.get("puedo_ayudar", False):
    # if AI thinks it cannot help: 
        if answer_dict.get("es_saludo", False):
            chat_completion = config_messages['automatic_more_info']
        else: 
            chat_completion = config_messages['automatic_no_info']
        
    elif table:
    # it AI thinks it can help and it chose a table
        if table in extra_info_tables:
        # if AI thinks it can help and it chose a table and it thinks it's answering a question and the table is in the ones with extra_info (further queries required). 
            informacion, columnas = get_info_for_ai(info_data_path, table,columns=extra_info_tables[table]["columnas"], \
                                                    conditions=[extra_info_tables[table]["conditions"]],variables=(message_info[1],))
            config_messages['messages_info'][0]['content'] = config_messages['messages_info'][0]['content'].format(table=table,columnas=columnas,informacion=informacion)
            messages_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_info'])
            chat_completion = model.create_chat_completion(
                messages=messages_info,
                temperature=0,
                max_tokens=MAX_TOKENS
            )
            chat_completion = chat_completion['choices'][0]['message']['content'].strip() 
            if not informacion or not columnas:
                chat_completion = f"Hubo algun problema. Por favor, comunicate con un humano al\n numero de telefono:\
                    {TELEFONO}\n whatsapp:{WHATSAPP}\n, o celular {CELULAR}"
                
        elif answer_dict["es_duda?"]:
        # if AI thinks it can help and it chose a table and table doesn't require further queries, but AI thinks its answering a question.  
            config_messages['messages_info'][0]['content'] = \
                config_messages['messages_info'][0]['content'].format(table=table,columnas=columnas,informacion=informacion)
            messages_info = complete_messages(all_user_messages_grouped, all_ai_messages,config_messages['messages_info'])
            chat_completion = model.create_chat_completion(
            messages = messages_info,
            temperature = 0,
            max_tokens=MAX_TOKENS
        )['choices'][0]['message']['content'].strip()
        
        else:
        # AI thinks it can help and it chose a table, but AI doesn't think it's a question: try to inquire more about the question. 
            chat_completion = config_messages['automatic_more_info'] 
        # else:
        #     chat_completion = f"Hubo algun problema. Por favor, comunicate con un humano al\n numero de telefono:\
        #             {TELEFONO}\n whatsapp:{WHATSAPP}\n, o celular {CELULAR}"       

    elif not answer_dict.get('es_duda?', False):
    # if AI thinks it can help, but there is no table selected, and AI thinks its NOT answering a question. 
        chat_completion = config_messages['automatic_more_info']
    
    # elif answer_dict.get('puedo_ayudar', False):
    #     chat_completion = config_messages['automatic_no_info']
    else:
    # if AI thinks it can heelp, but there is no table selected, and AI thinks its answering a question. 
        chat_completion = config_messages['automatic_more_info']    
    
    chat_completion = check_chat_completion(chat_completion, STRINGS)
    return chat_completion

def get_rid_old_messages(all_user_messages_grouped, all_ai_messages,model_path, config_messages):
    all_strings = ""
    for message in all_user_messages_grouped:
        all_strings += message
    for ai_message in all_ai_messages:
        all_strings += ai_message[-1]

    all_strings += config_messages['messages0'][0]['content']



    first_model = llama_cpp.Llama(
        model_path=model_path,
        chat_format="llama-2",
        verbose=False,
        n_ctx=2000
    )

    tokens = first_model.tokenize(all_strings.encode('utf-8'))
    ######### EXHAUSTED CODING OVER
    n_ctx = len(tokens) + 256
    print(f"Total tokens is {len(tokens)}")
    if len(tokens) > 800:
        all_user_messages_grouped.pop(0)
        all_ai_messages.pop(0)
    
    return n_ctx, all_ai_messages, all_user_messages_grouped

def get_messages_format(database_path, TABLE, WAIT_TIME):
    all_user_messages, all_ai_messages, all_user_times, all_ai_times, message_info = extract_from_database(database_path, TABLE, WAIT_TIME)

    all_ai_messages, all_ai_times, all_user_times, database_path = check_extra_ai_message(all_ai_messages, all_ai_times, all_user_times, database_path)
            
    all_user_times, all_ai_times = transform_to_datetime(all_user_times, all_ai_times)

    all_user_messages_grouped = group_user_messages(all_user_messages, all_ai_times, all_user_times)
    return all_user_messages, all_ai_messages, all_user_times, all_ai_times, all_ai_messages, all_ai_times, all_user_messages_grouped, message_info

def check_chat_completion(chat_completion, strings):
    index_inst = -1
    
    for string in strings:
        index_inst = chat_completion.find(string)
        if index_inst != -1:
            index_inst2 = chat_completion[index_inst+len(string):].find(string)
            if index_inst2 != -1:
                chat_completion = chat_completion[index_inst+len(string):index_inst2+index_inst+len(string)]
            else:
                chat_completion = chat_completion[:index_inst]
        
          
        # if index_inst != -1:
        #     chat_completion = chat_completion[index_inst+len(string):]
        # index_inst2 = chat_completion.find(string)
        # if index_inst2 != -1:
        #     chat_completion = chat_completion[:index_inst2]

    # if index_inst != -1:
    #     chat_completion = chat_completion[index_inst+7:]
    #     index_inst = chat_completion.find("<<ASSISTANT>>")    
    # if index_inst != -1:
    #     chat_completion = chat_completion[index_inst+7:]
    #     index_inst = chat_completion.find("<</ASSISTANT>>")   
    # if index_inst != -1:
    #     chat_completion = chat_completion[:index_inst]
    # index_inst = chat_completion.find("\n")
    # if index_inst != -1:
    #     chat_completion = chat_completion[:index_inst]
    return chat_completion


def check_correct_dict(answer_dict, correct_keys):
    new_dict = answer_dict.copy()
    for key in answer_dict:
        if type(answer_dict[key]) == str:
            comma_index = -1
            comma_index  = answer_dict[key].find(",")
            while comma_index != -1:
                new_dict[key] = new_dict[key][comma_index+1:]
                comma_index = new_dict[key].find(",")
            new_dict[key] = new_dict[key].strip()
        if key not in correct_keys:
            del new_dict[key]
        
    for c_key in correct_keys:
        if c_key not in new_dict:
            new_dict[c_key] = None
    return new_dict



def check_extra_ai_message(all_ai_messages, all_ai_times, all_user_times, database_path):

    if all_ai_times:
        if datetime.strptime((all_ai_times[0][-1]),"%Y-%m-%d %H:%M:%S") - datetime.strptime((all_user_times[0][-1]),"%Y-%m-%d %H:%M:%S") > timedelta(days=0):
            last_ai_message = all_ai_messages.pop(0)
            last_ai_time = all_ai_times.pop(0)
            with sqlite3.connect(database_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM messages WHERE content = ? AND created_at = ?",(last_ai_message[5],last_ai_time[0]))
    return  all_ai_messages, all_ai_times, all_user_times, database_path


# PROBABLY WILL NEED TO DEBUG THIS AT SOME POINT. LEAVING SOME DEBUGGING POINTS JUST IN CASE
def extract_json_from_string_simple(s):
    new_string = s.replace("False","false")
    new_string = new_string.replace("«", "\"")
    new_string = new_string.replace("»", "\"")
    new_string = new_string.replace("True","true")
    new_string = new_string.replace("None","null")
    start = s.find('{')  # Find the first occurrence of '{'
    end = s.rfind('}')   # Find the last occurrence of '}'
    if start != -1 and end != -1:
        new_string = new_string[start:end+1]  # Extract and return the JSON substring
    else:
        start = new_string.find("[")
        end = new_string.rfind("]")
        if start != -1 and end != -1:
          new_string = new_string[start:end+1]
          new_string = new_string.replace("[","{")
          new_string = new_string.replace("]","}")
        else:
            new_string = "{" + new_string + "}"  
    return new_string 


def extract_json_from_string(new_string, model, messages_json, correct_keys, strings):
    new_string =  check_chat_completion(new_string, strings)
    new_string = extract_json_from_string_simple(new_string)
    for _ in range(2):
        try:
            json_dict = json.loads(new_string)
            json_dict = check_correct_dict(json_dict, correct_keys)

            return json_dict
        except json.JSONDecodeError as err:
            print(f"Error loading json from response string: \n{err}")
            print(f"The string is now is {new_string}")
            print(f"trying to extract from json")
            new_string = model.create_chat_completion(
                messages = messages_json,
                temperature=0,
                max_tokens=100
            )['choices'][0]['message']['content'].strip()
            print(f"new string after AI is {new_string}")
            extract_json_from_string_simple(new_string)
            json_dict = {}
    return json_dict

def extract_from_database(database_path, table, wait_time):
    with sqlite3.connect (database_path) as conn:
        c = conn.cursor()
        c.execute(f'''SELECT * FROM {table} WHERE from_user=1 ORDER BY created_at DESC LIMIT 1''')
        message_info = c.fetchall()[0]
        user_id = message_info[1]
        # time_stamp = datetime.strptime(info[-1], '%Y-%m-%d %H:%M:%S')
        time_stamp = message_info[-1]
        query_user = f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=1 ORDER BY created_at DESC;'''
        c.execute(query_user, (user_id,))
        all_user_messages = c.fetchall()
        query_times_user = f'''SELECT created_at FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=1 ORDER BY created_at DESC;'''
        c.execute(query_times_user, (user_id,))
        all_user_times = c.fetchall()
        query_ai = f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=0 ORDER BY created_at DESC;'''
        c.execute(query_ai, (user_id,))
        all_ai_messages = c.fetchall()
        query_times_ai = f'''SELECT created_at FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=0 ORDER BY created_at DESC;'''
        c.execute(query_times_ai, (user_id,))
        all_ai_times = c.fetchall()
        # info = c.fetchall()[0]
        return all_user_messages, all_ai_messages, all_user_times, all_ai_times, message_info
  
def transform_to_datetime(all_user_times, all_ai_times):
    if all_user_times:
        all_user_times = pd.to_datetime([t[0] for t in all_user_times])
    else:
        all_user_times = pd.to_datetime([])
    if all_ai_times:
        all_ai_times = pd.to_datetime([t[0] for t in all_ai_times])
    return all_user_times, all_ai_times

def group_user_messages(all_user_messages, all_ai_times, all_user_times):
    all_user_messages = pd.Series(all_user_messages)
    all_user_messages_grouped = []
    next_start = 0
        
    for i in range(len(all_ai_times)):
        index = all_user_times - all_ai_times[i] > timedelta(days=0)
        messages_now = all_user_messages[next_start:][index[next_start:]]
        next_start = len(messages_now)
        for j in range(messages_now.shape[0]):
            user_messages_grouped = messages_now.iloc[j][-1]
        all_user_messages_grouped.append(user_messages_grouped)
    if not all_user_messages_grouped:
        all_user_messages_grouped.append(all_user_messages[0][-1])
    return all_user_messages_grouped
    
def complete_messages(all_user_messages_grouped, all_ai_messages, messages):
    for i in range(len(all_user_messages_grouped)-1,-1,-1):
        try:
            messages.append({
                "role":"assistant",
                "content":all_ai_messages[i][5]
            })
        except IndexError as err:
            print(f"Expected error in complete message: \n{err}")

        messages.append({
            "role":"user",
            "content":all_user_messages_grouped[i]
        })

    return messages
        
def get_info_for_ai(info_data_path, table, columns=None, conditions=None, variables=None):
    if not columns:
        columns = '*'
    with sqlite3.connect(info_data_path) as conn:
        c = conn.cursor()
        query = f'''SELECT {columns} FROM {table}'''
        if conditions:
            query += f" WHERE {conditions[0]}"
            for condition in conditions[1:]:
                query += f" and {condition}"
        if variables:
            try:
                c.execute(query, variables)
            except sqlite3.OperationalError as err:
                print(err)
                print(f"query is {query}")
                print("Most likely error was a mistake in table name from ai")
                return None, None
        else:
            try:
                c.execute(query)
            except sqlite3.OperationalError as err:
                print(f"query is {query}")
                print(err)
                print("Most likely error was a mistake in table name from ai")
                return None, None
        all_info = c.fetchall()
    column_names = [description[0] for description in c.description]
    info = all_info[0]

    columnas = column_names[0]
    for column in column_names[1:]:
        columnas += "," + column
    informacion = str(all_info[0])

    for info in all_info[1:]:
        informacion += "\n" + str(info)
    return informacion, columnas

def insert_into_database(values, database_path):
    with sqlite3.connect(database_path) as conn:
        c = conn.cursor()
        for _ in range(10):
            try:
                c.execute(f'''INSERT INTO messages (id, user_id, user_name, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?, ?);''', values)
                break
            except:
                new_id = values[0]  + "_" + str(rr.randint(0,10))
                values=(new_id,values[1],values[1],values[2],values[3],values[4],values[5])

def cut_ai_messages(all_ai_messages,key_strings, config_messages):
    for i, ai_message in enumerate(all_ai_messages):
        for key_string in key_strings:
            index = ai_message[-1].find(key_string)
            if index != -1:
                all_ai_messages[i] = all_ai_messages[i][:-1] + (key_strings.get(key_string, config_messages['more_info_replace']),)
    return all_ai_messages


