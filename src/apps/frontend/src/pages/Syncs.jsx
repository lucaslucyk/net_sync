import React, { Component, useEffect, useState } from "react";
import DataGridDisplay from '../components/DataGridDisplay/DataGridDisplay';
//import XGridDisplay from '../components/XGridDisplay/XGridDisplay';
import DataLoaderComponent from '../components/DataLoader/DataLoader';
import Typography from '@material-ui/core/Typography'
import Grid from '@material-ui/core/Grid';


export default function CompaniesPage(props) {
  const CompaniesLoader = DataLoaderComponent(DataGridDisplay);
  const [appState, setAppState] = useState({
    loading: false,
    results: null,
    columns: [
      { field: 'id', headerName: 'ID', flex: 0.2},
      { field: 'synchronize_display', headerName: 'Sync type', flex: 0.5},
      { field: 'origin_display', headerName: 'From', flex: 0.8},
      { field: 'destiny_display', headerName: 'To', flex: 0.8},
      { field: 'cron_expression', headerName: 'Cron', flex: 0.5},
      { field: 'active', headerName: 'Active', flex: 0.3},
      { field: 'status_display', headerName: 'Status', flex: 0.5},
    ]
  });

  useEffect(() => {
    setAppState({loading: true});
    const apiUrl = '/api/v2.0/syncs';
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        setAppState({
          loading: false,
          results: data.results,
          columns: appState.columns
        });
      })
    }, [setAppState] );

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" color="initial">My syncs</Typography>
        </Grid>
        <Grid item xs={12}>
          <CompaniesLoader
            isLoading={appState.loading}
            data={appState.results}
            columns={appState.columns}
          />
        </Grid>
      </Grid>
    )
}
