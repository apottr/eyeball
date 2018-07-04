import React from 'react'
import { withRouter } from 'react-router-dom'
import getFormData from 'get-form-data'

class Form extends React.Component {
    constructor(props){
        super(props)
        this.submitHandler = this.submitHandler.bind(this)
    }
    submitHandler(event){
        event.preventDefault()
        this.props.history.push({
            pathname: this.props.to,
            state: getFormData(event.target)
        })

    }
    render(){
        return (
            <form action={this.props.to} method={this.props.method} onSubmit={this.submitHandler}>
                {this.props.children}
            </form>
        )
    }
}

export default withRouter(Form)