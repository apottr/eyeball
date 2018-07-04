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

const ConRouter = () => (
	<Router>
		<Switch>
			<Route exact path="/" component={Homepage} />
			<Route path="/config/add-source" component={HandleAddSource} />
			<Route path="/config/new-source" component={SourceAdd} />
		</Switch>
	</Router>
)

const Homepage = () => (
	<div>
		<h1>Hello World!</h1>
		<Link to="/config/new-source">Add Source</Link>
	</div>
)

class HandleAddSource extends React.Component {
	constructor(props){
		super(props)
	}
	componentDidMount(){
		console.log(this.props.location.state)
	}
	render(){
		return (
			<Redirect to="/" />
		)
	}
}

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


export default ConRouter;
