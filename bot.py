import spacy
import numpy as np
import pandas as pd
from rasa_nlu.model import Interpreter

nlp = spacy.load('en')
interpreter = Interpreter.load('./models/faq_chatbot_nlu/default/faq_chatbot_nlu')

def run_nlu(query):
    global interpreter
    return interpreter.parse(query)

def bot():
    print('********** Chatbot Loaded! Start typing your queries here **********')
    print('\n')
    query = ''
    while(True):
        query = input()
        query = query.lower()
        if (query=='exit'):
            break
        parsed_query = run_nlu(query)
        response = route(parsed_query)
        print('A: ',response)
        print('\n')

def route(parsed_query):
    response = 'Kindly rephrase your words'
    demand_optional_entity_message = 'Please enter required information'
    intent = parsed_query['intent']['name']
    if (intent == 'greet' or intent == 'gratitude' or intent == 'goodbye'):
        response = general_conversation(intent)
    if (intent == 'requirement'):
        response = requirement(parsed_query)
    if (intent == 'extent'):
        response = single_entity_routing(parsed_query, intent ,'body')
    if (intent == 'definition'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'duration'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'benefits'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'legislation'):
        response = single_entity_routing(parsed_query, intent ,'field')
    if (intent == 'purpose'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'conditions'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'validity'):
        response = single_entity_routing(parsed_query, intent ,'country')
    if (intent == 'procedure'):
        response = single_entity_routing(parsed_query, intent ,'subject')
    if (intent == 'services'):
        response = single_entity_routing(parsed_query, intent ,'body')
    if (intent == 'address'):
        demand_optional_entity_message = 'For which city do you need the address for?'
        response = one_optional_double_entity_routing(parsed_query, intent ,'body','area', demand_optional_entity_message)
    if (intent == 'contact'):
        demand_optional_entity_message = 'For which city do you need the contact for?'
        response = one_optional_double_entity_routing(parsed_query, intent ,'body','area', demand_optional_entity_message)
    if (intent == 'email'):
        demand_optional_entity_message = 'For which city do you need the email for?'
        response = one_optional_double_entity_routing(parsed_query, intent ,'body','area', demand_optional_entity_message)
    if (intent == 'types'):
        demand_optional_entity_message = 'Please mention any status or card that you hold'
        response = one_optional_double_entity_routing(parsed_query, intent ,'subject','status', demand_optional_entity_message)
    return response

def most_similar_rows(routings, req_entity, req_entity_value):
    global nlp
    similarity_score = []
    for item in routings[req_entity]:
        w1 = nlp(req_entity_value)
        w2 = nlp(item)
        similarity = w1.similarity(w2)
        similarity_score.append(similarity)
    max_similarity_score = max(similarity_score)
    routings['score'] = similarity_score
    req_entity_rows = routings[routings['score'] == max_similarity_score]
    return req_entity_rows

def one_optional_double_entity_routing(parsed_query, intent, req_entity, optional_entity, demand_optional_entity_message):
    global nlp
    response = 'Kindly rephrase your words'
    path = 'routings/'+intent+'.xlsx'
    routings = pd.read_excel(path)
    entities = parsed_query['entities']
    if (len(entities) == 0):
        return response

    req_entity_value = []
    for entity in entities:
        if (entity['entity'] == req_entity):
            req_entity_value.append(entity['value'])
    if (len(req_entity_value) == 0):
        return 'No such information found.'
    req_entity_value = req_entity_value[0]

    demand_optional_entity = False
    req_entity_rows = most_similar_rows(routings, req_entity, req_entity_value)
    independent_row = req_entity_rows[req_entity_rows[optional_entity].isnull()]
    if (not(len(entities) == 1 and len(independent_row) == 1)):
        demand_optional_entity = True

    if (not demand_optional_entity):
        for item in req_entity_rows['response']:
            response = item
        return response

    optional_entity_value = []
    for entity in entities:
        if (entity['entity'] == optional_entity):
            optional_entity_value.append(entity['value'])

    if (len(optional_entity_value) == 0):
        print(demand_optional_entity_message)

        flag = 0
        optional_entity_detected = []
        while (flag == 0):
            optional_entity_query = input().lower()
            optional_query_entities = run_nlu(optional_entity_query)['entities']

            if (len(optional_query_entities) == 0):
                print('Kindly enter a valid',optional_entity)
            else:
                for entity in optional_query_entities:
                    if (entity['entity'] == optional_entity):
                        optional_entity_detected.append(entity['value'])
                        flag = 1

                if (len(optional_entity_detected) == 0):
                    print('Kindly enter a valid',optional_entity)
                else:
                    optional_entity_detected = optional_entity_detected[0]
                    optional_entity_value.append(optional_entity_detected)

    optional_entity_value = optional_entity_value[0]
    req_entity_rows.drop(['score'], axis=1, inplace=True)
    req_entity_rows.dropna(axis=0, inplace=True)
    optional_entity_rows = most_similar_rows(req_entity_rows, optional_entity, optional_entity_value)
    for item in optional_entity_rows['response']:
        response = item

    return response

test = run_nlu('types of taxable income')
message = 'enter status'
one_optional_double_entity_routing(test, 'types', 'subject', 'status', message)

def single_entity_routing(parsed_query, intent, req_entity):
    global nlp
    response = 'Kindly rephrase your words'
    path = 'routings/'+intent+'.xlsx'
    routings = pd.read_excel(path)
    entities = parsed_query['entities']
    if (len(entities) == 0):
        return response
    req_entity_value = []
    for entity in entities:
        if (entity['entity'] == req_entity):
            req_entity_value.append(entity['value'])
    if (len(req_entity_value) == 0):
        return response
    req_entity_value = req_entity_value[0]

    max_similarity = None
    max_similar_row = None
    for item in routings[req_entity]:
        w1 = nlp(req_entity_value)
        w2 = nlp(item)
        similarity = w1.similarity(w2)
        if (max_similarity == None):
            max_similarity = similarity
            max_similar_row = routings[routings[req_entity] == item]
        if (max_similarity < similarity):
            max_similarity = similarity
            max_similar_row = routings[routings[req_entity] == item]
    if (len(max_similar_row) == 0):
        return response
    for item in max_similar_row['response']:
        response = item
    return response

def requirement(parsed_query):
    global nlp
    response = 'Kindly rephrase your words'
    requirement_routings = pd.read_excel('routings/requirement.xlsx')
    entities = parsed_query['entities']

    if (len(entities) == 0):
        return response

    status = []
    for entity in entities:
        if (entity['entity'] == 'status'):
            status.append(entity['value'])
    if (len(status) == 0):
        print('Please enter a status card that you hold')
        flag = 0
        while(flag == 0):
            status_query = input().lower()
            status_query_entities = run_nlu(status_query)['entities']
            if (len(status_query_entities) == 0):
                print('Kindly rephrase your words and enter a valid status')
            else:
                status_detected = status_query_entities[0]['value']
                flag = 1
        status.append(status_detected)

    status = status[0]
    data = requirement_routings[requirement_routings['status'].isnull() == False]
    required_row = data[data['status'] == status]
    if (len(required_row) == 0):
        return 'Sorry! No such information found.'
    response = required_row['response'][0]
    return response

def general_conversation(intent):
    if (intent == 'greet'):
        return "Hi! I'm the Invest India Visa Chatbot"
    if (intent == 'gratitude'):
        return "It was a pleasure helping you"
    if (intent == 'goodbye'):
        return "Goodbye! Would love to hear from you again"

bot()
