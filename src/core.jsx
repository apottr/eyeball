import React from 'react'
import PropTypes from 'prop-types'
import Form from './form.jsx'
import {
	BrowserRouter as Router,
	Route,
	Link,
	Switch,
	Redirect
} from 'react-router-dom'
import {
	HandleAddJob,
	HandleAddSource
} from './form_handlers.jsx'

const ConRouter = () => (
	<Router>
		<Switch>
			<Route exact path="/" component={Homepage} />
			<Route path="/config/add-source" component={HandleAddSource} />
			<Route path="/config/add-job" component={HandleAddJob} />
			<Route path="/config/new-source" component={SourceAdd} />
			<Route path="/config/new-job" component={JobAdd} />
		</Switch>
	</Router>
)

const Homepage = () => (
	<div>
		<h1>Hello World!</h1>
		<Link to="/config/new-source">Add Source</Link>
		<br />
		<Link to="/config/new-job">Add Job</Link>
	</div>
)

const SelectOption = (props) => {
	const li = props.vs.map(v => (
		<option key={v} value={v}>{v}</option>
	))
	return (
		<select name={props.sn}>
			{li}
		</select>
	)
}

class SourceAdd extends React.Component {
	constructor(props){
		super(props)
		this.state = {regions: [], a: ''}
	}
	getRegions(){
		fetch("/api/get_regions")
		.then(r => r.json())
		.then(d => this.setState({regions: d}))
	}
	componentDidMount(){
		this.getRegions()
	}
	render(){
		return (
		<Form to='/config/add-source' method="POST">
			<h1>Add Source</h1>
			<label>Region</label>
			<SelectOption sn="region" vs={this.state.regions} />
        	<label>Command</label>
        	<input type="text" name="cmd" />
        	<button type="submit">Submit Source</button>
		</Form>
		)
	}
}

class JobAdd extends React.Component {
	constructor(props){
		super(props)
		this.state = {sources: []}
	}
	getSources(){
		fetch("/api/get_sources")
		.then(r => r.json())
		.then(d => this.setState({sources: d}))
	}
	componentDidMount(){
		this.getSources()
	}
	sCheckboxes(){
		const a = this.state.sources.map(v => (
			<li>
				<label>{v.cmd}</label>
				<input type="checkbox" name="sources" value={v.id}/>
			</li>
		))
		return a
	}
	render(){
		return (
			<Form to='/config/add-job' method="POST">
				<h1>Add Job</h1>
				<input type="text" name="name" /><br />
            	<label>Sources</label>
				<ul>
					{this.sCheckboxes()}
				</ul>
            	<button type="submit">Submit Job</button>
			</Form>
		)
	}
}


export default ConRouter;
