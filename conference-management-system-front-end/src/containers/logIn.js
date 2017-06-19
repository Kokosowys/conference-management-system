import React, { Component } from 'react';
import axios from 'axios';
import hash from 'object-hash';

class Home extends Component {
    state = {
        formHasErrors: false
    }
    handleSubmitLogginForm = (event) => {
        event.preventDefault();
        if (!event.target.username.value && event.target.username.value.length < 5 && !event.target.password.value && event.target.password.value.length < 5) {
            this.formErrors(true);
            //console.log("wrong authorization values");
            return
        }
        this.formErrors(false);
        var userData = {};
        userData.name = event.target.username.value;
        userData.password = hash.sha1(event.target.password.value).substring(0,32);
        console.log(userData.password);
        this.handleLogging(userData);
        //window.location = "/home";
    }
    handleLogging = (userData) => {
        //console.log(userData);
        const hash = new Buffer(`${userData.name}:${userData.password}`).toString('base64')
        axios({
                method: 'GET',
                url: this.props.apiPath+'/api/token/generate',
                headers: {
                    'Access-Control-Allow-Origin':'*',
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                this.setState({
                    formHasErrors: false
                })
                //console.log(response);
                this.props.handleLogging(response.data)
            })
    }
    formErrors = (has) => {
        this.setState({
            formHasErrors: has
        })
    }
    render() {
        const errorsStyle = {
            textAlign: "center",
            padding: 5,
            background: "red",
            color: "#FFF"
        }
        var content = null;
        var errors = null;
        if (this.state.formHasErrors) {
            errors = <div style={errorsStyle}><p>You have errors in your form</p></div>
        }
        if (!this.props.userTokenValid) {
            content = <form onSubmit={this.handleSubmitLogginForm}>
                        <label htmlFor="username">Username</label><br/>
                        <input type="text" id="username" name="username" required/><br/>
                        <label htmlFor="password">Password</label><br/>
                        <input type="password" id="password" name="password" required/><br/><br/>
                        <input type="submit" />
                    </form>
        } else {
            content = <div>You have sucessfully logged in</div>
        }
        return (
            <div>
                <header>
                    <h1>Log In</h1>
                </header>
                <div>
                    {errors}
                    {content}
                    
                </div>
            </div>
        )
    }
}
export default Home;