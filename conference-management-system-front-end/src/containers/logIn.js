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
            console.log("wrong authorization values");
            return
        }
        this.formErrors(false);
        var userData = {};
        userData.name = event.target.username.value;
        userData.password = hash.sha1(event.target.password.value);
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
                    'Accept':'*/*',
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                //console.log(response);
                this.props.handleLogging(response.data.token)
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
        var errors = null;
        if (this.state.formHasErrors) {
            errors = <div style={errorsStyle}><p>You have errors in your form</p></div>
        }
        return (
            <div>
                <header>
                    <h1>Log In</h1>
                </header>
                <div>
                    {errors}
                    <form onSubmit={this.handleSubmitLogginForm}>
                        <label htmlFor="username">Username</label><br/>
                        <input type="text" id="username" name="username" required/><br/>
                        <label htmlFor="password">Password</label><br/>
                        <input type="password" id="password" name="password" required/><br/><br/>
                        <input type="submit" />
                    </form>
                </div>
            </div>
        )
    }
}
export default Home;