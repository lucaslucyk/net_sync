import Typography from '@material-ui/core/Typography'
import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  dataGrid: {
    height: 400,
    width: '100%'
  },
});

const DataGridDisplay = (props) => {
  const { data } = props;
  const classes = useStyles();

  if (!data || data.length === 0){ 
    return (
      <Typography variant="body1" color="initial">
        No data to display.
      </Typography>
    )
  }

  return (
    <div className={classes.dataGrid}>
      <DataGrid 
        rows={data}
        columns={props.columns}
        pageSize={5}
        checkboxSelection
        //onRowClick={(RowParams) => console.log(RowParams.row)}
      />
    </div>
  );
}

export default DataGridDisplay;