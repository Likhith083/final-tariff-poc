import React from 'react'
import { Outlet } from 'react-router-dom'

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">ATLAS Enterprise</h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/" className="text-gray-700 hover:text-gray-900">Dashboard</a>
              <a href="/hts-search" className="text-gray-700 hover:text-gray-900">HTS Search</a>
              <a href="/calculator" className="text-gray-700 hover:text-gray-900">Calculator</a>
              <a href="/sourcing" className="text-gray-700 hover:text-gray-900">Sourcing</a>
              <a href="/ai-chatbot" className="text-gray-700 hover:text-gray-900">AI Assistant</a>
              <a href="/profile" className="text-gray-700 hover:text-gray-900">Profile</a>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
} 