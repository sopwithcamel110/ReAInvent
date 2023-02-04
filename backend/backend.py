import whisper
from pytube import YouTube
import csv
import pandas as pd
import numpy as np
import openai
import pickle
import tiktoken

COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"

MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"  # encoding for text-embedding-ada-002

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

model = None 
df = None 
document_embeddings =  None
#should only run once (first time user presses analyze)
def load_model():
    global model
    model = whisper.load_model("base")

#gets the vid transcription, should happen if analyze is pressed
def get_vid_transcript(url):
  global df
  global document_embeddings
  youtube_video_url = url
  vid = YouTube(youtube_video_url)
  streams = vid.streams.filter(only_audio=True)

  stream = streams.first()
  stream.download(filename='/content/video.mp4')

  output = model.transcribe("/content/video.mp4")

  with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["title", "heading", "content", "tokens"])
    content = []
    for i in range(len(output['segments'])):
      writer.writerow(["video", str(i+1), output['segments'][i]['text'], len(output['segments'][i]['tokens'])])

  df = pd.read_csv('/content/output.csv')
  df = df.set_index(["title", "heading"])

  # need to make this an environment variable
  openai.api_key = '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'
  document_embeddings = compute_doc_embeddings(df)
  return df, document_embeddings

#should be called anytime question is asked in chatbot
def get_out(question):
    # print("embeddings debug: ")
    # print(document_embeddings)
    return answer_query_with_context(question, df, document_embeddings, False)


#needed methods 
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 500,
    "model": COMPLETIONS_MODEL,
}
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

AX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"  # encoding for text-embedding-ada-002

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

def construct_prompt(question, context_embeddings, df):
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
    
    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    
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

# load_model()
# get_vid_transcript("https://www.youtube.com/watch?v=mi9sMazNPxM")
# response = get_out("why did the indus valley civilization go into decline?")