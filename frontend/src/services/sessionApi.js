import axios from 'axios';

// The base URL for your FastAPI backend
const API_URL = 'http://127.0.0.1:8000';

/**
 * Uploads a resume file to the backend.
 * @param {File} file - The resume file to upload.
 * @param {string} token - The user's JWT authentication token.
 * @returns {Promise<object>} The server's response, containing the extracted text.
 */
export const uploadResume = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    // Corrected the endpoint from "upload_resume" to "upload-resume"
    const response = await axios.post(`${API_URL}/session/upload_resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error uploading resume:", error.response?.data || error.message);
    // Re-throw the specific error detail from the backend if it exists
    throw error.response?.data || new Error("An unknown error occurred during file upload.");
  }
};

/**
 * Starts an interview session with pasted resume text.
 * @param {string} text - The raw resume text.
 * @param {string} token - The user's JWT authentication token.
 * @returns {Promise<object>} The server's response, likely the first question.
 */
export const startInterviewWithText = async (text, token) => {
  try {
    const response = await axios.post(`${API_URL}/session/start-with-text`, {
      resume_text: text
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error starting interview with text:", error.response?.data || error.message);
    throw error.response?.data || new Error("An unknown error occurred while starting the interview.");
  }
};

