import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Replace with your actual API base URL

const handleApiError = (error: any) => {
    console.error("API Error:", error);
    if (error.response && error.response.status === 401) {
        // Handle unauthorized error (e.g., token expired)
        console.error("Unauthorized access. Redirecting to login.");
        window.location.href = '/login';
    }
    return Promise.reject(error);
};

export const requestFinancialDocumentList = async (companyName: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/financial_documents/?company_name=${companyName}`);
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestUploadFinancialReport = async (docId: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/upload_financial_report/`, { doc_id: docId });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestAnalyzeFinancialDocument = async (gcsUri: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/analyze_financial_document/`, { gcs_uri: gcsUri });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestDownloadFinancialDocument = async (gcsUri: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/download_financial_document/`, { gcs_uri: gcsUri }, { responseType: 'blob' });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};
