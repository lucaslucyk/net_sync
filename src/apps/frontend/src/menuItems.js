// @material-ui/icons
import VpnKeyIcon from '@material-ui/icons/VpnKey';
import SyncIcon from '@material-ui/icons/Sync';
import SyncProblemIcon from '@material-ui/icons/SyncProblem';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import GroupIcon from '@material-ui/icons/Group';
import HelpIcon from '@material-ui/icons/Help';
import HomeIcon from '@material-ui/icons/Home';
import BusinessIcon from '@material-ui/icons/Business';

import HomePage from './pages/Home';
import CompaniesPage from './pages/Companies'
import CredentialsPage from './pages/Credentials';
import SyncPage from './pages/Syncs';
import SyncLogsPage from './pages/SyncLogs';
import ProfilePage from './pages/Profile';
import UserMgmtPage from './pages/UserMgmt';
import HelpPage from './pages/Help';

const menuItems = {
  primary: [{
    name: "Home",
    url: "/",
    exact: true,
    NavIcon: HomeIcon,
    component: HomePage
  },{
    name: "My Companies",
    url: "/companies",
    NavIcon: BusinessIcon,
    component: CompaniesPage
  },,{
    name: "My Credentials",
    url: "/credentials",
    NavIcon: VpnKeyIcon,
    component: CredentialsPage
  },
  {
    name: "My Syncs",
    url: "/syncs",
    NavIcon: SyncIcon,
    component: SyncPage
  },
  {
    name: "Sync Logs",
    url: "/sync-logs",
    NavIcon: SyncProblemIcon,
    component: SyncLogsPage,
    children: [
      {
        name: "Child31",
        url: "/child31",
        NavIcon: VpnKeyIcon,
      },
      {
        name: "Child32",
        url: "/child32",
        NavIcon: VpnKeyIcon,
      }
    ]
  }],
  secondary: [
    {
      name: "My Account",
      url: "/profile",
      NavIcon: AccountCircleIcon,
      component: ProfilePage
    },
    {
      name: "Users Management",
      url: "/user-mgmt",
      NavIcon: GroupIcon,
      component: UserMgmtPage
    },
    {
      name: "Help",
      url: "/help",
      NavIcon: HelpIcon,
      component: HelpPage
    },
  ]
};

export default menuItems;
