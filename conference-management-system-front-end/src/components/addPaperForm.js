import React, {Component} from 'react';

class AddPaperForm extends Component {
    render() {
        return (
            <form onSubmit={this.props.handleSubmit}>
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
        )
    }
}

export default AddPaperForm;