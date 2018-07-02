from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer, Metadata, Interpreter

def parse_query(query):
    interpreter = Interpreter.load('./models/faq_chatbot_nlu/default/faq_chatbot_nlu')
    return interpreter.parse(query)
