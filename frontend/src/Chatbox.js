import React, { useRef, useState } from "react";
import QandA from './QandA.js';
import { FiSend } from 'react-icons/fi';
import "./Chatbox.css";

function Chatbox(args) {
    const questionRef = useRef();
    const [chat, setChat] = useState([]);
    function setQuestion(e) {
        questionRef.current.value = e.currentTarget.id;
    }
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
        fetch(args.endpoint + '/ask', requestOptions)
          .then(response => response.json())
          .then(data => {
            setChat(oldArray => [["Answer", data.answer, data.stamps], ...oldArray]);
          });
    }
	return (
		<div className="chatbox">
            <div className="questionInput">
                <input id="questionTextInput" type="text" ref={questionRef} onKeyDown={handleQuestionEnter}/>
                <FiSend className="questionButton" onClick={askQuestion} size= "20px" style= {{
                    marginTop: "10px"
                }}/>
            </div>
            <div className="QandA">
                {
                    chat.length > 0 ? 
                    chat.map((value, index) => {
                    return (
                        <QandA key={index} playerRef={args.playerRef} setPlaying={args.setPlaying} type={value[0]} text={value[1]} stamps={value[2]}/>
                    )
                    }) : 
                    <div className="Examples">
                        <div className="ExampleBox" id="What are the main points of the video? "onClick={setQuestion}>
                            <p className="ExampleText">
                                "What are the main points of the video?" 
                                →
                            </p>
                        </div>
                        <div className="ExampleBox" id="Please summarize the video for me." onClick={setQuestion}>
                            <p className="ExampleText">
                                "Please summarize the video for me." 
                                →
                            </p>
                        </div>
                        <div className="ExampleBox" id="Where does the video take place?" onClick={setQuestion}>
                            <p className="ExampleText">
                                "Where does the video take place?" 
                                →
                            </p>
                        </div>
                    </div>
                }
            </div>
      </div>
	);
}

export default Chatbox;
