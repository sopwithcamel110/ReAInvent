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
    try:
	    r = requests.get(url)
    except:
        print("invalid link")
        return None
    return r.text

t = YouTube("https://www.youtube.com/watch?v=zzyai3wAkpo")
try:
    t.check_availability()
    print("should print")
except:
    print("worked")



htmldata = getdata("https://www.newschannel5.com/news/police-responding-to-active-aggressor-situation-at-covenant-school")
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

#TODO: Delete the lines above and make this work with directly writing to a dataframe 
data = {'title': ["article" for i in range(len(list_strings))], 'heading': [str(count) for count in range(len(list_strings))], 'content': [seg for seg in list_strings], 'tokens': [None for i in range(len(list_strings))]}

df = pd.DataFrame(data)
df = df.set_index(["title", "heading"])
print(df)
document_embeddings = helper.compute_doc_embeddings(df)
question = ""
while(True):
    question = input("Enter a question: ")
    if(question == 'q'):
        break
    print("__________________RESPONSE_____________________")
    answer, arrInds = helper.answer_query_with_context(question, df, document_embeddings, False)
    print(answer)
    print("__________________TIME STAMPS_________________")
    print(helper.filterLinks(0, df, None, arrInds, is_article=True))


