import React from 'react';

class User extends React.Component {
    
    render() {
        //var item = this.props.item;
        
        return (
            <div className="userDiv">
            <div>
                <p>Your account id is: {this.props.personId}</p>
            </div>
            <br/><br/>
            </div>
            
        )
    }
};

export default User;