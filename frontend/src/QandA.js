import React from "react";
import "./QandA.css";

function QandA(args) {
	return (
		<div className={args.type}>
			{args.text}
		</div>
	);
}

export default QandA;
