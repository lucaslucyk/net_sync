import React, { Component, useEffect, useState } from "react";
import DataGridDisplay from '../components/DataGridDisplay/DataGridDisplay';
import DataLoaderComponent from '../components/DataLoader/DataLoader';
import Typography from '@material-ui/core/Typography'
import Grid from '@material-ui/core/Grid';


export default function CredentialsPage(props) {
  const CredentialsLoader = DataLoaderComponent(DataGridDisplay);
  const [appState, setAppState] = useState({
    loading: false,
    credentials: null,
    columns: [
      { field: 'id', headerName: 'ID', flex: 0.2 },
      { field: 'company_name', headerName: 'Company', flex: 0.7 },
      { field: 'app_display', headerName: 'Application', flex: 0.7 },
      { field: 'comment', headerName: 'Comment', flex: 0.7 },
    ]
  });

  useEffect(() => {
    setAppState({loading: true});
    const apiUrl = '/api/v2.0/credentials';
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        setAppState({
          loading: false,
          credentials: data.results,
          columns: appState.columns
        });
      })
    }, [setAppState] );

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" color="initial">My credentials</Typography>
        </Grid>
        <Grid item xs={12}>
          <CredentialsLoader
            isLoading={appState.loading}
            data={appState.credentials}
            columns={appState.columns}
          />
        </Grid>
      </Grid>
    )
}
