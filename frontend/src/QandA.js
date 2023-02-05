import React from "react";
import "./QandA.css";
import { IconContext } from "react-icons";
import { GoPerson } from 'react-icons/go';
import { IoMdBarcode } from 'react-icons/io';

function QandA(args) {
	return (
		<div className={args.type}>
            <div className={"textArea" + args.type}>
                {args.type === "Answer" ? <img src="/logo512.png" alt="Italian Trulli" style={{
                    width: "25px", height:"25px"
                }}/> : <div/>}
                {args.text}
                {args.type === "Question" ? <GoPerson/> : <div/>}
            </div>
		</div>
	);
}

export default QandA;
