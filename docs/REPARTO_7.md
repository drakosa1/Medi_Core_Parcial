# Plan de integración para 7 integrantes

La versión completa es una base de trabajo asistida por IA: cada integrante debe revisar, adaptar, probar y explicar sus aportes. Completar el prompt real y la validación en la plantilla de cada PR. No atribuir a compañeros cambios que no realizaron ni crear evidencia simulada.

| Integrante | Célula / rama | Aporte |
|---|---|---|
| 1 | GitMaster · `chore/integracion` | src/main.py, main.py, requirements.txt, tests/test_domain.py, documentación y workflow |
| 2 | Dominio · `feature/dominio-modelos` | Entidad, Persona, Paciente y Medico en src/domain/models.py |
| 3 | Dominio · `feature/dominio-validaciones` | src/domain/exceptions.py; Cita y RegistroClinico y validaciones coordinadas en src/domain/models.py |
| 4 | Servicios · `feature/servicios-citas` | src/services/app_service.py |
| 5 | Datos · `feature/datos-json` | src/services/data_manager.py |
| 6 | Interfaz · `feature/interfaz-principal` | src/ui/cli_interface.py |
| 7 | Interfaz · `feature/interfaz-agenda` | src/ui/widgets.py y src/ui/assets/: tablas, scroll, estilos y recursos; nombre de rama conservado del plan inicial |

Los integrantes 2 y 3 comparten models.py: integrar primero la parte 2 y luego sincronizar la rama 3; aplicar únicamente sus clases y cambios acordados. No repartir a ambos una copia completa del mismo archivo para que la sobrescriban. Esta distribución se adapta al código entregado; no hay siete paquetes individuales en este ZIP.

Orden sugerido de PR: dominio 2 → dominio 3 → datos 5 → servicios 4 → componentes 7 → interfaz 6 → integración 1. Cada PR tiene su commit y autor reales. Ejecutar las pruebas cuando estén integradas las dependencias. GitMaster revisa Files changed y funcionalidad antes del merge; otro integrante revisa su PR.

La evaluación exige como mínimo un commit y un PR fusionado por cada uno de los siete. Completar antes del congelamiento de main una hora antes de clase. Guardar enlaces a PR, validaciones reales y resolución de conflictos si ocurre. El programa completo por sí solo no acredita esos requisitos.

## Ejemplo en Git Bash

```bash
git switch main
git pull origin main
git switch -c feature/datos-json
# Incorporar el archivo asignado y comprobarlo.
git add src/services/data_manager.py
git commit -m "feat: implementar persistencia JSON segura"
git push -u origin feature/datos-json
```

Abrir PR hacia main y completar la plantilla. Los demás cambian rama y rutas según su aporte. No incluir data/ ni carpetas de caché.
