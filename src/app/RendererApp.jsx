
import React from "react";
import { Provider } from "react-redux";
import { HashRouter as Router, Switch, Route } from "react-router-dom";
import AppContext from "./contexts/AppContext";
import routes from "./RootRoutes";
import { Store } from "./redux/Store";
import MatxLayout  from "./layout/MatxLayout/Layout2/Layout2";
import MatxTheme  from "./layout/MatxLayout/MatxTheme/MatxTheme";
import MatxSuspense from "./layout/MatxSuspense/MatxSuspense";
import { GlobalCss } from "./layout/styles/GlobalCss";

// import { GlobalCss, MatxSuspense, MatxTheme, MatxLayout } from "./matx";
import sessionRoutes from "./views/sessions/SessionRoutes";
import AuthGuard from "./auth/AuthGuard";
import { AuthProvider } from "./contexts/JWTAuthContext";
import { SettingsProvider } from "./contexts/SettingsContext";

import { useLocation } from 'react-router-dom'
import JwtLogin from "./views/sessions/login/JwtLogin";
import { Redirect, withRouter } from "react-router-dom";
import Dashboard from "./components/dashboard/Accounting/Dashboard";
import Header from "../components/common/header/Header";
import history from "../components/common/history.js";


const RendererApp = () => {

  const location = useLocation();
  console.log("Current Location", location.pathname, location);
  console.log("IN APP");
  console.log("ROutes", routes);

  return (
    <AppContext.Provider value={{ routes }}>
      <Provider store={Store}>
        <SettingsProvider>
          <MatxTheme>
            {/* <GlobalCss /> */}
            <Router history={history}>
              <Header />
              <AuthProvider>
                <MatxSuspense>
                  <Switch>
                    {/* AUTHENTICATION PAGES (SIGNIN, SIGNUP ETC.) */}
                    {sessionRoutes.map((item, i) => (
                      <Route
                        key={indexedDB}
                        path={item.path}
                        component={item.component}
                      />
                    ))}
                    {/* AUTH PROTECTED DASHBOARD PAGES */}

                    <AuthGuard>
                      <Dashboard />
                      {/* <MatxLayout /> */}
                    </AuthGuard>
                    {/* <Route  component={JwtLogin} />
                    <Route render={() => <Redirect to="/"/>}/> */}
                  </Switch>
                </MatxSuspense>
              </AuthProvider>
            </Router>
          </MatxTheme>
        </SettingsProvider>
      </Provider>
    </AppContext.Provider>
  );
};

export default RendererApp;
