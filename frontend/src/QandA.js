import React from "react";
import "./QandA.css";
import { GoPerson } from 'react-icons/go';

function QandA(args) {
    function seek(e) {
        args.playerRef.current.seekTo(e.target.id);
    }
	return (
		<div className={args.type}>
            <p className={"textArea" + args.type}>
                {args.type === "Answer" ? <img src="/logo512.png" alt="Italian Trulli" style={{
                    width: "40px", height:"40px", padding:"10px"
                }}/> : <></>}
                {args.text}
                {args.type === "Question" ? <GoPerson style= {{
                    width: "40px", height:"40px", padding:"10px"
                }}/> : <></>}
            </p>
            <div>
                {
                    args.stamps.map((value, i) => {
                    return (
                        <input type="submit" id={value} value={"Ref " + (i+1)} onClick={seek}/>
                    )
                    })
                }
            </div>
		</div>
	);
}

export default QandA;
