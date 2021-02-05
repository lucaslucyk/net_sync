import axios from 'axios';
import * as actionsTypes from './actionTypes';

export const authStart = () => {
  return {
    type: actionsTypes.AUTH_START
  }
}

export const authSuccess = token => {
  return {
    type: actionsTypes.AUTH_SUCCESS,
    token: token
  }
}

export const authFail = error => {
  return {
    type: actionsTypes.AUTH_FAIL,
    error: error
  }
}

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('expirationDate');
  return {
    type: actionsTypes.AUTH_LOGOUT
  }
}

export const checkAuthTimeout = expirationTime => {
  return dispatch => {
    setTimeOut(() => {
      dispatch(logout());
    }, expirationTime * 1000)
  }
}

export const authLogin = (username, password) => {
  return dispatch => {
    dispatch(authStart());
    axios.post('/auth/token/', {
      username: username,
      password: password
    })
    .then(res => {
      const token = res.data.key;
      const exporationDate = new Date(new Date().getTime() + 3600 * 1000);

      localStorage.setItem('token', token);
      localStorage.setItem('expirationDate', exporationDate);

      dispatch(authSuccess(token));
      dispatch(checkAuthTimeout(3600));

    })
    .catch(err => {
      dispatch(authFail(err));
    })
  }
}

export const authCheckState = () => {
  return dispatch => {
    const token = localStorage.getItem('token');
    if (token === undefined) {
      dispatch(logout());
    } else {
      const expirationDate = new Date(localStorage.getItem('expirationDate'));
      if (expirationDate <= new Date()) {
        dispatch(logout());
      }
      else {
        dispatch(authSuccess(token));
        dispatch(checkAuthTimeout((expirationDate.getTime() - new Date().getTime()) / 1000) );
      }
    }
  }
}