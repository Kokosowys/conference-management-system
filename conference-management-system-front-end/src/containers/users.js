import React, {Component} from 'react';
import {BrowserRouter, Route, NavLink} from 'react-router-dom'
import User from '../components/user';
import AddPaper from '../components/paper';

class Users extends Component {
    render() {
        return (
            <div>
                <User userToken={this.props.userToken}/>
                <BrowserRouter>
                    <div>
                        <div>
                            <NavLink activeClassName="active" className="routerLink" to="/users/addpaper">Add new paper</NavLink>
                        </div>
                        <div>
                            <Route path='/users/addpaper' component={() => (<AddPaper apiPath={this.props.apiPath}/>)} />
                        </div>
                    </div>
                </BrowserRouter>
            </div>
        )
    }
}

export default Users;