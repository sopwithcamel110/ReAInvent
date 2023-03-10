# Import modules
from importlib.machinery import FrozenImporter
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_restful import Resource, Api
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

load_dotenv()

# Create Flask App
app = Flask(__name__)
app.secret_key = os.environ.get('secret_key')
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
Session(app)
# Create API Object
api = Api(app)

# Create resources

class ValidateURL(Resource):
    def post(self):
        session.clear()
        content = request.json
        url = content['url']
        try:
            _ = YouTube(url)
            valid = 1
        except:
            valid = 0

        session['url'] = url 
        return jsonify({'Valid' : valid})
        
class Ping(Resource):
    def get(self):
        return jsonify({'message' : "Pong!"})

class GenerateTranscript(Resource):
    def get(self):
        url = session.get('url')
        vid = YouTube(url)

        id=extract.video_id(url)
        # transcript: list of dictionaries with start, text, duration keys
        session['id'] = id
        try:
            transcript = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
        except:
            return jsonify({'Completed' : 404})
        fin_out = []
        count = 0 

        #combining sentences in transcript
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

        #making dataframe  
        arr = [] 
        for seg in transcript: 
            arr.append(seg['text'])
        data = {'title': ['video' for i in range(len(transcript))], 'heading': [i+1 for i in range(len(transcript))], 'content': arr, "tokens" : [None for i in range(len(transcript))]}
        
        df = pd.DataFrame(data)
        # df = df.set_index(["title", "heading"])
        # print("___________Works______________")
        session['df'] = df.to_json()
        # print('----------TESTING------------')
        # print(session['df'])
        # print("_____________Also__Works________")
        df = df.set_index(["title", "heading"])
        val = helper.compute_doc_embeddings(df)
        # print("TESTING" + str(type(val)))
        document_embeddings = val
        document_embeddings = {str(k): v for k, v in document_embeddings.items()}
        session['embeddings'] = document_embeddings
        session['vid_length'] = str(vid.length)
        return jsonify({'Completed' : 1})

class AnswerQuestion(Resource):
    def post(self):
        transcript = session.get('transcript')
        # #making dataframe  
        # arr = [] 
        # for seg in transcript: 
        #     arr.append(seg['text'])
        # data = {'title': ['video' for i in range(len(transcript))], 'heading': [i+1 for i in range(len(transcript))], 'content': arr, "tokens" : [None for i in range(len(transcript))]}

        df = pd.read_json(session.get('df'))

        content = request.json
        question = content['question']
        # df = pd.DataFrame(data)
        df = df.set_index(["title", "heading"])
        document_embeddings = {literal_eval(k): v for k, v in session.get('embeddings').items()}

        answer, arrInds = helper.answer_query_with_context(question, df, document_embeddings, False)
        # print("------------arrInds:-----------")
        # print(arrInds)
        stamps = helper.filterLinks(int(session.get('vid_length')), df, transcript, arrInds)

        return jsonify({"answer": answer, "stamps" : stamps})


# Add resources to API
api.add_resource(ValidateURL, "/validate")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")
api.add_resource(Ping, "/ping")

# Driver
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
