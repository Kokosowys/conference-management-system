import React from 'react';
import axios from 'axios';
import AddPaperForm from './addPaperForm'

class AddPaper extends React.Component {
    state = {
        formHasErrors: false,
        error: ""
    }
    handleSubmit = (event) => {
        //console.log("validating...");
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
            //console.log("validated");
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
                    'Content-Type': 'application/json',
                    'token': this.state.userToken,
                    'Authorization': `Basic ${hash}`
                },
                data: JSON.stringify(userData)
            }).then((response) => {
                if( response.data.articleId ) {
                    this.handlePaperAdded();
                }
                console.log(response.data.articleId);
            })
        } else {
            document.body.scrollTop = 0;
        };
    }
    handleValidation = (t) => {
        return true;
    }
    handlePaperAdded = () => {
        this.props.handleAddNewPaper(true);
    }
    formErrors = (has) => {
        this.setState({
            formHasErrors: has
        })
    }
    shouldComponentUpdate = () => {
        if (this.props.paperAdded) {
            this.props.handleAddNewPaper(false);
            return true
        }
        return false
    }
    render() {
        const errorsStyle = {
            textAlign: "center",
            padding: 5,
            background: "red",
            color: "#FFF"
        }
        
        const style={
            marginLeft: '25%',
            marginRight: '25%',
            textAlign: 'left'
        }
        var errors = null;
        var content = null;
        if (this.state.formHasErrors) {
            errors = <div style={errorsStyle}><p>{this.state.error}</p></div>
        }
        if (this.props.paperAdded) {
            content = <div>Your paper has been sucessfully added</div>
        } else {
            content = <AddPaperForm handleSubmit={this.handleSubmit} />
        }
        return (
            <div className="userDiv">
                <div style={style}>
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