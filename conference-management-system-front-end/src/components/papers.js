import React, {Component} from 'react';
import axios from 'axios';

class Papers extends Component {
    state = {
        article: {},
        attachments: []
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
                //console.log(response);
                var attachments = [];
                if ( response.data.attachments.length > 0 ) {
                    response.data.attachments.forEach((item) => {
                       attachments.push( this.getAttachment(item.attachmentId) );
                    })
                        
                    
                }
                this.setState({
                    article: response.data,
                    attachments: attachments
                })
            })
    }
    getAttachment = (attachmentId) => {
        const hash = new Buffer(`${this.getProps().userToken}:anything`).toString('base64');
        axios({
                method: 'GET',
                url: this.getProps().apiPath+'/api/articles/attachments/'+attachmentId,
                headers: {
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                //console.log(response);
                return response.data;
            })
    }
    postAttachment = (attachment) => {
        //console.log(attachment);
        var datas = new FormData();
        datas.append('foo', 'bar');
        datas.append('file', attachment);
        const hash = new Buffer(`${this.getProps().userToken}:anything`).toString('base64')
        axios({
            method: 'post',
            url: this.getProps().apiPath+'/api/articles/'+this.getProps().articleId+'/attachments',
            headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': `Basic ${hash}`
            },
            data: datas
        }).then((response) => {
            //console.log(response);
            this.getArticleData();
            return true;
        });
        return false;
    }
    handleFileUpload = (event) => {
        event.preventDefault();
        this.postAttachment(event.target[0].files[0])
    }
    componentWillMount = () => {
        this.componentWillReceiveProps();
    }
    componentWillReceiveProps = () => {
        //console.log(this.props);
        this.getArticleData();
    }
    render() {
        //console.log(this.state.attachments);
        var attachments="";
        if (this.state.article.attachments) {
            attachments = <div>
                    {this.state.article.attachments.map( attachment => <div key={attachment.attachmentId}>   
                        <div><a href={ this.getProps().apiPath+'/api/articles/attachments/'+attachment.attachmentId} target="blank">{attachment.name}</a></div>              
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