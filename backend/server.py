# Import modules
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import whisper
from pytube import YouTube
import csv
import pandas as pd
import numpy as np
import openai
import pickle
import tiktoken
import os

# Create Flask App
app = Flask(__name__)
# Create API Object
api = Api(app)

# Globals
COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"

model = None
df = None
document_embeddings =  None
url = None

# Create resources
class AnswerQuestion(Resource):
    def post(self):
        content = request.json
        question = content['question']
        return jsonify({"answer":"Let's find an answer to: " + question})
class ValidateURL(Resource):
    def get(self, desc=""):
        # Set valid to 1 if url is valid
        # desc: YouTube url descriptor https://www.youtube.com/watch?v=     ----> cdZZpaB2kDM
        valid = 0
        if len(desc) == 11:
            valid = 1
            global url
            url = "https://www.youtube.com/watch?v=" + desc
        
        #END CODE
        return jsonify({'Valid' : valid})

class LoadModel(Resource):
    def get(self):
        global model
        if (model == None):
            model = whisper.load_model("base")
        return jsonify({'Completed' : 1})

class GenerateTranscript(Resource):
    def get(self):
        global df
        global document_embeddings
        youtube_video_url = url
        vid = YouTube(youtube_video_url)
        streams = vid.streams.filter(only_audio=True)

        os.mkdir("./content/")

        stream = streams.first()
        stream.download(filename='./content/video.mp4')
        output = model.transcribe("./content/video.mp4")


        with open('output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["title", "heading", "content", "tokens"])
            content = []
            for i in range(len(output['segments'])):
                writer.writerow(["video", str(i+1), output['segments'][i]['text'], len(output['segments'][i]['tokens'])])

        df = pd.read_csv('./content/output.csv')
        df = df.set_index(["title", "heading"])

        # need to make this an environment variable
        openai.api_key = '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'
        document_embeddings = compute_doc_embeddings(df)

        return jsonify({'Completed' : 1})


# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(LoadModel, "/loadmodel")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")

# Driver
if __name__ == '__main__':
    app.run(debug=True)

def get_embedding(text, model=EMBEDDING_MODEL):
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]

def compute_doc_embeddings(df):
    return {
        idx: get_embedding(r.content) for idx, r in df.iterrows()
    }