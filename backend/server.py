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
url = None
output_transcript = None
document_embeddings =  None
vid_length = None
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 500,
    "model": COMPLETIONS_MODEL,
}
#holding arrays before index processing 
arrInds = [] 
#array holding a tuple value of (time, youtube_url) for relevant points of the video
timestamps = [] 


# Create resources
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
    global arrayInds
    most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)
    
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []
     
    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.        
        document_section = df.loc[section_index]
        
        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break
            
        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
            
    # Useful diagnostic information
    # print(f"Selected {len(chosen_sections)} document sections:")
    # print("\n".join(chosen_sections_indexes))
    
    arrInds = chosen_sections_indexes

    header = """Answer the question as truthfully as possible using the provided context from a video, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    
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
class GenerateTranscript(Resource):
    def get(self):
        global df
        global document_embeddings
        global output_transcript
        global vid_length
        youtube_video_url = url
        vid = YouTube(youtube_video_url)
        vid_length = vid.length
        streams = vid.streams.filter(only_audio=True)

        if(not os.path.exists("./content")):
            os.mkdir("./content/")

        stream = streams.first()
        out_file=stream.download(filename='./content/video.mp3')

        model = replicate.models.get("openai/whisper")
        version = model.versions.get("23241e5731b44fcb5de68da8ebddae1ad97c5094d24f94ccb11f7c1d33d661e2")

        inputs = {
            # Audio file
            'audio': open("./content/video.mp3", "rb"),

            # Choose a Whisper model.
            'model': "base",

            # Choose the format for the transcription
            'transcription': "plain text",

            # Translate the text to English when set to True
            'translate': False,

            # language spoken in the audio, specify None to perform language
            # detection
            # 'language': ...,

            # temperature to use for sampling
            'temperature': 0,

            # optional patience value to use in beam decoding, as in
            # https://arxiv.org/abs/2204.05424, the default (1.0) is equivalent to
            # conventional beam search
            # 'patience': ...,

            # comma-separated list of token ids to suppress during sampling; '-1'
            # will suppress most special characters except common punctuations
            'suppress_tokens': "-1",

            # optional text to provide as a prompt for the first window.
            # 'initial_prompt': ...,

            # if True, provide the previous output of the model as a prompt for
            # the next window; disabling may make the text inconsistent across
            # windows, but the model becomes less prone to getting stuck in a
            # failure loop
            'condition_on_previous_text': True,

            # temperature to increase when falling back when the decoding fails to
            # meet either of the thresholds below
            'temperature_increment_on_fallback': 0.2,

            # if the gzip compression ratio is higher than this value, treat the
            # decoding as failed
            'compression_ratio_threshold': 2.4,

            # if the average log probability is lower than this value, treat the
            # decoding as failed
            'logprob_threshold': -1,

            # if the probability of the <|nospeech|> token is higher than this
            # value AND the decoding has failed due to `logprob_threshold`,
            # consider the segment as silence
            'no_speech_threshold': 0.6,
        }

        #   output = model.transcribe(Path("content//Indus Valley Civilization   Early Civilizations  World History  Khan Academy.mp3"))\
        output = version.predict(**inputs)
        output_transcript = output

        with open('./content/output.csv', 'w', newline='') as file:
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

class AnswerQuestion(Resource):
    def post(self):
        content = request.json
        question = content['question']
        answer =  answer_query_with_context(question, df, document_embeddings, False)
        return jsonify({"answer": answer})


# Add resources to API
api.add_resource(ValidateURL, "/validate/<desc>")
api.add_resource(GenerateTranscript, "/gentranscript")
api.add_resource(AnswerQuestion, "/ask")

# Driver
if __name__ == '__main__':
    app.run(debug=True)


# ████████╗██╗███╗░░░███╗███████╗░██████╗████████╗░█████╗░███╗░░░███╗██████╗░  ░█████╗░░█████╗░██████╗░███████╗
# ╚══██╔══╝██║████╗░████║██╔════╝██╔════╝╚══██╔══╝██╔══██╗████╗░████║██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗██╔════╝
# ░░░██║░░░██║██╔████╔██║█████╗░░╚█████╗░░░░██║░░░███████║██╔████╔██║██████╔╝  ██║░░╚═╝██║░░██║██║░░██║█████╗░░
# ░░░██║░░░██║██║╚██╔╝██║██╔══╝░░░╚═══██╗░░░██║░░░██╔══██║██║╚██╔╝██║██╔═══╝░  ██║░░██╗██║░░██║██║░░██║██╔══╝░░
# ░░░██║░░░██║██║░╚═╝░██║███████╗██████╔╝░░░██║░░░██║░░██║██║░╚═╝░██║██║░░░░░  ╚█████╔╝╚█████╔╝██████╔╝███████╗
# ░░░╚═╝░░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═╝░░░░░  ░╚════╝░░╚════╝░╚═════╝░╚══════╝

# MADE BY RITESH:

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

    arrPut = output['segments']

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
        arrLink.append(url+'&t='+str(arrTimes[i][0]-3)+'s')
    
    return arrLink

def filterLinks():
    ratio = 0.3
    capped = min(ratio*vid_length, 10)

    links = getLinks()
    fin_links = []

    while(count <= capped):
        fin_links.append(links[count])
        count += 1 
    
    return fin_links
