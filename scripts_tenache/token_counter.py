import tiktoken

# def num_tokens_from_string(string: str, encoding_name: str) -> int:
#     """Returns the number of tokens in a text string."""
#     encoding = tiktoken.get_encoding(encoding_name)
#     num_tokens = len(encoding.encode(string))
#     print(f"number of tokens is {num_tokens}")
#     return num_tokens
import sqlite3
import os

table='Horarios'
database_folder = os.path.join("\\","Users","tenache89", "Desktop","llama.cpp","build","bin","Release","scripts")
info_data_name = 'info.db'
info_data_path = os.path.join(database_folder, info_data_name)
with sqlite3.connect(info_data_path) as conn:
    c = conn.cursor()
    c.execute(f'''SELECT * FROM {table}''')
    all_info = c.fetchall()
    column_names = [description[0] for description in c.description]
    info = all_info[0]
    print(info)

# if __name__ == "__main__":
#     num_tokens_from_string(string='De acuerdo a la información que tengo disponible y no habiendo mención específica sobre horarios o actividades relacionadas con tu profesión como biologo, no puedo proporcionarle una respuesta precisa sobre su disponibilidad en ese día en particular. Sin embargo,',encoding_name="cl100k_base")