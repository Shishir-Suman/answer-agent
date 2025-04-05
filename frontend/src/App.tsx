import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        <ChatInterface />
      </main>
      <footer className="bg-gray-100 py-4 text-center text-gray-600 text-sm">
        <div className="container mx-auto">
          Answer Agent &copy; {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  )
}

export default App 