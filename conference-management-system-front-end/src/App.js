import React, { Component } from 'react';
import {BrowserRouter, Route, NavLink} from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import Account from './containers/account';
import Products from './containers/products';
import Home from './containers/home';
import ContactForm from './containers/contactForm';
import LogIn from './containers/logIn';
import AddUser from './components/addUser';
import axios from 'axios';

class App extends Component {
    state = {
        userTokenValid: false,
        userToken: window.localStorage.userToken,
        personId: -1,
        isLoggingScreen: false,
        apiPath: "http://skt-site.com:5000"
    }
    handleValidateToken = (userData) => {
        axios({
            method: 'GET',
            url: this.state.apiPath+'/api/token/validate',
            params: {
                token: userData.token
            }
        }).then( (response) => {
            //console.log(response);
            if (response.data.tokenValidation) {
                window.localStorage.setItem("userToken", userData.token);
                if (this.state.isLoggingScreen) {
                    this.setState({
                        userTokenValid: true,
                        userToken: userData.token,
                        isLoggingScreen: false,
                        personId: userData.personId
                    });
                    
                } else {
                    this.setState({
                        userTokenValid: true,
                        userToken: userData.token,
                        isLoggingScreen: false
                    });
                }
                
                //browserHistory.push('/home');
            } else {
                window.localStorage.setItem("userToken", null);
                this.setState({
                    userTokenValid: false,
                    userToken: null,
                    isLoggingScreen: true
                });
            };
        })

    }
    handleLogging = (userData) => {
        //console.log(token);
        if (userData.token) {
            this.handleValidateToken(userData);
        }
    }
    handleIsUserLogged = () => {
        if (this.state.userToken === null) {
            //console.log("validating token");
            this.handleValidateToken(this.state.userToken);
        } 
    }
    handleToLoggingScreen = () => {
        if (window.location.pathname !== "/logIn") {
            this.setState({
                isLoggingScreen: true
            });
            return
        } 
        this.setState({
            isLoggingScreen:false
        });
        return
    }
    componentWillMount = () => {
        if (window.location.pathname.length === 1) {
            window.location.pathname = "/home"
        }
        this.setState({
            userTokenValid: false
        })
        this.handleIsUserLogged();
        return true
    }
    componentWillUpdate = () => {
        if (window.location.pathname.length === 1) {
            window.location.pathname = "/home"
        }
        return true
    }
  render() {
      let loggingRoute = "";
      if (!this.state.isLoggingScreen && window.location.pathname !== "/logIn") {
              loggingRoute = 
                  <div className="headerNav">
                    <NavLink activeClassName="active" className="routerLink" to="/home">Home</NavLink>
                    { this.state.userTokenValid ?
                          <NavLink activeClassName="active" className="routerLink" to="/users">Account</NavLink>
                     :
                        <span>
                            <NavLink activeClassName="active" className="routerLink" to="/logIn" onClick={this.handleToLoggingScreen}>Log In</NavLink>
                            <NavLink activeClassName="active" className="routerLink" to="/register">Register</NavLink>
                        </span>
                      
                    }
                    <NavLink activeClassName="active" className="routerLink" to="/contactForm">Contact</NavLink>
                </div>
              
          } else {
            loggingRoute =
              <div className="headerNav">
                <NavLink activeClassName="active" className="routerLink" to="/home" onClick={this.handleToLoggingScreen}>Home</NavLink>
            </div>
          }
      
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Conference Management System</h2>
            <p>by Marcin Kokoszka & Rafał Sztandera</p>
            <br/>
        </div>
        <BrowserRouter>
            <div>
                {loggingRoute}
                
                <div>
                    <Route path='/register' component={() => <AddUser apiPath={this.state.apiPath}/>} />
                    <Route path='/logIn' component={() => <LogIn handleLogging={this.handleLogging} apiPath={this.state.apiPath} userTokenValid={this.state.userTokenValid}/>} />
                    <Route path='/home' component={Home} />
                    <Route path='/products' component={Products} />
                    <Route path='/users' exact component={() => (<Account apiPath={this.state.apiPath} userToken={this.state.userToken} userTokenValid={this.state.userTokenValid} personId={this.state.personId}/>)}/>
                    <Route path='/contactForm' component={ContactForm} />
                </div>
            </div>
        </BrowserRouter>
      </div>
    );
  }
}

//<NavLink activeClassName="active" className="routerLink" to="/products">Products</NavLink>
export default App;