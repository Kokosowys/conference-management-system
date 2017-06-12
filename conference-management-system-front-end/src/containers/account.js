import React, {Component} from 'react';
import {BrowserRouter, Route, NavLink} from 'react-router-dom'
import axios from 'axios';
import User from '../components/user';
import AddPaper from '../components/addPaper';
import Papers from '../components/papers';
import PaperManage from '../components/paperManage';

class Account extends Component {
    state = {
        paperAdded: false,
        articles: []
    }
    handleAddNewPaper = (paperAdded) => {
        this.setState({
            paperAdded: paperAdded
        });
        this.handleGetArticles();
    }
    handleGetArticles = () => {
        const hash = new Buffer(`${this.props.userToken}:anything`).toString('base64')
        axios({
                method: 'GET',
                url: this.props.apiPath+'/api/articles/author/' + this.props.personId,
                headers: {
                    'Authorization': `Basic ${hash}`
                }
            }).then((response) => {
                //console.log(response);
                this.handleMapArticles(response.data);
            })
    }
    handleMapArticles = (articlesJSON) => {
        this.setState({
            articles: articlesJSON
        })
    }
    componentWillMount = () => {
        this.handleGetArticles();
    }
    render() {
        return (
            <div>
                <User personId={this.props.personId}/>
                <BrowserRouter>
                    <div>
                        <div>
                            <NavLink activeClassName="active" className="routerLink" to="/users/addpaper">Add new paper</NavLink>
                            {this.state.articles.map( article => <NavLink activeClassName="activePaper" className="routerLink" key={article.articleId} to={{
                            pathname:"/users/paperManage/" + article.articleId,
                            params:{
                                articleId:article.articleId,
                                articleName:article.name,
                                userToken:this.props.userToken,
                                apiPath:this.props.apiPath 
                            }}}>{article.name}</NavLink>)}
                        </div>
                        <div>
                            <Route exact path='/users/addpaper' component={() => (<AddPaper apiPath={this.props.apiPath} userToken={this.props.userToken} userTokenValid={this.props.userTokenValid} handleAddNewPaper={this.handleAddNewPaper} paperAdded={this.state.paperAdded} />)} />
                            <Route path='/users/paperManage/:articleId' exact component={Papers} />
                            
                        </div>
                        
                    </div>
                </BrowserRouter>
            </div>
        )
    }
}

export default Account;