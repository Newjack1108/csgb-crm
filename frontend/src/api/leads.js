import client from './client'

export const getLeadInbox = async (limit = 100, offset = 0) => {
  const response = await client.get('/api/leads/inbox', {
    params: { limit, offset },
  })
  return response.data
}

export const getLeadDetail = async (leadId) => {
  const response = await client.get(`/api/leads/${leadId}`)
  return response.data
}

export const createLead = async (leadData) => {
  const response = await client.post('/api/leads/', leadData)
  return response.data
}

export const createLeadWebhook = async (source, payload, externalId = null) => {
  const params = externalId ? { external_id: externalId } : {}
  const response = await client.post(`/api/leads/webhook/${source}`, payload, {
    params,
  })
  return response.data
}

export const qualifyLead = async (leadId) => {
  const response = await client.post(`/api/leads/${leadId}/qualify`)
  return response.data
}

export const requestInfo = async (leadId) => {
  const response = await client.post(`/api/leads/${leadId}/request-info`)
  return response.data
}

export const sendSMS = async (leadId, message) => {
  const response = await client.post('/api/comms/sms/send', {
    lead_id: leadId,
    message,
  })
  return response.data
}
