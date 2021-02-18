import React, { useEffect } from 'react';
import axiosInstance from '../axios';
import { useHistory } from 'react-router-dom';

export default function LogOut() {
  const history = useHistory();

  useEffect(() => {
    const response = axiosInstance.post('/auth/logout/', {
      refresh_token: sessionStorage.getItem('refresh_token'),
    });
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    axiosInstance.defaults.headers['Authorization'] = null;
    history.push('/login');
  });

  return <div>Logout...</div>;
}