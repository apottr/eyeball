import React from 'react'
import {Redirect} from 'react-router-dom'

const makeFormData = (json) => {
	let f = new FormData()
	for (let key in json) {
		f.append(key,json[key])
	}
	return f
}

class GenericHandler extends React.Component {
	constructor(props){
		super(props)
	}
	componentDidMount(){
		let f = makeFormData(this.props.data)
		fetch(this.props.href,{
			method: "POST",
			body: f
		})
	}
	render(){
		return (
			<Redirect to="/" />
		)
	}
}

const HandleAddSource = (props) => {
	return (
		<GenericHandler 
			href="/api/add-source"
			data={props.location.state} />
	)
}

const HandleAddJob = (props) => {
	return (
		<GenericHandler 
			href="/api/add-job"
			data={props.location.state} />
	)
}

export {HandleAddSource, HandleAddJob} 