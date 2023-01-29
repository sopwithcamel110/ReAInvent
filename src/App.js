import './App.css';
import React , { useRef, useState } from 'react';

function App() {
  const linkInputRef = useRef();
  const [ chatBox, updateChatBox ] = useState();
  async function handleAnalyzeClick() {
    let linkInput = linkInputRef.current.value;
    
    chat(linkInput);
  }
  async function chat(url) {
    // link: video url
    // PROCESS LINK HERE
    updateChatBox(url);
  }
  return (
    <>
    <h3>Enter a video link below:</h3>
    <input type="text" ref={linkInputRef}/>
    <input type="button" onClick={handleAnalyzeClick} value="Analyze"/>
    <hr/>
    <div>
      {chatBox}
    </div>
    </>
  );
}

export default App;
