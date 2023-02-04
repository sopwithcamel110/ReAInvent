import React, { useRef, useState } from "react";
import ReactPlayer from 'react-player'
import "./App.css";
import QandA from './QandA.js';

function App() {
  const textRef = useRef();
  const questionRef = useRef();
  const [url, setUrl] = useState();
  const [progress, setProgress] = useState();
  const [qs, setQs] = useState([]);
  let desc = "None";

  function handleQuestionEnter(e) {
    if (e.key === 'Enter') {
      // Ask question
      let text = questionRef.current.value;
      setQs(oldArray => [...oldArray, ["Question", text]])

      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      };
      fetch('/ask', requestOptions)
        .then(response => response.json())
        .then(data => {
          setQs(oldArray => [...oldArray, ["Answer", data.answer]]);
        });
    }
  }

  function LoadModel() {
    setProgress("Loading Model...");
    fetch("/loadmodel")
    .then((response) => response.json())
    .then((data) => {
      if (data.Completed === 1) {
        console.log("Model loaded.");
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
      }
    });
    setProgress("");
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
        LoadModel();
      }
    });
  }

	return (
		<>
			<header className="App-header">
				<h1>Testing</h1>
			</header>
      <h3>
        Enter text:
      </h3>
      <input id="urlInput" name="linkInput" type="text" ref={textRef}/>
      <br/>
      <input type="submit" id="analyzeBtn" value="Analyze" onClick={HandleAnalyzeClicked}/>
      <br/>
      <h3>{progress}</h3>
      <ReactPlayer url={url} id="videoplayer"/>
      <div className="chatbox">
        <div className="QandA">
          {
            qs.map((value) => {
              return (
                <QandA type={value[0]} text={value[1]}/>
              )
            })
          }
        </div>
        <div className="questionInput">
          <input id="questionTextInput" type="text" ref={questionRef} onKeyDown={handleQuestionEnter}/>
        </div>
      </div>
		</>
	);
}

export default App;
