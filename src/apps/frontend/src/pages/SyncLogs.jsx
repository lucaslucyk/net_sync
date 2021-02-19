import React, { Component, useEffect, useState } from "react";
import DataGridDisplay from '../components/DataGridDisplay/DataGridDisplay';
import DataLoaderComponent from '../components/DataLoader/DataLoader';
import Typography from '@material-ui/core/Typography'
import Grid from '@material-ui/core/Grid';
import axiosInstance from '../axios';


export default function CompaniesPage(props) {
  const CompaniesLoader = DataLoaderComponent(DataGridDisplay);
  const [appState, setAppState] = useState({
    loading: false,
    results: null,
    columns: [
      { field: 'id', headerName: 'ID', flex: 0.2},
      { field: 'sync_display', headerName: 'Sync', flex: 1.2},
      { field: 'start_time', headerName: 'Start Time', flex: 0.6, type: 'dateTime'},
      { field: 'end_time', headerName: 'End Time', flex: 0.6, type: 'dateTime'},
      { field: 'ok', headerName: 'OK', flex: 0.2},
    ]
  });

  useEffect(() => {
    setAppState({loading: true});
    axiosInstance.get('sync-history/')
      .then((res) => {
        setAppState({
          loading: false,
          results: res.data.results,
          columns: appState.columns
        });
      })
      .catch((err) => {
        setAppState({
          loading: false,
        });
      });
    }, [setAppState] );

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" color="initial">Sync Logs</Typography>
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
