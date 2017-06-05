import React from 'react';
import axios from 'axios';
import hash from 'object-hash';

class AddUser extends React.Component {
    state = {
        formHasErrors: false
    }
    handleSubmit = (event) => {
        console.log("validating...");
        event.preventDefault();
        if (this.handleValidation(event.target)) {
            console.log("validated");
            this.formErrors(false);
            var userData = {};
            for (var i = 0, iLen = event.target.length -1; i < iLen; i++) {
	           //var Value = this.attribute('name').value;
                let name = event.target[i].name;
                let value = event.target[i].value;
                userData[name] = value;
            }
            delete userData.password2;
            userData.password = hash.sha1(userData.password);
            console.log(JSON.stringify(userData));
            axios({
                method: 'post',
                url: this.props.apiPath+'/api/people',
                withCredentials: true,
                headers: {
                    'Access-Control-Allow-Origin': true,
                    'Content-Type': 'application/json',
                    'withCredentials':true
                },
                data: JSON.stringify(userData)
            }).then((response) => {
                console.log(response);
            })
        } else {
            document.body.scrollTop = 0;
        };
    }
    handleValidation = (t) => {
        if (!this.validatePassword(t.password.value, t.password2.value)) {
            this.formErrors(true);
            console.log(this.state);
            return false;
        }
        console.log(t)
        if (!this.validateAge(t.age.value)) {
            this.formErrors(true);
            console.log(this.state);
            return false;
        }
        if (!this.validateSex(t.sex.value)) {
            this.formErrors(true);
            return false;
        }
        if (!this.validateAcademicDegree(t.academic_degree.value)) {
            this.formErrors(true);
            return false;
        }
        return true;
        
    }
    onFormValidated = () => {
        
    }
    validateAge = (a) => {
        return a >= 18;
    }
    validatePassword = (p1, p2) => {
        return p1 === p2;
    }
    validateSex = (s) => {
        return s !== 0 && s !== "0";
    }
    validateAcademicDegree = (a) => {
        return a !== 0 && a !== "0";
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
            <div className="userDiv">
            <div style={{
                marginLeft: '25%',
                marginRight: '25%',
                textAlign: 'left'
            }}>
                {errors}
                <form onSubmit={this.handleSubmit}>
                <label htmlFor="userName">Name:</label><br/>
                <input type="text" id="userName" name="name" required />
                <br/>
                <label htmlFor="userSurname">Surname:</label><br/>
                <input type="text" id="userSurname" name="surname" required />
                <br/>
                <label htmlFor="password">Password:</label><br/>
                <input type="password" id="password" name="password" minLength="5" maxLength="20" required />
                <br/>
                <label htmlFor="password2">Repeat your password:</label><br/>
                <input type="password" id="password2" name="password2" minLength="5" maxLength="20" required/>
                <br/>
                <label htmlFor="sex">Sex:</label><br/>
                <select id="sex" name="sex" required>
                    <option defaultValue="0">choose Sex</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                </select>
                <br/>
                <label htmlFor="age" required>Age:</label><br/>
                <input type="number" id="age" name="age" />
                    <br/>
                <label htmlFor="academic_degree">Academic degree:</label><br/>
                <select id="academic_degree" name="academic_degree">
                    <option defaultValue="0" >choose Academic degree</option>
                    <option value="BSc">BSc</option>
                    <option value="MSc">MSc</option>
                    <option value="PhD">PhD</option>
                    <option value="Prof">Prof.</option>
                </select>
                    <br/>
                <label htmlFor="userMobile">Mobile number:</label><br/>
                <input type="text" id="userMobile" name="userMobile" pattern=""></input>
                <br/>
                <label htmlFor="userMail">mail:</label><br/>
                <input type="mail" id="userMail" name="userMail" pattern='/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/'></input>
                <br/><br/>
                <input type="submit"/>
                </form>
            </div>
            <br/><br/>
            </div>
            
        )
    }
};

export default AddUser;