import React from "react";
import "./QandA.css";
import { GoPerson } from 'react-icons/go';

function QandA(args) {
	return (
		<div className={args.type}>
            <p className={"textArea" + args.type}>
                {args.type === "Answer" ? <img src="/logo512.png" alt="Italian Trulli" style={{
                    width: "40px", height:"40px", padding:"10px"
                }}/> : <div/>}
                {args.text}
                {args.type === "Question" ? <GoPerson style= {{
                    width: "40px", height:"40px", padding:"10px"
                }}/> : <div/>}
            </p>
		</div>
	);
}

export default QandA;
