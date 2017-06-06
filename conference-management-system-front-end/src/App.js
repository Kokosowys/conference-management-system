import React, { Component } from 'react';
import {BrowserRouter, Route, NavLink} from 'react-router-dom'
import logo from './logo.svg';
import './App.css';
import Users from './containers/users';
import Products from './containers/products';
import Home from './containers/home';
import ContactForm from './containers/contactForm';
import LogIn from './containers/logIn';
import AddUser from './components/addUser';
import axios from 'axios';
import axiosMethodOverride from 'axios-method-override';

class App extends Component {
    state = {
        userTokenValid: false,
        userToken: window.localStorage.userToken,
        isLoggingScreen: false,
        apiPath: "http://skt-site.com:5000"
    }
    handleValidateToken = (tokenz) => {
        const hash = new Buffer(`token:${tokenz}`).toString('base64');
        var tokenJSON = {token:tokenz};
        axios({
            method: 'get',
            url: this.state.apiPath+'/api/token/validate',
            params: tokenJSON
        }).then( (response) => {
            //console.log(response);
            if (response.data.tokenValidation) { 
                this.setState({
                    userTokenValid: true,
                    userToken: tokenz
                });
                window.localStorage.setItem("userToken", tokenz);
            } else {
                this.setState({
                    userTokenValid: false,
                    userToken: null
                })
                window.localStorage.setItem("userToken", null)
            };
        })

    }
    handleLogging = (token) => {
        //console.log(token);
        this.handleValidateToken(token);
        if (this.state.isLoggingScreen) {
            this.setState({
                isLoggingScreen:false
            });
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
          <h2>This site is based on React! &lt;3</h2>
        </div>
        <BrowserRouter>
            <div>
                {loggingRoute}
                
                <div>
                    <Route path='/register' component={() => <AddUser apiPath={this.state.apiPath}/>} />
                    <Route path='/logIn' component={() => <LogIn handleLogging={this.handleLogging} apiPath={this.state.apiPath}/>} />
                    <Route path='/home' component={Home} />
                    <Route path='/products' component={Products} />
                    <Route path='/users' component={() => (<Users apiPath={this.state.apiPath} userToken={this.state.userToken} userTokenValid={this.state.userTokenValid} />)}/>
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