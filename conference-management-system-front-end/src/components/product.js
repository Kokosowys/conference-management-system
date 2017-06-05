import React from 'react';

class Product extends React.Component {
    state = {
        clickCount: 0
    }
    handleClickEvent = (event) => {
        this.setState({
            clickCount: this.state.clickCount + 1
        })
    }
    render() {
        var item = this.props.item;
        return (
            <div className="productDiv" data-user-id={item.id}>
            <div style={{
                marginLeft: '25%',
                marginRight: '25%',
                textAlign: 'left'
            }}>
                <span>Category: {item.category}</span><br/>
                <span>No. {item.id}</span><br/>
                <span>Name: {item.name}</span><br/>
                <span>Description: {item.description}</span><br/>
                <span>Price: {item.price}</span><br/>
                <span>Weight/size: {item.weight}</span><br/>
            </div>
            <p>Click count: {this.state.clickCount}</p>
            <button onClick={this.handleClickEvent} title="Click me to change click count!">Click Me</button><br/><br/>
            </div>
            
        )
    }
};

export default Product;