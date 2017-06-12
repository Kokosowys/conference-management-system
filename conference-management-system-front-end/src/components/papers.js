import React, {Component} from 'react';
import {BrowserRouter, Route, NavLink} from 'react-router-dom';
import axios from 'axios';
import PaperManage from '../components/paperManage';

class Papers extends Component {
    state = {
        article: {}
    }
    getProps = () => {
        return this.props.location.params;
    }
    getArticleData = () => {
        const hash = new Buffer(`${this.getProps().userToken}:anything`).toString('base64')
        axios({
                method: 'GET',
                url: this.getProps().apiPath+'/api/articles/'+this.getProps().articleId,
                headers: {
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                console.log(response);
                var attachments = [];
                if ( response.data.attachments.length > 0 ) {
                    for ( let attachment in response.data.attachments ) {
                        this.getAttachment(attachment.attachmentId);
                    }
                }
                this.setState({
                    article: response.data
                })
            })
    }
    getAttachment = (attachmentId) => {
        const hash = new Buffer(`${this.getProps().userToken}:anything`).toString('base64')
        axios({
                method: 'GET',
                url: this.getProps().apiPath+'/api/articles/attachments/'+attachmentId,
                headers: {
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                console.log(response);
                //return response.data;
            })
    }
    postAttachment = (attachment) => {
        console.log(attachment);
        const hash = new Buffer(`${this.getProps().userToken}:anything`).toString('base64')
        axios({
                method: 'post',
                url: this.getProps().apiPath+'/api/articles/'+this.getProps().articleId+'/attachments',
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Basic ${hash}`
                },
                data: {attachment}
            }).then((response) => {
                console.log(response);
            return true;
            });
        return false;
    }
    handleFileUpload = (event) => {
        event.preventDefault();
        this.postAttachment(event.target[0].files[0]) ? event.target.reset : "";
    }
    componentWillMount = () => {
        this.componentWillReceiveProps();
    }
    componentWillReceiveProps = () => {
        //console.log(this.props);
        this.getArticleData();
    }
    render() {
        var attachments="";
        if (this.state.article.attachments) {
            attachments = <div>
                    {this.state.article.attachments.map( attachment => <div>   
                        <p onClick={this.getAttachment(attachment.attachmentId)}>{attachment.attachmentId}</p>              
                    </div>)}
                </div>
        }
        return (
            <div>
                <p>{this.state.article.name}</p>
                <p>{this.state.article.theme}</p>
                <p>{this.state.article.description}</p>
                <p>{this.state.article.label}</p>
                <p>{this.state.article.text}</p> 
                {attachments}
                <form onSubmit={this.handleFileUpload}>
                <label htmlFor="addFileToArticle">Attach file to this article</label><br/>
                <input type="file" id="addFileToArticle" name="files" accept="*/*" />
                <input type="submit" value="Submit your file" />
                </form>
            </div>
        )
    }
}

export default Papers;

/*
<BrowserRouter>
                    <div>
                        <div>
                            <NavLink exact strict activeClassName="active" className="managePaperLink" to={pathTo} >Manage paper</NavLink>
                        </div>
                        <div>
                            <Route path='/users/paperManage/:articleId/manage' exact component={() => (<PaperManage articleName={this.props.articleName}/>)} />
                        </div>
                    </div>
                </BrowserRouter>
*/