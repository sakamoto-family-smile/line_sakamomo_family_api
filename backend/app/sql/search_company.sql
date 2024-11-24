select
    docID,
    filerName,
    docDescription
from
    `line_sakamomo_family_api.edinet_document_metadata`
where
    CONTAINS_SUBSTR(filerName, "{company_name}")
    AND
    CONTAINS_SUBSTR(docDescription, "有価証券報告書")
    AND
    pdfFlag = "1"
order by
    submitDateTime DESC
