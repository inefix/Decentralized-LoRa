import React from "react";
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