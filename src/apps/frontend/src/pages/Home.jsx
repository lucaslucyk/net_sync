import React, { Component } from "react";
import isAuthenticated from '../utils/sessionState';

export default class HomePage extends Component {
  constructor(props){
    super(props);
  }

  render() {
    return <p>Home page: {isAuthenticated().toString()}</p>
  }
}