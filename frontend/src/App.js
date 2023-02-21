import React, { useRef, useState } from "react";
import ReactPlayer from 'react-player'
import "./App.css";
import Chatbox from './Chatbox.js';
import Header from './Header.js';
import { GrYoutube } from 'react-icons/gr';
import { AtomLoader } from "react-loaders-kit";
import * as Scroll from 'react-scroll';

function App() {
  const API_ENDPOINT = "/api";
  const urlInputRef = useRef();
  const playerRef = useRef();
  const [url, setUrl] = useState();
  const [progress, setProgress] = useState();
  const [transcriptLoader, showTranscriptLoader] = useState(false);
  const [chatbox, showChatbox] = useState(false);
  const [isPlaying, setPlaying] = useState(false);
  const loaderProps = {
    loading: true,
    size: 80,
    duration: 2,
    colors: ["#FF2900", "#FF5500", "#FFE600"],
  };
  let link = "None";

  function CheckServerStatus() {
    setProgress("Checking server status...");
    fetch(API_ENDPOINT + "/ping")
    .then((response) => {
      if (!response.ok) {
        setProgress("Server is offline. Please try again later.");
        throw new Error(response.status);
      }
      else {
        return response.json();
      }
    })
    .then((data) => {
      if (data.message === "Pong!") {
        ValidateURL();
      }
    })
    .catch((error) => {
      console.log(error);
    });
  }

  function ValidateURL() {
    setProgress("Validating URL...");

    // Get input
    let text = urlInputRef.current.value;
    if (text === "") {
      text = "None"
    }
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: text })
    };
    link = text;
    // Create get request
    fetch(API_ENDPOINT + "/validate", requestOptions)
    .then((response) => response.json())
    .then((data) => {
      if (data.Valid === 1) {
        // Cleanup
        showTranscriptLoader(true);
        GenerateTranscript();
      }
      else {
        setProgress("Invalid URL.");
      }
    });
  }

  function GenerateTranscript() {
    setProgress("Fetching Transcript...");
    fetch(API_ENDPOINT + "/gentranscript")
    .then((response) => response.json())
    .then((data) => {
      if (data.Completed === 1) {
        setUrl(link)
        showChatbox(true);
        Scroll.animateScroll.scrollTo(420);
        setProgress("");
        showTranscriptLoader(false);
      }
      else if (data.Completed === 404) {
        setProgress("Requested video has no transcript. Please try a new video.")
        showTranscriptLoader(false);
      }
    });
  }

  function HandleAnalyzeClicked(e) {
    CheckServerStatus();
  }

	return (
		<>
      <Header/>
      <div className="title">
        <h1>Re</h1>
        <h1 className="titleAI">AI</h1>
        <h1>nvent</h1>
      </div>
      <h3>
        Enter Youtube URL below:
      </h3>
      <div className="urlInput">
        <GrYoutube color = "red" size = "30px" style = {{
          marginLeft: "-20px", marginBottom: "-7px"
        }}/>
        <input id="urlTextInput" name="linkInput" type="text" ref={urlInputRef}/>
      </div>
      <br/>
      <input type="submit" id="analyzeBtn" value="Analyze" onClick={HandleAnalyzeClicked}/>
      <br/>
      <h3>{progress}</h3>
      {
        transcriptLoader ? (<div className="progressLoader"><AtomLoader {...loaderProps}/></div>) : (<div/>)
      }
      {
        chatbox ? <div>
                    <div>
                      <ReactPlayer ref={playerRef} controls={true} url={url} id="videoplayer" playing={isPlaying}/>
                    </div>
                    <Chatbox playerRef={playerRef} endpoint={API_ENDPOINT} setPlaying={setPlaying}/>
                  </div> : <></>
      }
		</>
	);
}

export default App;
