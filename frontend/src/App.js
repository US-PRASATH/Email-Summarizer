// src/App.js

import React from 'react';
import './App.css';
import EmailList from './components/EmailList';

const App = () => {
    return (
        <div className="App">
            <h1 className='bg-gray-600'>Email Summarization</h1>
            <EmailList />
        </div>
    );
};

export default App;
