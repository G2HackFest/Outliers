import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000";

// Centralized error handling
const handleApiError = (error) => {
  console.error("API Error:", error.response ? error.response.data : error.message);
  throw error.response ? error.response.data : new Error("Network error occurred");
};

// Fetch all cases
export const getCases = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/cases`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Search cases with a query (assumes backend supports POST for search)
export const searchCases = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/cases/search`, { query });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Add a new case
export const addCase = async (caseData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/cases/add`, caseData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Send chat message to chatbot
export const sendChatMessage = async (message) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chatbot`, { message });
    return response.data.reply;
  } catch (error) {
    handleApiError(error);
  }
};