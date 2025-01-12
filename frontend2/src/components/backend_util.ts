import axios from 'axios';

const backendConfig = {
  api_base_url: process.env.IAP_BACKEND_URL
}

const handleApiError = (error: any) => {
    console.error("API Error:", error);
    if (error.response && error.response.status === 401) {
        // Handle unauthorized error (e.g., token expired)
        console.error("Unauthorized access. Redirecting to login.");
        window.location.href = '/login';
    }
    return Promise.reject(error);
};

export const requestFinancialDocumentList = async (companyName: string, idToken: string) => {
    try {
        const response = await axios.get(`${backendConfig.api_base_url}/financial_documents/?company_name=${companyName}`, {
            headers: {
                Authorization: `Bearer ${idToken}`,
            },
        });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestUploadFinancialReport = async (docId: string, idToken: string) => {
    try {
        const response = await axios.post(`${backendConfig.api_base_url}/upload_financial_report/`, { doc_id: docId }, {
            headers: {
                Authorization: `Bearer ${idToken}`,
            },
        });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestAnalyzeFinancialDocument = async (gcsUri: string, idToken: string) => {
    try {
        const response = await axios.post(`${backendConfig.api_base_url}/analyze_financial_document/`, { gcs_uri: gcsUri }, {
            headers: {
                Authorization: `Bearer ${idToken}`,
            },
        });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const requestDownloadFinancialDocument = async (gcsUri: string, idToken: string) => {
    try {
        const response = await axios.post(`${backendConfig.api_base_url}/download_financial_document/`, { gcs_uri: gcsUri }, { responseType: 'blob', headers: { Authorization: `Bearer ${idToken}` } });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};
