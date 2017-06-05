import React, { Component } from 'react';
import Product from '../components/product';
import SelectOption from '../components/selectOption';

function returnProduct(category, id, name, description, price, weight) {
    var obj = {};
    obj.category = category;
    obj.id = id;
    obj.name = name;
    obj.description = description + " " + name;
    obj.price = price;
    obj.weight = weight;
    return obj;
}

const productArr = [
    returnProduct('photo', 0, 'mountians', 'this is a photo of', 10, '128 kB'),
    returnProduct('photo', 1, 'water', 'this is a photo of', 15, '128 kB'),
    returnProduct('photo', 2, 'lake', 'this is a photo of', 20, '128 kB'),
    returnProduct('photo', 3, 'ocean', 'this is a photo of', 25, '128 kB'),
    returnProduct('photo', 4, 'river', 'this is a photo of', 30, '128 kB'),
    returnProduct('photo', 5, 'road', 'this is a photo of', 35, '128 kB'),
    returnProduct('photo', 6, 'sky', 'this is a photo of', 40, '128 kB'),
    returnProduct('photo', 7, 'clouds', 'this is a photo of', 45, '128 kB'),
    returnProduct('photo', 8, 'road', 'this is a photo of', 50, '128 kB')
];

class Products extends Component {
    state = {
        searcherText: '',
        sortBy: ''
    }
    
    handleInputChange = (event) => {
        this.setState({
            searcherText: event.target.value
        })
    }
    handleSortChange = (event) => {
        this.setState({
            sortBy: event.target.value
        })
    }
    searcherFilter = (item) => {
        var searchingFor = new RegExp(this.state.searcherText, 'i');
        var found = false;
        var eachField = (a) => {
            if (a.match(searchingFor) != null ? ( a.match(searchingFor).length > 0 ? true : false) : false) 
                {
                    return true;
                }
        }
        for (var value in item) {
            if (eachField(item[value].toString()) ) {return true};
        }
        return found;
    }
    resultsSorter = (a,b) => {
        var sortBy = this.state.sortBy;
        a = a.props.item[sortBy];
        b = b.props.item[sortBy];
        if (sortBy.length < 1) return 0;
        if (a < b) {
               return -1;
         } else   if (a > b)  {
               return 1; 
         } else {
               return 0;
        }
    }
    
    render(){
        return (
        <div>
            <h2>Products</h2>
            <div>
                <label>Search for products</label><br/>
                <input type="text" onChange={this.handleInputChange} /><br/>
                <label>Sort values by</label><br/>
                <select onChange={this.handleSortChange} >
                    <option value="">do not sort</option>
                    {['category', 'id', 'name', 'description', 'price', 'weight'].map(item => <SelectOption key={item} optionValue={item} optionText={item}/>
                    )}
                </select><br/>
            </div>
            <p>You are searching for: {this.state.searcherText}</p>
            <p>You are sorting by: {this.state.sortBy}</p>
            {productArr.filter(product => this.searcherFilter(product)).map(product => <Product key={product.id} item={product} />
                        ).sort(this.resultsSorter)
            }
        </div>
        )
}}
      
      export default Products;