// src/services/backtestService.js
// src/services/BacktestApi.js

class APIClient {
  constructor(baseURL = 'http://127.0.0.1:8000') {
    this.baseURL = baseURL;
  }

  async _handleRequest(endpoint, options) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, options);
      const data = await response.json();
      if (response.ok) {
        return { success: true, data };
      }
      return { success: false, error: data.detail || 'Unknown error' };
    } catch (error) {
      return { success: false, error: error.message || 'Network error' };
    }
  }

  async getBacktest(backtestId) {
    return this._handleRequest(`/backtest/${backtestId}/`, { method: 'GET' });
  }

  async getBacktestsSummaries() {
    return this._handleRequest('/backtest', { method: 'GET' });
  }
}

export default APIClient;

// import axios from 'axios';

// class BacktestApi {
//   constructor() {
//     this.api_url = 'http://127.0.0.1:8000';  // replace with your FastAPI server URL
//     this.client = axios.create({
//       baseURL: this.api_url,
//       timeout: 30000,  // Adjust as needed
//       headers: {
//         Accept: "application/json",
//       },
//     });
//   }

//   getBacktests = async () => {
//     try {
//       const response = await this.client.get("/backtests/");
//       return response.data;
//     } catch (error) {
//       console.error('Error fetching backtests:', error);
//       throw error;
//     }
//   };

//   // Add more methods as needed
//   // getBacktestById = async (id) => { ... }
//   // createBacktest = async (data) => { ... }
//   // updateBacktest = async (id, data) => { ... }
//   // deleteBacktest = async (id) => { ... }
// }

// export default BacktestApi;

