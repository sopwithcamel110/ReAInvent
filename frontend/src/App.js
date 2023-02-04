import React, { useRef, useState, useEffect } from "react";
import "./App.css";

function App() {
  /*
  const [data, setdata] = useState({
      received: 0
    });
    useEffect(() => {
      fetch("/analyze/"+desc).then((res) =>
        res.json().then((data) => {
          setdata({
            received: data.Received
          });
        })
      );
    }, []);
   */
  const textRef = useRef();

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
  }

	return (
		<div className="App">
			<header className="App-header">
				<h1>Youtube Chatbot</h1>
			</header>
      <h3>
        Enter a Youtube link:
      </h3>
        <input id="urlInput" name="linkInput" type="text" ref={textRef}/>
        <br/>
        <input type="submit" id="analyzeBtn" value="Analyze" onClick={HandleAnalyzeClicked}/>
        <br/>
        <label>Video not found.</label>
		</div>
	);
}

export default App;
