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
import helper

load_dotenv()

# Create Flask App
app = Flask(__name__)
CORS(app)
# Create API Object
api = Api(app)

# Global vars
df = None 
arrInds = None 
output_transcript = None
document_embeddings =  None
vid_length = None
vid = None

# API
# Create resources
class LoadModel(Resource):
    def get(self):
        # model = whisper.load_model("small")
        return jsonify({'Completed' : 1})

class ValidateURL(Resource):
    def get(self, desc=""):
        global url
        url = "https://www.youtube.com/watch?v=" + desc
        session['url'] = url 
        try:
            session['vid'] = vid 
            valid = 1
        except:
            valid = 0
        
        #END CODE
        return jsonify({'Valid' : valid})
        
class Ping(Resource):
    def get(self):
        return jsonify({'message' : "Pong!"})

class GenerateTranscript(Resource):
    def get(self):
        global url
        global df
        global document_embeddings
        global vid_length
        global output_transcript
        youtube_video_url = session.get('url')
        vid = YouTube(youtube_video_url)
        session['vid'] = vid 
        streams = vid.streams.filter(only_audio=True)
        id=extract.video_id(youtube_video_url)
        vid_length = vid.length
        session['vid_length'] = vid.length
        output = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
        fin_out = []
        count = 0 

        #combining sentences in transcript
        for seg in output: 
            if(count >= len(output) - 8):
                break
            else:
                string = output[count]['text'] + " " + output[count+1]['text']+ " " + output[count+2]['text'] + " " + output[count+3]['text'] + output[count+4]['text'] + output[count+5]['text'] + output[count+6]['text'] + output[count+7]['text']
                string = helper.remove_non_ascii(string)
                start = output[count]['start']
                fin_out.append({'text': string, 'start':start, 'end':-1})
                count += 8
        output = fin_out
        output_transcript = output
        session['output_transcript'] = output

        #making dataframe  
        arr = [] 
        for seg in output: 
            arr.append(seg['text'])
        data = {'title': ['video' for i in range(len(output))], 'heading': [i+1 for i in range(len(output))], 'content': arr, "tokens" : [None for i in range(len(output))]}
        df = pd.DataFrame(data)
        df = df.set_index(["title", "heading"])
        session['df'] = df

        document_embeddings = helper.compute_doc_embeddings(df)
        session['document_embedings'] = document_embeddings
        return jsonify({'Completed' : 1})

class AnswerQuestion(Resource):
    def post(self):
        content = request.json
        question = content['question']
        answer =  helper.answer_query_with_context(question, session.get('df'), session.get('document_embeddings'), False)
        stamps = helper.filterLinks(session.get('vid_length'), session.get('df'), session.get('output_transcript'))
        return jsonify({"answer": answer, "stamps" : stamps})


# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")
api.add_resource(LoadModel, "/loadmodel")

# Driver
if __name__ == '__main__':
    app.run()
