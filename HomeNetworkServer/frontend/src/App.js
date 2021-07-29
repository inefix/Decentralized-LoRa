// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;


import React from "react";
// import Web3 from 'web3';
// import { simpleStorageAbi } from './components/abis';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Navigation, Footer, About, Contact, Devices, Messages, Down } from "./components";
function App() {
  return (
    <div className="App">
      <Router>
        <Navigation />
        <Switch>
          <Route path="/" exact component={() => <Devices />} />
          <Route path="/devices" exact component={() => <Devices />} />
          <Route path="/messages" exact component={() => <Messages />} />
          <Route path="/about" exact component={() => <About />} />
          <Route path="/contact" exact component={() => <Contact />} />
          <Route path="/down" exact component={() => <Down />} />
        </Switch>
        <Footer />
      </Router>
    </div>
  );
}

export default App;