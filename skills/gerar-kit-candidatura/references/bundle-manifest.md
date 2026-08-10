# Contrato do manifesto

```json
{
  "bundle_version": 1,
  "candidate_id": "candidata-exemplo",
  "generated_at": "2026-07-29T12:00:00-03:00",
  "global_files": {
    "workbook": "Mapa_de_Oportunidades.xlsx",
    "report_pdf": "Relatorio_Executivo.pdf",
    "archive_zip": "Kit_Candidatura.zip"
  },
  "jobs": [
    {
      "job_id": "vaga-1",
      "score": 85,
      "resume_file": "Curriculo_Vaga_1.docx",
      "resume_pages": 1,
      "resume_visual_reviewed": true,
      "letter_file": "Carta_Vaga_1.docx",
      "letter_pages": 1,
      "letter_visual_reviewed": true
    }
  ]
}
```

Usar `null` nos arquivos não elegíveis. Incluir `manifest.json`, planilha, relatório e todos os documentos esperados dentro do ZIP.
