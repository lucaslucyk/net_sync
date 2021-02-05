import React from 'react';
import LinearProgress from '@material-ui/core/LinearProgress';

export default function DataLoader(Component) {
  return function DataLoaderComponent({ isLoading, ...props}) {
    if (!isLoading) return <Component {...props} />;
    return <LinearProgress />;
  }
}