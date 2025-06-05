import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './Components/Dashboard.jsx'
const App = () => {
  return (
    <Routes>
        <Route path='/' element ={<Dashboard></Dashboard>}></Route>
    </Routes>
  )
}

export default App