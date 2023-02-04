import React, { useRef, useState } from "react";
import ReactPlayer from 'react-player'
import "./App.css";
import QandA from './QandA.js';
import { IconContext } from "react-icons";
import { FiSend } from 'react-icons/fi';

function App() {
  const textRef = useRef();
  const questionRef = useRef();
  const [url, setUrl] = useState();
  const [progress, setProgress] = useState();
  const [chat, setChat] = useState([]);
  let desc = "None";

  function handleQuestionEnter(e) {
    if (e.key === 'Enter') {
      // Ask question
      let text = questionRef.current.value;
      questionRef.current.value = "";
      setChat(oldArray => [...oldArray, ["Question", text]]);

      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      };
      fetch('/ask', requestOptions)
        .then(response => response.json())
        .then(data => {
          setChat(oldArray => [...oldArray, ["Answer", data.answer]]);
        });
    }
  }

  function GenerateTranscript() {
    setProgress("Fetching Transcript...");
    fetch("/gentranscript")
    .then((response) => response.json())
    .then((data) => {
      if (data.Completed === 1) {
        console.log("Transcript loaded.");
        setUrl("https://www.youtube.com/watch?v=" + desc)
        questionRef.current.scrollIntoView();
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
        GenerateTranscript();
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
            chat.map((value) => {
              return (
                <QandA type={value[0]} text={value[1]}/>
              )
            })
          }
        </div>
        <div className="questionInput">
          <input id="questionTextInput" type="text" ref={questionRef} onKeyDown={handleQuestionEnter}/>
          <IconContext.Provider value={{ size: "20px", top: "10px" }}>
            <FiSend />
          </IconContext.Provider>
        </div>
      </div>
		</>
	);
}

export default App;
