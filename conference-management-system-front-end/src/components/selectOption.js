import React from 'react';

class SelectOption extends React.Component {
    
    render() {
        return (
            <option value={this.props.optionValue}>{this.props.optionText}</option>
        )
    }
};

export default SelectOption;