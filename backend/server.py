# Import modules
from importlib.machinery import FrozenImporter
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
from pathlib import Path
import replicate
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract 

# Create Flask App
app = Flask(__name__)
# Create API Object
api = Api(app)

# Global vars
COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"
os.environ["REPLICATE_API_TOKEN"] = 'cc7adc079220b946329055014b9e32299e37bca9'
MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"  # encoding for text-embedding-ada-002
encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))
df = None 
arrInds = None 
output_transcript = None
document_embeddings =  None
vid_length = None
vid = None
model = None
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 500,
    "model": COMPLETIONS_MODEL,
}
def makeNumArr():
    num = arrInds
    arr = []
    for i in range(len(num)):
        arr.append(int(num[i][10:len(num[i])-1]))
    return arr 

def get_start_and_end():
    arrNum = makeNumArr()
    output = output_transcript

    arrPut = output

    arrTime = []
    for i in range(len(arrNum)):
        text = df['content'][arrNum[i]-1]
        text = text.strip()
        text = text.lower()
        for j in range(len(arrPut)):
            temp = arrPut[j]['text']
            temp = temp.strip()
            temp = temp.lower()
            if temp == text: 
                arrTime.append( ( int(arrPut[j]['start']) , int(arrPut[j]['end'] )) )

    return arrTime

def getLinks():
    arrTimes = get_start_and_end()
    sorted(arrTimes)
    arrLink = [] 

    for i in range(len(arrTimes)):
        arrLink.append(str(arrTimes[i][0]-3))
    
    return arrLink

def filterLinks():
    count = 0
    ratio = 0.116
    capped = min(int(ratio*vid_length/60), 10)

    links = getLinks()
    # print("links: ")
    # print(links)
    fin_links = []

    while(count <= capped):
        fin_links.append(links[count])
        count += 1 
    
    return fin_links


#needed methods
def answer_query_with_context(query,df,document_embeddings,show_prompt):
    # print("embeddings debug: ")
    # print(document_embeddings)
    prompt = construct_prompt(
        query,
        document_embeddings,
        df
    )
    
    if show_prompt:
        print(prompt)

    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )

    return response["choices"][0]["text"].strip(" \n")

def construct_prompt(question, context_embeddings, df):
    global arrInds
    most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)
    
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    count = 30
    
    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.        
        document_section = df.loc[section_index]
        
        chosen_sections_len += document_section.tokens + separator_len
        if count == 0:
            break
        else:
            count -= 1 
            
        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
    
    arrInds = chosen_sections_indexes
    # # Useful diagnostic information
    # print(f"Selected {len(chosen_sections)} document sections:")
    # print("\n".join(chosen_sections_indexes))
    
    header = """Answer the question as truthfully as possible using the provided context from a youtube video, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    
    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"

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
def load_embeddings(fname):
    df = pd.read_csv(fname, header=0)
    max_dim = max([int(c) for c in df.columns if c != "title" and c != "heading"])
    return {
           (r.title, r.heading): [r[str(i)] for i in range(max_dim + 1)] for _, r in df.iterrows()
    }
def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query, contexts):
    query_embedding = get_embedding(query)
    
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    
    return document_similarities

# API
# Create resources
class LoadModel(Resource):
    def get(self):
        global model
        # model = whisper.load_model("small")

        return jsonify({'Completed' : 1})
class ValidateURL(Resource):
    def get(self, desc=""):
        # Set valid to 1 if url is valid
        # desc: YouTube url descriptor https://www.youtube.com/watch?v=     ----> cdZZpaB2kDM
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
            
        # for i in range(len(srt['segments'])):
        #     writer.writerow(["video", str(i+1), output['segments'][i]['text'], len(output['segments'][i]['tokens'])])
        df = pd.read_csv('./content/output.csv')
        df = df.set_index(["title", "heading"])

        # need to make this an environment variable
        openai.api_key = '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'
        document_embeddings = compute_doc_embeddings(df)
        return jsonify({'Completed' : 1})

class AnswerQuestion(Resource):
    def post(self):
        content = request.json
        question = content['question']
        answer =  answer_query_with_context(question, df, document_embeddings, False)
        stamps = filterLinks()
        return jsonify({"answer": answer, "stamps" : stamps})


# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")
api.add_resource(LoadModel, "/loadmodel")

# Driver
if __name__ == '__main__':
    app.run(debug=True)


# getting the indices from the string into an array
def makeNumArr():
    num = arrInds
    arr = []
    for i in range(len(num)):
        arr.append(int(num[i][10:len(num[i])-1]))
    return arr 

def get_start_and_end():
    arrNum = makeNumArr()
    output = output_transcript

    arrPut = output

    arrTime = []
    for i in range(len(arrNum)):
        text = df['content'][arrNum[i]-1]
        text = text.strip()
        text = text.lower()
        for j in range(len(arrPut)):
            temp = arrPut[j]['text']
            temp = temp.strip()
            temp = temp.lower()
            if temp == text: 
                arrTime.append( ( int(arrPut[j]['start']) , int(arrPut[j]['end'] )) )
    return arrTime

