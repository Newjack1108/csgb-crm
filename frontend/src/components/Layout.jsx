import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <h1>CSGB CRM</h1>
          </Link>
          <nav className="nav">
            <Link
              to="/"
              className={location.pathname === '/' ? 'active' : ''}
            >
              Lead Inbox
            </Link>
            <Link
              to="/leads/new"
              className={location.pathname === '/leads/new' ? 'active' : ''}
            >
              Create Lead
            </Link>
          </nav>
        </div>
      </header>
      <main className="main">{children}</main>
    </div>
  )
}

export default Layout
