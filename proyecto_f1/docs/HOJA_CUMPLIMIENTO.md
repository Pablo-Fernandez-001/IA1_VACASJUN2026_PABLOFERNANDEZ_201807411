# Hoja de Cumplimiento - Doctor Byte Fase 1

| Criterio | Estado | Evidencia |
|---|---|---|
| Hechos, reglas y cortes | Cumple | `doctor_byte.pl` y `doctor_byte_knowledge.pl`. |
| 15 síntomas | Cumple | 25 hechos `symptom/4`. |
| 10 fallas | Cumple | 13 hechos `failure/5`. |
| 10 recomendaciones | Cumple | 26 hechos `recommendation/4`. |
| 10 reglas funcionales | Cumple | 13 hechos `diagnosis_rule/6`. |
| Listas | Cumple | Requeridos, apoyo, faltantes y coincidencias. |
| Python-Prolog | Cumple | `subprocess` ejecuta `doctor_byte_cli`. |
| Endpoints y errores | Cumple | API separada por tags, validación y códigos HTTP. |
| Interfaz | Cumple | Selección, filtros, errores, resultados y reinicio. |
| Historial | Cumple | SQLite auxiliar. |
| CRUD síntomas | Cumple | UI, gateway y Prolog. |
| CRUD fallas | Cumple | UI, gateway y Prolog. |
| CRUD recomendaciones | Cumple | UI, gateway y Prolog. |
| Asociaciones | Cumple | Regla-falla-síntomas-recomendaciones. |
| CRUD reglas | Cumple | Visualizar, crear, editar y eliminar. |
| Configuración | Cumple | ID, estado y mensajes en SQLite. |
| Telegram recibe mensajes | Cumple | Polling `getUpdates`. |
| Telegram comunica backend | Cumple | `/api/symptoms`, `/api/config`, `/api/diagnose`. |
| Documentación | Cumple | Manuales, arquitectura, casos y guía. |
| Docker | Cumple | Compose, healthchecks y volúmenes. |

## Penalizaciones Evitadas

- Prolog y Python son componentes reales y ejecutables.
- Los diagnósticos se calculan en SWI-Prolog.
- Toda la base experta vive en archivos `.pl`, no en SQLite.
- SQLite está limitada y justificada para historial/configuración.
- Token e ID no están quemados en el código.
- CRUD, documentación, diagrama y Docker están presentes.

## Condiciones Externas

El estudiante debe completar entrega UEDI, acceso del repositorio, evidencias visuales, video y defensa técnica.
