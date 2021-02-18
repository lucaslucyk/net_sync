import React, { Component } from 'react';
import { 
  BrowserRouter,
  Switch,
  Route 
} from 'react-router-dom';
import { connect } from 'react-redux';
import BaseContainer from './components/Base/Base';
import menuItems from './menuItems';
import LogIn from './pages/LogIn';
import LogOut from './pages/LogOut';
import * as actions from './store/actions/auth';

const makeRoute = (menu, level=0) => {
  return menu.map(({name, url, component, exact}) => {
    return (
      <Route 
        exact={exact? 'true': 'false'}
        path={url}
        component={component}>
      </Route>
    )
  })
}

class App extends Component {

  componentDidMount(){
    this.props.onTryAutoSignup();
  }

  render() {
    return (
      <BrowserRouter>
        <BaseContainer {...this.props}>
          <Switch>
            <Route 
              path='/login'
              component={LogIn}>
            </Route>
            <Route 
              path='/logout'
              component={LogOut}>
            </Route>
            { makeRoute(menuItems.primary) }
            { makeRoute(menuItems.secondary) }
          </Switch>
        </BaseContainer>
      </BrowserRouter>
    )
  }
}

const mapStateToProps = state => {
  return {
    isAuthenticated: state.token != null
  }
}

const mapDispatchToprops = dispatch => {
  return {
    onTryAutoSignup: () => dispatch(actions.authCheckState())
  }
}

export default connect(mapStateToProps, mapDispatchToprops)(App);
//export default App;