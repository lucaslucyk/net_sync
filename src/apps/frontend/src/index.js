import React from 'react';
import ReactDOM from 'react-dom';
import { ThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import App from './App';

import { createStore, compose, applyMiddleware} from 'redux';
import { Provider } from 'react-redux';
import thunk from 'redux-thunk';

import reducer from './store/reducers/auth';

const composeEnhaces = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const store = createStore(reducer, composeEnhaces(
  applyMiddleware(thunk)
));

const app = (
  <Provider store={store}>
      <App></App>
  </Provider>
)

const theme = createMuiTheme({
  palette: {
    type: "dark",
  }
});

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    {app}
  </ThemeProvider>,
  document.getElementById('app')
);
