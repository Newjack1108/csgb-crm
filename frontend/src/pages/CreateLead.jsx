import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createLead } from '../api/leads'
import Button from '../components/Button'
import './CreateLead.css'

function CreateLead() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    source: 'manual',
    name: '',
    email: '',
    phone: '',
    postcode: '',
    product_interest: '',
    timeframe: '',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      const payload = {
        source: formData.source,
        name: formData.name || undefined,
        email: formData.email || undefined,
        phone: formData.phone || undefined,
        raw_payload: {
          postcode: formData.postcode || undefined,
          product_interest: formData.product_interest || undefined,
          timeframe: formData.timeframe || undefined,
        },
      }

      // Remove undefined values
      Object.keys(payload.raw_payload).forEach(
        (key) => payload.raw_payload[key] === undefined && delete payload.raw_payload[key]
      )
      if (Object.keys(payload.raw_payload).length === 0) {
        delete payload.raw_payload
      }

      const lead = await createLead(payload)
      alert('Lead created successfully!')
      navigate(`/leads/${lead.id}`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create lead')
      console.error('Error creating lead:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="create-lead">
      <div className="page-header">
        <h2>Create New Lead</h2>
        <Button variant="outline" onClick={() => navigate('/')}>
          Cancel
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="lead-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label htmlFor="source">Source *</label>
            <select
              id="source"
              name="source"
              value={formData.source}
              onChange={handleChange}
              required
            >
              <option value="manual">Manual</option>
              <option value="website">Website</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Full name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="email@example.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+441234567890"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Additional Information</h3>

          <div className="form-group">
            <label htmlFor="postcode">Postcode</label>
            <input
              type="text"
              id="postcode"
              name="postcode"
              value={formData.postcode}
              onChange={handleChange}
              placeholder="SW1A 1AA"
            />
          </div>

          <div className="form-group">
            <label htmlFor="product_interest">Product Interest</label>
            <input
              type="text"
              id="product_interest"
              name="product_interest"
              value={formData.product_interest}
              onChange={handleChange}
              placeholder="e.g., Solar panels, Heat pumps"
            />
          </div>

          <div className="form-group">
            <label htmlFor="timeframe">Timeframe</label>
            <input
              type="text"
              id="timeframe"
              name="timeframe"
              value={formData.timeframe}
              onChange={handleChange}
              placeholder="e.g., Within 3 months"
            />
          </div>
        </div>

        <div className="form-actions">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Lead'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}

export default CreateLead
