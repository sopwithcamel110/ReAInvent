# Import modules
from importlib.machinery import FrozenImporter
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_restful import Resource, Api
from bs4 import BeautifulSoup
from pytube import YouTube
import csv
import pandas as pd
import numpy as np
import openai
import pickle
import os
from pathlib import Path
import replicate
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract 
from dotenv import load_dotenv
from json import dumps, loads
import helper
from ast import literal_eval
from flask_session import Session
import fitz


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('secret_key')
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
Session(app)
api = Api(app)

class ValidateURL(Resource):
    def post(self):
        session.clear()
        url = request.json['url']
        session['url'] = url
        try:
            t = YouTube(url)
            t.check_availability() 
            session['mediatype'] = 'video'
            return jsonify({'Valid': 1})
        except:
            try: 
                _ = requests.get(url)
                session['mediatype'] = 'article' 
                return jsonify({'Valid':1})
            except:
                return jsonify({'Valid' : 0})
        
class Ping(Resource):
    def get(self):
        return jsonify({'message' : "Pong!"})

def getURLText(url):
    try:
        r = requests.get(url)
    except:
        return None
    return r.text
def remove_non_ascii(string):
    return ''.join(char for char in string if ord(char) < 128)
class GenerateTranscript(Resource):
    def get(self):
        url = session.get('url')

        fin_out = []
        count = 0
        match session['mediatype']:
            case 'video':
                vid = YouTube(url)
                session['vid_length'] = str(vid.length)
                id=extract.video_id(url)
                session['id'] = id
                transcript = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
                for seg in transcript: 
                    if(count >= len(transcript) - 8):
                        break
                    else:
                        string = transcript[count]['text'] + " " + transcript[count+1]['text']+ " " + transcript[count+2]['text'] + " " + transcript[count+3]['text'] + transcript[count+4]['text'] + transcript[count+5]['text'] + transcript[count+6]['text'] + transcript[count+7]['text']
                        string = helper.remove_non_ascii(string)
                        string = string.replace("\n", " ")
                        start = transcript[count]['start']
                        fin_out.append({'text': string, 'start':start, 'end':-1})
                        count += 8

                transcript = fin_out
                session['transcript'] = fin_out
                arr = [] 
                for seg in transcript: 
                    arr.append(seg['text'])
                data = {'title': ['video' for i in range(len(transcript))], 'heading': [i+1 for i in range(len(transcript))], 'content': arr, "tokens" : [None for i in range(len(transcript))]}

            case 'article':
                htmldata = getURLText(url)
                temp = [] 
                data = ''
                if htmldata is not None:
                    soup = BeautifulSoup(htmldata, 'html.parser')
                    for data in soup.find_all("p"):
                        temp.append(remove_non_ascii(data.get_text()))
                else:
                    return jsonify({'Completed' : 403}) 
                
                list_strings = [] 
                i = 0
                while i < len(temp): 
                    if(i+1 < len(temp)):
                        list_strings.append(temp[i] + " " + temp[i+1])
                    else:
                        list_strings.append(temp[i])
                    i+=2
                data = {'title': ["article" for i in range(len(list_strings))], 'heading': [count for count in range(len(list_strings))], 'content': [seg for seg in list_strings], 'tokens': [None for i in range(len(list_strings))]}
            
        df = pd.DataFrame(data)
        session['df'] = df.to_json()
        df = df.set_index(["title", "heading"])
        val = helper.compute_doc_embeddings(df)
        document_embeddings = val
        document_embeddings = {str(k): v for k, v in document_embeddings.items()}
        session['embeddings'] = document_embeddings
        return jsonify({'Completed' : 1})

class AnswerQuestion(Resource):
    def post(self):
        transcript = session.get('transcript')
        df = pd.read_json(session.get('df'))
        df = df.set_index(["title", "heading"])
        content = request.json
        question = content['question']
        document_embeddings = {literal_eval(k): v for k, v in session.get('embeddings').items()}
        answer, arrInds = helper.answer_query_with_context(question, df, document_embeddings, False)
        match session['mediatype']:
            case 'video':
                stamps = helper.filterLinks(int(session.get('vid_length')), df, transcript, arrInds)
                return jsonify({"answer": answer, "stamps" : stamps})
            case 'article':
                return jsonify({'answer': answer, 'stamps': []})



api.add_resource(ValidateURL, "/validate")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")
api.add_resource(Ping, "/ping")

# Driver
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
