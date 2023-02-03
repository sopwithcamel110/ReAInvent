import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  // Create state management vars
	const [data, setdata] = useState({
		name: "",
		age: 0,
	});
  // Fetch data from localhost/data and store into name and age
	useEffect(() => {
		fetch("/data").then((res) =>
			res.json().then((data) => {
				setdata({
					name: data.Name,
					age: data.Age,
				});
			})
		);
	}, []);

	return (
		<div className="App">
			<header className="App-header">
				<h1>React and flask</h1>
				<p>{data.name}</p>
				<p>{data.age}</p>
			</header>
      <h3>
        Enter a Youtube link:
      </h3>
      <form action="/" method="POST">
          <input id="urlInput" name="linkInput" type="text"/>
          <br/>
          <input type="submit" id="analyzeBtn" value="Analyze"/>
      </form>
		</div>
	);
}

export default App;
