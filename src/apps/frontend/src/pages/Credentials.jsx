import React, { Component, useEffect, useState } from "react";
import DataGridDisplay from '../components/DataGridDisplay/DataGridDisplay';
import DataLoaderComponent from '../components/DataLoader/DataLoader';
import Typography from '@material-ui/core/Typography'
import Grid from '@material-ui/core/Grid';


export default function CredentialsPage(props) {
  const CredentialsLoader = DataLoaderComponent(DataGridDisplay);
  const [appState, setAppState] = useState({
    loading: false,
    credentials: null
  });

  useEffect(() => {
    setAppState({loading: true});
    const apiUrl = '/api/credentials/list';
    fetch(apiUrl)
      .then((data) => data.json())
      .then((credentials) => {
        setAppState({loading: false, credentials: credentials});
      })
    }, [setAppState] );

    // datagrid headers
    const columns = [
      { field: 'id', headerName: 'ID', width: 70 },
      { field: 'company', headerName: 'Company', width: 130 },
      { field: 'application', headerName: 'Application', width: 130 },
      { field: 'comment', headerName: 'Comment', width: 130 },
    ];
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" color="initial">My credentials</Typography>
        </Grid>
        <Grid item xs={12}>
          <CredentialsLoader
            isLoading={appState.loading}
            data={appState.credentials}
            columns={columns}
          />
        </Grid>
      </Grid>
    )
}
