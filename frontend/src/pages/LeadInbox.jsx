import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getLeadInbox } from '../api/leads'
import Button from '../components/Button'
import './LeadInbox.css'

function LeadInbox() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadLeads()
  }, [])

  const loadLeads = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getLeadInbox()
      setLeads(data)
    } catch (err) {
      setError(err.message || 'Failed to load leads')
      console.error('Error loading leads:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      new: { label: 'New', class: 'badge-new' },
      needs_info: { label: 'Needs Info', class: 'badge-warning' },
      qualified: { label: 'Qualified', class: 'badge-success' },
      disqualified: { label: 'Disqualified', class: 'badge-danger' },
    }
    const statusInfo = statusMap[status] || { label: status, class: 'badge-secondary' }
    return <span className={`badge ${statusInfo.class}`}>{statusInfo.label}</span>
  }

  const getSourceBadge = (source) => {
    return <span className="badge badge-secondary">{source}</span>
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading leads...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <Button onClick={loadLeads}>Retry</Button>
      </div>
    )
  }

  return (
    <div className="lead-inbox">
      <div className="page-header">
        <h2>Lead Inbox</h2>
        <Button onClick={loadLeads} variant="outline">
          Refresh
        </Button>
      </div>

      {leads.length === 0 ? (
        <div className="empty-state">
          <p>No leads in inbox</p>
          <Link to="/leads/new">
            <Button>Create First Lead</Button>
          </Link>
        </div>
      ) : (
        <div className="leads-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Contact</th>
                <th>Source</th>
                <th>Status</th>
                <th>Missing Fields</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td>
                    <Link to={`/leads/${lead.id}`} className="lead-link">
                      {lead.name || 'N/A'}
                    </Link>
                  </td>
                  <td>
                    <div className="contact-info">
                      {lead.email && <div>{lead.email}</div>}
                      {lead.phone && <div className="text-light">{lead.phone}</div>}
                    </div>
                  </td>
                  <td>{getSourceBadge(lead.source)}</td>
                  <td>{getStatusBadge(lead.status)}</td>
                  <td>
                    {lead.missing_fields && lead.missing_fields.length > 0 ? (
                      <div className="missing-fields">
                        {lead.missing_fields.map((field, idx) => (
                          <span key={idx} className="missing-field-tag">
                            {field}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-light">None</span>
                    )}
                  </td>
                  <td className="text-light">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <Link to={`/leads/${lead.id}`}>
                      <Button variant="outline" style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}>
                        View
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default LeadInbox
