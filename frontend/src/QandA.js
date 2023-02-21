import React from "react";
import "./QandA.css";
import { GoPerson } from 'react-icons/go';
import * as Scroll from 'react-scroll';

function QandA(args) {
    function seek(e) {
        args.playerRef.current.seekTo(e.target.id);
        Scroll.animateScroll.scrollTo(420);
        args.setPlaying(true);
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
            <div className="answerDetails">
                {
                    args.type === "Answer" ? "References: " : <></>
                }
                {
                    args.stamps.map((value, i) => {
                    return (
                        <input className="ref" type="submit" id={value} value={(i+1)} onClick={seek}/>
                    )
                    })
                }
            </div>
		</div>
	);
}

export default QandA;
