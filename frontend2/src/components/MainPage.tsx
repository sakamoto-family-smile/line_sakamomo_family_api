import React, { useState, useEffect } from 'react';
import { requestFinancialDocumentList, requestUploadFinancialReport, requestAnalyzeFinancialDocument, requestDownloadFinancialDocument } from './backend_util';
import { useNavigate } from 'react-router-dom';

const AUTH_TOKEN_KEY = 'authToken';
const AUTH_TOKEN_EXPIRY_KEY = 'authTokenExpiry';

interface DocumentItem {
    filer_name: string;
    document_description: string;
    doc_id: string;
}

interface DownloadFile {
    filename: string;
    file_data: Blob;
}

const handleTokenExpiration = () => {
    alert("Token Expired! Please relogin.");
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
    sessionStorage.removeItem(AUTH_TOKEN_EXPIRY_KEY);
    window.location.href = '/login';
};

const checkAuthKey = () => {
    const token = sessionStorage.getItem(AUTH_TOKEN_KEY);
    const expiryTime = sessionStorage.getItem(AUTH_TOKEN_EXPIRY_KEY);

    // debug
    console.log("token = " + token)
    console.log("expiryTime = " + expiryTime)

    if (!token || !expiryTime) {
        // debug
        console.log("checkAuthKey is false")

        return false;
    }

    const currentTime = new Date().getTime()

    // debug
    console.log("current time = " + currentTime)
    console.log("parse time = " + parseInt(expiryTime, 10))

    return currentTime < parseInt(expiryTime, 10);
};

const setDocumentList = (documents: DocumentItem[]) => {
    sessionStorage.setItem("document_list", JSON.stringify(documents));
};

const getDocumentList = (): DocumentItem[] => {
    const storedList = sessionStorage.getItem("document_list");
    return storedList ? JSON.parse(storedList) : [];
};

const setDownloadFile = (downloadFile: DownloadFile) => {
    sessionStorage.setItem("download_file", JSON.stringify(downloadFile));
};

const getDownloadFile = (): DownloadFile | null => {
    const storedFile = sessionStorage.getItem("download_file");
    return storedFile ? JSON.parse(storedFile) : null;
};

const FinancialReportAnalysisPage: React.FC = () => {
    const [companyName, setCompanyName] = useState('');
    const [documentList, setDocumentListState] = useState<DocumentItem[]>(getDocumentList());
    const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
    const [analysisResult, setAnalysisResult] = useState<string>('');
    const [downloadFile, setDownloadFileState] = useState<DownloadFile | null>(getDownloadFile());

    useEffect(() => {
        setDocumentListState(getDocumentList());
        setDownloadFileState(getDownloadFile());
    }, []);

    const handleSearch = async () => {
        try {
            const data = await requestFinancialDocumentList(companyName);
            setDocumentListState(data.document_list);
            setDocumentList(data.document_list);
        } catch (error) {
            console.error("Search failed", error);
        }
    };

    const handleAnalyze = async () => {
        if (selectedDocument) {
            try {
                const document = documentList.find(doc => `${doc.filer_name}_${doc.document_description}` === selectedDocument);
                if (document) {
                    const uploadResponse = await requestUploadFinancialReport(document.doc_id);
                    const gcsUri = uploadResponse.gcs_uri;
                    setAnalysisResult(`GCS URI: ${gcsUri}`);
                    const analysisResponse = await requestAnalyzeFinancialDocument(gcsUri);
                    setAnalysisResult(analysisResponse.text);

                    const downloadResponse = await requestDownloadFinancialDocument(gcsUri);
                    const filename = gcsUri.split('/').pop() || 'report.pdf';
                    setDownloadFileState({ filename, file_data: downloadResponse });
                    setDownloadFile({ filename, file_data: downloadResponse });
                }
            } catch (error) {
                console.error("Analysis failed", error);
            }
        }
    };

    const handleDownload = () => {
        if (downloadFile) {
            const url = window.URL.createObjectURL(new Blob([downloadFile.file_data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', downloadFile.filename);
            document.body.appendChild(link);
            link.click();
        }
    };

    return (
        <div>
            <h2>Analysis Financial Report</h2>
            <input
                type="text"
                placeholder="企業名"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
            />
            <button onClick={handleSearch}>検索</button>

            {documentList.length > 0 && (
                <div>
                    <table>
                        <thead>
                            <tr>
                                <th>Filer Name</th>
                                <th>Document Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {documentList.map((item, index) => (
                                <tr key={String(index)}>
                                    <td>{item.filer_name}</td>
                                    <td>{item.document_description}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <select
                        value={selectedDocument || ""}
                        onChange={(e) => setSelectedDocument(e.target.value)}
                    >
                        <option value="">分析したい決算資料を選択してください</option>
                        {documentList.map(item => (
                            <option
                                key={String(item.doc_id)}
                                value={`${item.filer_name}_${item.document_description}`}
                            >
                                {`${item.filer_name}_${item.document_description}`}
                            </option>
                        ))}
                    </select>

                    <button onClick={handleAnalyze}>解析開始</button>

                    {analysisResult && (
                        <div>
                            <h3>解析結果</h3>
                            <p>{analysisResult}</p>
                        </div>
                    )}

                    {downloadFile && (
                        <button onClick={handleDownload}>PDFのダウンロード</button>
                    )}
                </div>
            )}
        </div>
    );
};

const MainPage: React.FC = () => {
    const [activeTab, setActiveTab] = useState('financial_report');

    return (
        <div>
            <h1>Sakamomo-Family-App</h1>
            <button onClick={() => setActiveTab('financial_report')}>決算書分析</button>

            {activeTab === 'financial_report' && <FinancialReportAnalysisPage />}
        </div>
    );
};

const UI: React.FC = () => {
    const navigate = useNavigate();
    useEffect(() => {
        if (!checkAuthKey()) {
            // debug
            console.log("UI move login page")

            navigate('/login');
        }
    }, [navigate]);

    return (
        <div>
            <MainPage />
        </div>
    );
};

export default UI;
