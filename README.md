# CruzHacks2023

## Put GIF here

## Project description 

This was our submission for CruzHacks 2023, soon to become a full-fledged project (maybe). We created a **question answer chatbot for youtube videos** using semantic search and large language models. We used OpenAI's embedding models and GPT-DaVinci to perform a semantic search on a youtube transcription, then took the most relevent transcripts received to answer questions using prompt engineering with GPT-DaVinci.

## Examples: soon to be added 

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

## Start the Website
```console
cd frontend
npm start
```

Navigate to localhost:3000 to view the webserver.
