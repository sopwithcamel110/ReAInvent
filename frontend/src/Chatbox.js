import React, { useRef, useState } from "react";
import QandA from './QandA.js';
import { FiSend } from 'react-icons/fi';
import "./Chatbox.css";

function Chatbox(args) {
    const questionRef = useRef();
    const [chat, setChat] = useState([]);
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
        console.log(text);
        fetch(args.endpoint + '/ask', requestOptions)
          .then(response => response.json())
          .then(data => {
            console.log(data.stamps);
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
                    chat.map((value, index) => {
                    return (
                        <QandA key={index} playerRef={args.playerRef} type={value[0]} text={value[1]} stamps={value[2]}/>
                    )
                    })
                }
            </div>
      </div>
	);
}

export default Chatbox;
