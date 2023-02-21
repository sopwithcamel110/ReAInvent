import React, { useRef, useState } from "react";
import ReactPlayer from 'react-player'
import "./App.css";
import Chatbox from './Chatbox.js';
import Header from './Header.js';
import { GrYoutube } from 'react-icons/gr';
import { AtomLoader } from "react-loaders-kit";

function App() {
  const API_ENDPOINT = "/api";
  const urlInputRef = useRef();
  const playerRef = useRef();
  const [url, setUrl] = useState();
  const [progress, setProgress] = useState();
  const [transcriptLoader, showTranscriptLoader] = useState(false);
  const [chatbox, showChatbox] = useState(false);
  const loaderProps = {
    loading: true,
    size: 80,
    duration: 2,
    colors: ["#FF2900", "#FF5500", "#FFE600"],
  };
  let desc = "None";

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
    // Isolate descriptor from youtube link
    desc = (text.replace("https://", "")).replace("www.youtube.com/watch?v=", "");
    // Create get request
    fetch(API_ENDPOINT + "/validate/" + desc)
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
        console.log("Transcript loaded.");
        setUrl("https://www.youtube.com/watch?v=" + desc)
        showChatbox(true);
        //playerRef.scrollIntoView({behavior: "smooth"});
        setProgress("");
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
                      <ReactPlayer ref={playerRef} controls={true} url={url} id="videoplayer"/>
                    </div>
                    <Chatbox playerRef={playerRef} endpoint={API_ENDPOINT}/>
                  </div> : <div/>
      }
		</>
	);
}

export default App;
