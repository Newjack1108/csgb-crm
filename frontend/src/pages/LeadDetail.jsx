import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getLeadDetail, qualifyLead, requestInfo, sendSMS } from '../api/leads'
import Button from '../components/Button'
import './LeadDetail.css'

function LeadDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [leadData, setLeadData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [smsMessage, setSmsMessage] = useState('')
  const [showSmsForm, setShowSmsForm] = useState(false)

  useEffect(() => {
    loadLead()
  }, [id])

  const loadLead = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getLeadDetail(id)
      setLeadData(data)
    } catch (err) {
      setError(err.message || 'Failed to load lead')
      console.error('Error loading lead:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleQualify = async () => {
    if (!confirm('Are you sure you want to qualify this lead? This will create an opportunity.')) {
      return
    }

    try {
      setActionLoading(true)
      await qualifyLead(id)
      alert('Lead qualified successfully!')
      loadLead()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to qualify lead')
    } finally {
      setActionLoading(false)
    }
  }

  const handleRequestInfo = async () => {
    try {
      setActionLoading(true)
      await requestInfo(id)
      alert('Info request sent. Automation will follow up via SMS.')
      loadLead()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to request info')
    } finally {
      setActionLoading(false)
    }
  }

  const handleSendSMS = async () => {
    if (!smsMessage.trim()) {
      alert('Please enter a message')
      return
    }

    try {
      setActionLoading(true)
      await sendSMS(id, smsMessage)
      alert('SMS sent successfully!')
      setSmsMessage('')
      setShowSmsForm(false)
      loadLead()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send SMS')
    } finally {
      setActionLoading(false)
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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading lead...</p>
      </div>
    )
  }

  if (error || !leadData) {
    return (
      <div className="error-container">
        <p className="error-message">{error || 'Lead not found'}</p>
        <Button onClick={() => navigate('/')}>Back to Inbox</Button>
      </div>
    )
  }

  const { lead, customer, timeline } = leadData

  return (
    <div className="lead-detail">
      <div className="detail-header">
        <div>
          <Button variant="outline" onClick={() => navigate('/')}>
            ← Back
          </Button>
          <h2 style={{ marginTop: '1rem' }}>{lead.name || 'Unnamed Lead'}</h2>
        </div>
        <div className="actions">
          {lead.status === 'new' && lead.missing_fields?.length === 0 && (
            <Button
              onClick={handleQualify}
              disabled={actionLoading}
              variant="success"
            >
              Qualify Lead
            </Button>
          )}
          {lead.status === 'needs_info' && (
            <Button
              onClick={handleRequestInfo}
              disabled={actionLoading}
              variant="warning"
            >
              Request Info (Auto)
            </Button>
          )}
          {lead.phone && (
            <Button
              onClick={() => setShowSmsForm(!showSmsForm)}
              variant="primary"
            >
              Send SMS
            </Button>
          )}
        </div>
      </div>

      {showSmsForm && (
        <div className="sms-form">
          <h3>Send SMS</h3>
          <textarea
            value={smsMessage}
            onChange={(e) => setSmsMessage(e.target.value)}
            placeholder="Enter your message..."
            rows="4"
          />
          <div className="form-actions">
            <Button onClick={handleSendSMS} disabled={actionLoading}>
              Send
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowSmsForm(false)
                setSmsMessage('')
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      <div className="detail-grid">
        <div className="detail-card">
          <h3>Lead Information</h3>
          <div className="info-row">
            <span className="label">Status:</span>
            <span>{getStatusBadge(lead.status)}</span>
          </div>
          <div className="info-row">
            <span className="label">Source:</span>
            <span>{lead.source}</span>
          </div>
          <div className="info-row">
            <span className="label">Name:</span>
            <span>{lead.name || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="label">Email:</span>
            <span>{lead.email || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="label">Phone:</span>
            <span>{lead.phone || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="label">Created:</span>
            <span>{new Date(lead.created_at).toLocaleString()}</span>
          </div>
          {lead.missing_fields && lead.missing_fields.length > 0 && (
            <div className="info-row">
              <span className="label">Missing Fields:</span>
              <div className="missing-fields">
                {lead.missing_fields.map((field, idx) => (
                  <span key={idx} className="missing-field-tag">
                    {field}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {customer && (
          <div className="detail-card">
            <h3>Customer</h3>
            <div className="info-row">
              <span className="label">Name:</span>
              <span>{customer.name || 'N/A'}</span>
            </div>
            <div className="info-row">
              <span className="label">Email:</span>
              <span>{customer.primary_email || 'N/A'}</span>
            </div>
            <div className="info-row">
              <span className="label">Phone:</span>
              <span>{customer.primary_phone || 'N/A'}</span>
            </div>
            <div className="info-row">
              <span className="label">Status:</span>
              <span>{customer.status}</span>
            </div>
          </div>
        )}

        <div className="detail-card timeline-card">
          <h3>Timeline</h3>
          {timeline && timeline.length > 0 ? (
            <div className="timeline">
              {timeline.map((event) => (
                <div key={event.id} className="timeline-item">
                  <div className="timeline-marker"></div>
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <span className="timeline-channel">{event.channel}</span>
                      <span className="timeline-direction">{event.direction}</span>
                      <span className="timeline-date">
                        {new Date(event.created_at).toLocaleString()}
                      </span>
                    </div>
                    {event.subject && (
                      <div className="timeline-subject">{event.subject}</div>
                    )}
                    <div className="timeline-body">{event.body}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-light">No timeline events yet</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default LeadDetail
