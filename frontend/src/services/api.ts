import axios from 'axios'

const API_URL = '/api'

export const submitQuery = async (query: string): Promise<any> => {
  try {
    const response = await axios.post(`${API_URL}/query`, { query })
    return response.data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export default {
  submitQuery
} 