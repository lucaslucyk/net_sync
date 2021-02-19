
export default function isAuthenticated() {
  return localStorage.getItem('access_token') ? true : false;
}