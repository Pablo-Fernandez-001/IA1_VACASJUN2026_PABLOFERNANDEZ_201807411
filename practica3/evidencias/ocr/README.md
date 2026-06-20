# Evidencia OCR

Al procesar una factura, el backend guarda aqui:

- `*_pagina_*_preprocesada.png`: resultado de escala de grises, binarizacion, limpieza y correccion de inclinacion.
- `*_ocr.txt`: texto bruto obtenido por Tesseract.

Para regenerar evidencia, cargue una factura desde el panel o use `POST /api/invoices/upload`.
