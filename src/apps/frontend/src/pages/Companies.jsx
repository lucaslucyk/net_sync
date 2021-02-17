import React, { Component, useEffect, useState } from "react";
import DataGridDisplay from '../components/DataGridDisplay/DataGridDisplay';
import DataLoaderComponent from '../components/DataLoader/DataLoader';
import Typography from '@material-ui/core/Typography'
import Grid from '@material-ui/core/Grid';


export default function CompaniesPage(props) {
  const CompaniesLoader = DataLoaderComponent(DataGridDisplay);
  const [appState, setAppState] = useState({
    loading: false,
    results: null,
    columns: [
      { field: 'id', headerName: 'ID', flex: 0.4 },
      { field: 'name', headerName: 'Name', flex: 0.7 },
      { field: 'country', headerName: 'Country', flex: 0.7 },
      { field: 'city', headerName: 'City', flex: 0.7 },
      { field: 'address', headerName: 'Address', flex: 0.7 },
      { field: 'postal_code', headerName: 'Postal Code', flex: 0.7 },
      { field: 'phone', headerName: 'Phone', flex: 0.7 },
    ]
  });

  useEffect(() => {
    setAppState({loading: true});
    const apiUrl = '/api/v2.0/companies';
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
          <Typography variant="h6" color="initial">My companies</Typography>
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
