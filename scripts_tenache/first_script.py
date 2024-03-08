import llama_cpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
import os


import sys

try:
    message = sys.argv[1]
except:
    message = "Cual es el numero?"

print(f"El mensaje de la foca es: {message}")

    
model_folder = os.path.join("\\","Users", "tenache89", "llama.cpp", "build", "bin", "Release")  
model_name = 'tinyllama-1.1b-chat-v1.0.Q2_K.gguf'
model_path = os.path.join(model_folder, model_name)
print(f"model_path is {model_path}")
# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path=model_path,
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)


template = """Question: {question}

Answer: Let's work this out in a step by step way to be sure we have the right answer."""

prompt = PromptTemplate(template=template, input_variables=["question"])
final_prompt = prompt.format(**{'question':message})
# prompt = """
# Question: A rap battle between Stephen Colbert and John Oliver
# """

my_message = llm.invoke(final_prompt)

with open('mensaje.txt','w') as file:
    file.write(my_message)