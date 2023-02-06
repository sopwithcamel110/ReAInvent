# CruzHacks2023

## Example:

<p align="center">
  <img src="https://media.giphy.com/media/oepOUjo00amPeTO6ye/giphy.gif" width=600 height=350 alt="animated" />
</p>

## Project description 

This was our submission for CruzHacks 2023, soon to become a full-fledged project (maybe). We created a **question answer chatbot for youtube videos** using semantic search, large language models, and REST API.
 
## What is it for? 

We created this project to increase the efficiency of learning, allowing for longer form videos to be parsed down to text in the matter of seconds. Being able to quickly re-reference sections of lectures where professors go over specific types of problems, or trying to find where the professor talks about a specific quiz/grading policy can be quite the pain for videos that last over an hour. Being able to quickly find this information, and being ensured it is accurate, is an incredibly convenient and useful product for any student.

Outside of just university students, this program can be used with any youtube video, so long as it has an accurate transcription. In any case where you find yourself scrubbing through a video to quickly find pieces of information, reAInvent is there to do it faster for you. 

## How does it work? 

We use `pytube` and `youtube_transcript_api` to scrape a given youtube url for its transcription. From there we run a semantic search with the query being the question asked by the client, and the document being the youtube transcription. To perform the semantic search, we use OpenAI's embedding models, and sort the transcription by cosine similarity in respect to the query in order to find the most relevant parts of the video for the question. We then feed the transcriptions as context to GPT-DaVinci, OpenAI's largest LLM, and the original question to achieve the accurate and diegestable responses you saw in the example.

We also use prompt engineering to prevent hallucinations (misinfomration) by GPT, and include relevant timestamps so you can quickly watch back the sections you are looking for.

## Create a virtual environment
1. Start by navigating to the project directory
2. Create the virtual environment
```console 
python3 -m venv ./venv
```
3. Activate the virtual environment
```console 
/venv/Scripts/activate.bat
```
## Install dependencies
```console 
pip install -r requirements.txt
```
## Start the API
```console 
python ./backend/server.py
```
_Note: You need to provide an OpenAI API key in a .env file within the backend directory. We are currently working on deploying this project but for now, running locally will require an API key. The .env file should have the text openai_key = "{API_KEY}".
_
## Start the Website
```console
cd frontend
npm start
```

Navigate to localhost:3000 to view the webserver.
