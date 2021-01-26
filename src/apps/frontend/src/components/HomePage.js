import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Link,
  Redirect,
  Route
} from "react-router-dom";


import CredentialListPage from "./CredentialPages";

export default class HomePage extends Component {
  constructor(props){
    super(props);
  }

  render() {
    return( <Router>
      <Switch>
        <Route exact path='/'><p>This is Home Page.</p></Route>
        <Route path='/credentials/list' component={CredentialListPage}></Route>
      </Switch>
    </Router>);
  }
}