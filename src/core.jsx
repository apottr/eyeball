import React from 'react'
import PropTypes from 'prop-types'
import {
	BrowserRouter as Router,
	Route,
	Link,
	Switch,
	Redirect
} from 'react-router-dom'
import Form from './form.jsx'
import { HandleAddJob, HandleAddSource } from './form_handlers.jsx'
import { SelectOption, UnorderedList, Empty } from './helper_components.jsx'
import { MapView } from './map_view.jsx'

const ConRouter = () => (
	<Router>
		<Switch>
			<Route exact path="/" component={Homepage} />
			<Route exact path="/config" component={Config} />
			<Route path="/map" component={MapView} />
			<Route path="/config/add-source" component={HandleAddSource} />
			<Route path="/config/add-job" component={HandleAddJob} />
			<Route path="/config/new-source" component={SourceAdd} />
			<Route path="/config/new-job" component={JobAdd} />
			<Route path="/config/job/:id" component={Empty} />
			<Route path="/config/source/:id" component={Empty} />
		</Switch>
	</Router>
)

const Homepage = () => (
	<div>
		<h1>Homepage</h1>
		<Link to="/config">Configure Jobs</Link>
	</div>
)

class Config extends React.Component {
	constructor(props){
		super(props)
		this.state = {sources: [], jobs: [], intervalId: 0}
	}
	getSources(){
		fetch("/api/get-sources")
		.then(r => r.json())
		.then(d => this.setState({sources: d}))
	}
	getJobs(){
		fetch("/api/get-jobs")
		.then(r => r.json())
		.then(d => this.setState({jobs: d}))
	}
	componentDidMount(){
		let self = this
		self.getSources()
		self.getJobs()
		let interval = setInterval(() => {
			self.getSources()
			self.getJobs()
		}, 5000)
		this.setState({intervalId: interval})
	}
	componentWillUnmount(){
		clearInterval(this.state.intervalId)
	}
	render(){
		return(
			<div>
				<h1>Configuration</h1>
				<UnorderedList items={this.state.sources} opts={{
					href: "/config/source/",
					hrefKey: "id",
					valKey: "cmd"
				}} />
				<Link to="/config/new-source">Add Source</Link>
				<br />
				<UnorderedList items={this.state.jobs} opts={{
					href: "/config/job/",
					hrefKey: "id",
					valKey: "name"
				}} />
				<Link to="/config/new-job">Add Job</Link>
			</div>
		)
	}
}

class SourceAdd extends React.Component {
	constructor(props){
		super(props)
		this.state = {regions: [], a: ''}
	}
	getRegions(){
		fetch("/api/get-regions")
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
