import React from 'react';
import axios from 'axios';

class AddPaper extends React.Component {
    state = {
        formHasErrors: false,
        paperAdded: false,
        error: ""
    }
    handleSubmit = (event) => {
        console.log("validating...");
        event.preventDefault();
        if (!this.props.userTokenValid) {
            this.formErrors(true);
            this.setState({
                error: "Your session has expired, you must log in again"
            })
            document.body.scrollTop = 0;
            return
        }
        if (this.handleValidation(event.target)) {
            console.log("validated");
            this.formErrors(false);
            this.setState({
                error: "You have errors in your form"
            })
            var userData = {};
            for (var i = 0, iLen = event.target.length -1; i < iLen; i++) {
	           //var Value = this.attribute('name').value;
                let name = event.target[i].name;
                let value = event.target[i].value;
                userData[name] = value;
            }
            const hash = new Buffer(`${this.props.userToken}:password`).toString('base64');
            axios({
                method: 'post',
                url: this.props.apiPath+'/api/articles',
                headers: {
                    'token': this.state.userToken,
                    'Authorization': `Basic ${hash}`
                },
                data: JSON.stringify(userData)
            }).then((response) => {
                if( response.articleId ) {
                    this.handlePaperAdded();
                }
                console.log(response);
            })
        } else {
            document.body.scrollTop = 0;
        };
    }
    handleValidation = (t) => {
        return true;
    }
    handlePaperAdded = () => {
        this.setState({
            paperAdded: true
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
        var content = null;
        if (this.state.formHasErrors) {
            errors = <div style={errorsStyle}><p>{this.state.error}</p></div>
        }
        if (this.state.paperAdded) {
            content = <div>Your paper has been sucessfully added</div>
        } else {
            content = <form onSubmit={this.handleSubmit}>
                <label htmlFor="userName">Name:</label><br/>
                <input type="text" id="userName" name="name" required />
                <br/>
                <label htmlFor="theme">Theme:</label><br/>
                <input type="text" id="theme" name="theme" required />
                <br/>
                <label htmlFor="label">Label:</label><br/>
                <input type="text" id="label" name="label" required />
                <br/>
                <label htmlFor="description" required>Description:</label><br/>
                <textarea id="description" name="description" ></textarea>
                <br/>
                <label htmlFor="text" required>Text:</label><br/>
                <textarea id="text" name="text" ></textarea>
                <br/><br/>
                <input type="submit"/>
                </form>
        }
        return (
            <div className="userDiv">
            <div style={{
                marginLeft: '25%',
                marginRight: '25%',
                textAlign: 'left'
            }}>
                {errors}
                <br/>
                {content}
            </div>
            <br/><br/>
            </div>
            
        )
    }
};

export default AddPaper;