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
			<Redirect to={this.props.redirectHref} />
		)
	}
}

const HandleAddSource = (props) => {
	return (
		<GenericHandler 
			href="/api/add-source"
			redirectHref="/config"
			data={props.location.state} />
	)
}

const HandleDelSource = (props) => {
	return (
		<GenericHandler
			href="/api/del-source"
			redirectHref="/config"
			data={{id: props.match.params.id}}
		/>
	)
}

const HandleDelJob = (props) => {
	return (
		<GenericHandler
			href="/api/del-job"
			redirectHref="/config"
			data={{id: props.match.params.id}}
		/>
	)
}

const HandleAddJob = (props) => {
	return (
		<GenericHandler 
			href="/api/add-job"
			redirectHref="/config"
			data={props.location.state} />
	)
}

export {
	HandleAddSource, 
	HandleAddJob, 
	HandleDelSource, 
	HandleDelJob
} 