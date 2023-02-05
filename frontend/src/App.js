import React, { useRef, useState } from "react";
import ReactPlayer from 'react-player'
import "./App.css";
import QandA from './QandA.js';
import { FiSend } from 'react-icons/fi';
import {GrYoutube} from 'react-icons/gr';

function App() {
  const textRef = useRef();
  const questionRef = useRef();
  const playerRef = useRef();
  const [url, setUrl] = useState();
  const [progress, setProgress] = useState();
  const [chat, setChat] = useState([]);
  let desc = "None";

  function handleQuestionEnter(e) {
    if (e.key === 'Enter') {
      askQuestion();
    }
  }
  
  function askQuestion() {
    // Ask question
    let text = questionRef.current.value;
    questionRef.current.value = "";
    setChat(oldArray => [["Question", text, []], ...oldArray]);
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    };
    fetch('/ask', requestOptions)
      .then(response => response.json())
      .then(data => {
        console.log(data.stamps);
        setChat(oldArray => [["Answer", data.answer, data.stamps], ...oldArray]);
      });
  }

  function LoadModel() {
    setProgress("Loading Model...");
    fetch("/loadmodel")
    .then((response) => response.json())
    .then((data) => {
      if (data.Completed === 1) {
        GenerateTranscript();
      }
    });
  }

  function GenerateTranscript() {
    setProgress("Fetching Transcript...");
    fetch("/gentranscript")
    .then((response) => response.json())
    .then((data) => {
      if (data.Completed === 1) {
        console.log("Transcript loaded.");
        setUrl("https://www.youtube.com/watch?v=" + desc)
        questionRef.current.scrollIntoView({behavior: "smooth"});
        setProgress("");
      }
    });
  }

  function HandleAnalyzeClicked(e) {
    setProgress("Validating URL...");
    // Get input
    let text = textRef.current.value;
    if (text === "") {
      text = "None"
    }
    // Isolate descriptor from youtube link
    desc = (text.replace("https://", "")).replace("www.youtube.com/watch?v=", "");
    // Create get request
    fetch("/validate/"+desc)
    .then((response) => response.json())
    .then((data) => {
      if (data.Valid === 1) {
        // Cleanup
        LoadModel();
      }
      else {
        setProgress("Invalid URL.");
      }
    });
  }

	return (
		<>
			<header className="App-header">
				<h1>Re</h1>
        <h1 className="titleAI">AI</h1>
        <h1>nvent</h1>
			</header>
      <h3>
        Enter Youtube URL below:
      </h3>
      <div className="urlInput">
        <GrYoutube color = "red" size = "30px" style = {{
          marginLeft: "-20px", marginBottom: "-7px"
        }}/>
        <input id="urlTextInput" name="linkInput" type="text" ref={textRef}/>
      </div>
      <br/>
      <input type="submit" id="analyzeBtn" value="Analyze" onClick={HandleAnalyzeClicked}/>
      <br/>
      <h3>{progress}</h3>
      <ReactPlayer ref={playerRef} controls="true" url={url} id="videoplayer" style= {{
      }}/>
      <div className="chatbox">
        <div className="questionInput">
          <input id="questionTextInput" type="text" ref={questionRef} onKeyDown={handleQuestionEnter}/>
          <FiSend className="questionButton" onClick={askQuestion} size= "20px" style= {{
            marginTop: "10px"
          }}/>
        </div>
        <div className="QandA">
          {
            chat.map((value) => {
              return (
                <QandA playerRef={playerRef} type={value[0]} text={value[1]} stamps={value[2]}/>
              )
            })
          }
        </div>
      </div>
		</>
	);
}

export default App;
