import React from "react";
import "./QandA.css";
import { IconContext } from "react-icons";
import { GoPerson } from 'react-icons/go';
import { IoMdBarcode } from 'react-icons/io';

function QandA(args) {
	return (
		<div className={args.type}>
            <div className={"textArea" + args.type}>
                <IconContext.Provider value={{ size: "25px" }}>
                    {args.type === "Answer" ? <IoMdBarcode/> : <div/>}
                    {args.text}
                    {args.type === "Question" ? <GoPerson/> : <div/>}
                </IconContext.Provider>
            </div>
		</div>
	);
}

export default QandA;
