import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  // withCredentials: true,
  headers: {
    "Content-type": "application/json",
    // "Authorization": `Token ${auth_token}`
}
})

export default api;
