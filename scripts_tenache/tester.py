import sqlite3
import random as rr
from script_ofreser_predeterminado import ai_respond
import os
# Th

# 3875377223_test
# user_id = str(rr.randint(100_000_000, 999_999_999)) + 'test_user'
user_id = '3875377223_test'
while True:
    content = input("\nEnter your message for AI here: \n")
    if content == "break":
        break

    # Next part is to upload it to the database
    database_folder = os.path.join("/","home","tenache","whatsappBot2","scripts_tenache","databases")
    database_name = "whatsapp3.db"
    database_path = os.path.join(database_folder,database_name)

    id = str(rr.randint(100_000_000, 999_999_999)) + rr.choice(['T','N','H'])
    user_name = 'tester01'
    from_user = 1
    from_ai = 0
    values = id, user_id, user_name, from_user, from_ai, content

    with sqlite3.connect(database_path) as conn:
        c = conn.cursor()
        for _ in range(10):
            try:
                c.execute(f'''INSERT INTO messages (id, user_id, user_name, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?, ?);''', values)
                break
            except:
                new_id = values[0]  + "_" + str(rr.randint(0,10))
                values=(new_id,values[1],values[1],values[2],values[3],values[4],values[5])
    ai_respond(debug = True)


