import React, { useRef, useState, useEffect } from "react";
import ReactPlayer from 'react-player'
import "./App.css";

function App() {
  const textRef = useRef();
  const [url, setUrl] = useState();

  function HandleAnalyzeClicked(e) {
    // Get input
    let text = textRef.current.value;
    if (text === "") {
      text = "None"
    }
    // Isolate descriptor from youtube link
    let desc = (text.replace("https://", "")).replace("www.youtube.com/watch?v=", "");
    // Create get request
    fetch("/validate/"+desc)
    .then((response) => response.json())
    .then((data) => {
      console.log(data.Valid)
    });
    setUrl("https://www.youtube.com/watch?v=" + desc)
  }

	return (
		<div className="App">
			<header className="App-header">
				<h1>testing</h1>
			</header>
      <h3>
        Enter text:
      </h3>
        <input id="urlInput" name="linkInput" type="text" ref={textRef}/>
        <br/>
        <input type="submit" id="analyzeBtn" value="Analyze" onClick={HandleAnalyzeClicked}/>
        <br/>
        <label>not found.</label>
        <ReactPlayer url={url} />
        <div className="Chatbox">
          
        </div>
		</div>
	);
}

export default App;
