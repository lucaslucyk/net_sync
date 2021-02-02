import React, { Component } from 'react';
import { 
  BrowserRouter,
  Switch,
  Route 
} from 'react-router-dom';

import BaseContainer from './components/Base/Base';
import menuItems from './menuItems';

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
  render() {
    return (
      <BrowserRouter>
        <BaseContainer>
          <Switch>
            { makeRoute(menuItems.primary) }
            { makeRoute(menuItems.secondary) }
          </Switch>
        </BaseContainer>
      </BrowserRouter>
    )
  }
}

export default App;
