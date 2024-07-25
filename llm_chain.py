# ====== Import Library ======
from langchain.chains import LLMChain
from langchain_community.llms import CTransformers
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
import vectordb

from operator import itemgetter
import yaml
import json
# ====== Load configuration ======
with open("db_config.yml","r") as f:
    db_config = yaml.safe_load(f)
    
with open("model_config.yml","r") as f:
    model_config = yaml.safe_load(f)
    
with open("history_config.yml","r") as f:
    history_config = yaml.safe_load(f)
    
# ====== Load Template ======
from prompt_template import memory_prompt_template, rag_prompt_template

# ====== Load llm model ======
def load_llm_model(model_path=model_config["chatbot_path"]["Q5bit"], 
                   model_type=model_config["chatbot_type"],
                   model_config=model_config["chatbot_config"]):
    llm_model = CTransformers(model=model_path, model_type=model_type, model_config=model_config)
    return llm_model

# ====== Get Prompt Template ======
def get_PromptTemplate(template):
    return PromptTemplate.from_template(template)

# ====== LLMChain ======
def get_llm_chain(llm_model, prompt_template):
    pipeline = (
        {
            "human_input": itemgetter("human_input"),
            "history": itemgetter("history"),
        }
    | prompt_template | llm_model.bind(stop=["Human:", "Sinh viên:", "Học sinh:"])
    )
    return pipeline
    # return LLMChain(llm=llm_model, prompt=prompt_template)

class ChatChain:
    def __init__(self,
                 model_path=model_config["chatbot_path"]["Q5bit"], 
                 model_type=model_config["chatbot_type"],
                 model_config=model_config["chatbot_config"]):
        
        llm_model = load_llm_model(model_path, model_type, model_config)
        prompt_template = get_PromptTemplate(memory_prompt_template)
        self.llm_chain = get_llm_chain(llm_model, prompt_template)
        
    def run(self, question, memory):
        return self.llm_chain.invoke(input={"human_input" : question, "history" : memory.load_memory_variables({})})

def load_normal_chain():
    return ChatChain()

# ====== RetrievalQA Chain ======
def get_retriever_chain(llm_model, retriever):
    return RetrievalQA.from_chain_type(llm=llm_model, chain_type="stuff", retriever=retriever, verbose=True)

def get_retriever_chain_pipeline(llm_model, prompt_template, retriever):
    pipeline = (
        {
            "context": itemgetter("human_input") | retriever,
            "human_input": itemgetter("human_input"),
            "history": itemgetter("history"),
        }
    | prompt_template | llm_model.bind(stop=["Human:", "Sinh viên:", "Học sinh:"])
    )
    return pipeline

class RAG_ChatChain:
    def __init__(self,
                 number_of_documents=3,
                 model_path=model_config["chatbot_path"]["Q5bit"], 
                 model_type=model_config["chatbot_type"],
                 model_config=model_config["chatbot_config"],
                 db_path=db_config["database_path"]):
        
        db = vectordb.load_vector_db(db_path)
        retriever = db.as_retriever(search_kwargs={"k":number_of_documents})
        llm_model = load_llm_model(model_path, model_type, model_config)
        prompt_template = get_PromptTemplate(rag_prompt_template)
        
        self.llm_chain = get_retriever_chain_pipeline(llm_model=llm_model, prompt_template=prompt_template, retriever=retriever)
        
    def run(self, question, memory):
        return self.llm_chain.invoke(input={"human_input" : question, "history" : memory.load_memory_variables({})})
    
def load_rag_chain(number_of_documents=3):
    return RAG_ChatChain(number_of_documents=number_of_documents)