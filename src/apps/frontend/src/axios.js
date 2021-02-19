import axios from 'axios';


const baseURL = 'http://localhost:8000/api/v2.0/';
const tokenURL = 'http://localhost:8000/api/v2.0/auth/login/';
const refreshURL = 'http://localhost:8000/api/v2.0/auth/refresh/';

const axiosInstance = axios.create({
  baseURL: baseURL,
  timmeout: 5000,
  headers: {
    Authorization: localStorage.getItem('access_token')
      ? 'JWT ' + localStorage.getItem('access_token')
      : null,
      'Content-Type': 'application/json',
      accept: 'application/json', 
  }
});

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async function (error) {
    const originalRequest = error.config;

    if (typeof error.response === 'undefined'){
      alert(
        'A server/network error ocurred. ' +
        'Looks like CORS might be the problem. ' +
        'Sorry about this - we will get it fixed shortly.'
      );
      return Promise.reject(error);
    }

    if (
      error.response.status === 401 &&
      originalRequest.url === refreshURL
    ) {
      //console.log(originalRequest.url, refreshURL);
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (
      error.response.data.code === 'token_not_valid' &&
      error.response.status === 401 &&
      error.response.statusText === 'Unauthorized'
    ){
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken){
        const tokenParts = JSON.parse(atob(refreshToken.split('.')[1]));

        // exp date in token expressed in seconds, while now() returns miliseconds:
        const now = Math.ceil(Date.now() / 1000);
        //console.log(token.tokenParts.exp);

        if (tokenParts.exp > now) {
          return axiosInstance
          .post(refreshURL, {refresh: refreshToken})
          .then((response) => {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);

            axiosInstance.defaults.headers['Authorization'] = 
              'JWT ' + response.data.access;
            originalRequest.headers['Authorization'] = 
              'JWT ' + response.data.access;

            return axiosInstance(originalRequest);
          })
          .catch((err) => {
            console.log(err);
          });
        } else {
          console.log('Refresh token is expired', tokenParts.exp, now);
          window.location.href = '/login';
        }
      } else {
        console.log('Refresh token not available.');
        window.location.href = '/login';
      }
    }
    //not logued 
    if (
      error.response.data.detail === "Authentication credentials were not provided." &&
      error.response.status === 401
    ) {
      console.log('Session not started');
      window.location.href = '/login';
    }

    // specific error handling done elsewhere
    return Promise.reject(error);
  }
);

export default axiosInstance;