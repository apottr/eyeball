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

const Tab = (props) => (
	<span>&emsp;</span>
)

const UnorderedList = (props) => {
	const li = props.items.map((v,i) => {
		if("element" in props){
			return (<li key={i}><props.element data={v} /></li>)
		}else{
			return (<li key={i}>{v}</li>)
		}
	})
	return (
		<ul>
			{li}
		</ul>
	)
}

export { SelectOption, UnorderedList, Empty, Tab }