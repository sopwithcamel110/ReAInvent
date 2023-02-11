# import module
import requests
import pandas as pd
from bs4 import BeautifulSoup
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
import helper

load_dotenv()

def remove_non_ascii(string):
    return ''.join(char for char in string if ord(char) < 128)

# link for extract html data
def getdata(url):
	r = requests.get(url)
	return r.text

htmldata = getdata("https://www.reuters.com/world/middle-east/two-women-survive-days-earthquake-rubble-death-toll-tops-24150-2023-02-11/")
soup = BeautifulSoup(htmldata, 'html.parser')
data = ''
temp = [] 

for data in soup.find_all("p"):
	temp.append(remove_non_ascii(data.get_text()))

list_strings = [] 

i = 0
while i < len(temp): 
    if(i+1 < len(temp)):
        list_strings.append(temp[i] + " " + temp[i+1])
    else:
        list_strings.append(temp[i])
    i+=2

# print(f'length of old list {len(temp)}')
# print(f'length of new list {len(list_strings)}')

# print(list_strings)


if (not os.path.exists("./content")):
    os.mkdir("./content")


with open('./content/output_article.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["title", "heading", "content", "tokens"])
    content = []
    count = 0 
    for seg in list_strings: 
        count += 1
        writer.writerow(["article", str(count), seg])

df = pd.read_csv('./content/output_article.csv')
df = df.set_index(["title", "heading"])
document_embeddings = helper.compute_doc_embeddings(df)
question = ""
while(True):
    question = input("Enter a question: ")
    if(question == 'q'):
        break
    answer = helper.answer_query_with_context(question, df, document_embeddings, False)
    print(answer)


