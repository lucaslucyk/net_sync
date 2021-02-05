import React from 'react'
import clsx from 'clsx';
import { fade, makeStyles, useTheme } from '@material-ui/core/styles';
import { Link } from "react-router-dom";
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import {
  Drawer,
  CardMedia,
  List,
  Divider,
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@material-ui/core';

import menuItems from '../../menuItems';


const drawerWidth = 240;
const useStyles = makeStyles((theme) => ({
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
  },
  drawerOpen: {
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerClose: {
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: 'hidden',
    width: theme.spacing(7) + 1,
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9) + 1,
    },
  },
  logoSection: {
    maxWidth: '50%',
    margin: 'auto',
  }
}));

const makeMenu = (menu, level=0) => {
  return menu.map(({name, url, NavIcon, children}) => {
    return (
      <ListItem button key={name} component={Link} to={url}>
        <ListItemIcon><NavIcon /> </ListItemIcon>
        <ListItemText primary={name} />
      </ListItem>
    )
})
}

export default function NavBar(props) {
  const classes = useStyles();
  const theme = useTheme();


  return (
    <Drawer
      variant="permanent"
      className={clsx(classes.drawer, {
        [classes.drawerOpen]: props.open,
        [classes.drawerClose]: !props.open,
      })}
      classes={{
        paper: clsx({
          [classes.drawerOpen]: props.open,
          [classes.drawerClose]: !props.open,
        }),
      }}
    >
      <div className={classes.toolbar}>
        <CardMedia
          className={classes.logoSection}
          component='img'
          src='/static/images/logo_spec.png'
          alt='logo-spec'
          href='/'
        ></CardMedia>
        <IconButton onClick={() => props.handleDrawerClose()}>
          {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </div>
      <Divider />
      <List>
        { makeMenu(menuItems.primary) }
        <Divider />
        { makeMenu(menuItems.secondary) }
      </List>
    </Drawer>
  )
}
