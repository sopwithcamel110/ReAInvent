# Import modules
from importlib.machinery import FrozenImporter
from flask import Flask, jsonify, request
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
from flask_cors import CORS
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
        global vid
        url = "https://www.youtube.com/watch?v=" + desc
        try:
            vid = YouTube(url)
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
        global df
        global document_embeddings
        global vid_length
        global output_transcript
        #create the csv file from the transcript
        if (not os.path.exists("./content")):
            os.mkdir("./content")
        youtube_video_url = url
        vid = YouTube(youtube_video_url)
        streams = vid.streams.filter(only_audio=True)
        id=extract.video_id(youtube_video_url)
        vid_length = vid.length
        output = YouTubeTranscriptApi.get_transcript(id, languages=['en'])
        fin_out = []
        count = 0 

        for seg in output: 
            if(count >= len(output) - 8):
                break
            else:
                string = output[count]['text'] + " " + output[count+1]['text']+ " " + output[count+2]['text'] + " " + output[count+3]['text'] + output[count+4]['text'] + output[count+5]['text'] + output[count+6]['text'] + output[count+7]['text']
                start = output[count]['start']
                fin_out.append({'text': string, 'start':start, 'end':-1})
                count += 8
        output = fin_out
        output_transcript = output
        with open('./content/output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["title", "heading", "content", "tokens"])
            content = []
            count = 0 
            for seg in output: 
                count += 1
                writer.writerow(["video", str(count), seg['text']])

        df = pd.read_csv('./content/output.csv')
        df = df.set_index(["title", "heading"])
        document_embeddings = helper.compute_doc_embeddings(df)
        return jsonify({'Completed' : 1})

class AnswerQuestion(Resource):
    def post(self):
        content = request.json
        question = content['question']
        answer =  helper.answer_query_with_context(question, df, document_embeddings, False)
        stamps = helper.filterLinks(vid_length, df, output_transcript)
        return jsonify({"answer": answer, "stamps" : stamps})


# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")
api.add_resource(LoadModel, "/loadmodel")

# Driver
if __name__ == '__main__':
    app.run(debug=True)
