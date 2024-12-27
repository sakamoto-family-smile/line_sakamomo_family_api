select
    docID,
    filerName,
    docDescription
from
    `family_data.edinet_document_metadata`
where
    CONTAINS_SUBSTR(filerName, "{company_name}")
    AND
    CONTAINS_SUBSTR(docDescription, "有価証券報告書")
    AND
    pdfFlag = "1"
order by
    submitDateTime DESC
