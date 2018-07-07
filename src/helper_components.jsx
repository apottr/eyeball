import React from 'react'
import { Link } from 'react-router-dom';

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

const Table = (props) => {
	return (
		<table>
			<thead>
				{props.header.map(v => (
					<th>{v}</th>
				))}
			</thead>
			<tbody>
				{props.data.map(v => (
					<tr>
						{v.map(k =>  (
							<td>{k}</td>
						))}
					</tr>
				))}
			</tbody>
		</table>
	)
}

const Empty = (props) => (
	<div><h1>{JSON.stringify(props)}</h1></div>
)

const UnorderedList = (props) => {
	let opts = {}
	let href = ""
	if("opts" in props){
		opts = props.opts
	}
	if ("href" in opts){
		href = opts.href
	}
	const li = props.items.map(v => {
			if(href){
				return (<li key={v[opts.hrefKey]}><Link to={href+v[opts.hrefKey]}>{v[opts.valKey]}</Link></li>)
			}
			return (<li key={v}>{v}</li>)
	})
	return (
		<ul>
			{li}
		</ul>
	)
}

export { SelectOption, UnorderedList, Empty }