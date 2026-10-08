# MediCore · Gestión del centro médico

Sistema de escritorio operado por el encargado del centro médico. El centro presta servicios directamente al paciente (B2C); el paciente no utiliza la aplicación. Se mantiene la estructura obligatoria de la evaluación.

## Ejecutar

Descomprime `Medi_Core_parcial.zip`, abre la carpeta `Medi_Core_parcial` en VS Code y ejecuta:

```bash
python main.py
```

También funcionan `python src/main.py` y `python -m src.main`. Requiere Python 3.10 o superior con Tcl/Tk, sin paquetes pip. En Windows puedes usar `py main.py`. Para comprobar Tk: `python -m tkinter`.

## Flujo del encargado

1. Abre directamente el **Panel del encargado**, sin selector de responsabilidades ni portal de pacientes.
2. En **Pacientes**, registra nombre, DNI y datos de contacto. Cada paciente es un registro del centro, no una cuenta de acceso.
3. Selecciona un paciente de la tabla y pulsa **Programar cita**. En **Médicos** consulta tarifas y disponibilidad; el paciente elegido se mantiene.
4. Elige al médico, confirma el paciente en el formulario, selecciona fecha/turno y escribe el motivo. Guarda la cita.
5. En **Agenda**, consulta todas las citas, filtra por fecha/estado, revisa detalles o cancela una cita.
6. Al finalizar la consulta, selecciona una cita que ya haya comenzado y pulsa **Registrar atención**. El encargado transcribe el diagnóstico y las indicaciones proporcionados por el profesional.
7. La cita pasa a ATENDIDA y el registro aparece en **Historias clínicas**. También se accede desde la tabla de pacientes.
8. En **Resumen**, consulta indicadores o exporta la agenda a CSV. Los cambios se guardan automáticamente.

La primera ejecución incluye datos ficticios y una cita anterior de Alex Torres para probar inmediatamente el registro de atención. **Atendidas se cuenta por la atención registrada**, no por el paso de la hora.

## Funciones y presentación

- Registro de pacientes y médicos, búsqueda, tarifas y especialidades.
- Programación centralizada de citas, disponibilidad, cancelación, detalles y filtros.
- Historias clínicas por paciente y registro de atención vinculado al médico de la cita.
- Indicadores globales y exportación CSV.
- Iconos e ilustraciones locales en `src/ui/assets/`; tablas con scroll vertical y horizontal.
- DNI y CMP únicos, campos obligatorios, tarifas positivas y prevención de cruces de médico o paciente.
- Turnos de 30 minutos, lunes a sábado de 08:00 a 18:00, hasta 180 días por adelantado.
- Guardado JSON atómico y reversión en memoria si falla el almacenamiento.

## Alcance

Aplicación académica local de una sola instancia para el encargado. No incluye autoservicio, cuentas de pacientes, autenticación ni pagos en línea. B2C describe la relación del centro con sus pacientes, no un portal digital. Usar datos ficticios en la demostración. No es un sistema clínico listo para producción: ese uso requiere contresponsabilidades de acceso, privacidad y auditoría. El encargado registra la información emitida por el profesional; no reemplaza su criterio médico.

Las fechas usan la hora local del equipo: configurar Windows en la zona horaria de Perú. No abrir dos instancias sobre el mismo JSON. El valor de atenciones no acredita pagos recibidos.

## Datos y terminal

El archivo se crea al primer inicio en `data/medicore.json`, excluido de Git. No se incluye un archivo con datos personales en la entrega. Para probar otra base sin tocar la anterior:

```bash
python main.py --datos data/otra_demo.json
python main.py --datos data/base_vacia.json --sin-demo
python main.py --cli
```

`--sin-demo` se aplica solo a una base que todavía no exista. La CLI es un resumen de datos; la operación interactiva se realiza en la GUI.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Hay 14 pruebas automáticas: encapsulamiento, DNI/contacto, duplicados, tarifas, persistencia, cruces de médico/paciente, cancelación, horarios, atención/historia, diagnóstico obligatorio, reversión ante fallo de guardado, JSON corrupto y filtros. Se ejecutaron correctamente en el entorno de construcción. La interfaz no pudo verificarse visualmente en ese entorno por falta de servidor gráfico; revisar la GUI en Windows antes de la sustentación. No se adjuntan capturas de ejecución ficticias.

## Estructura

Las rutas exigidas se conservan: `.github/PULL_REQUEST_TEMPLATE.md`, `src/domain/__init__.py`, `exceptions.py`, `models.py`; `src/services/__init__.py`, `app_service.py`, `data_manager.py`; `src/ui/__init__.py`, `cli_interface.py`; `src/__init__.py`, `src/main.py`, `tests/test_domain.py`, `.gitignore`, `architecture.md`, `README.md`.

Adiciones: `main.py` (lanzador), `requirements.txt` (requisitos), `src/ui/widgets.py` (componentes), `src/ui/assets/` (imágenes/iconos), `.github/workflows/tests.yml` (pruebas en PR) y `docs/REPARTO_7.md` (plan de equipo).

## Uso en el repositorio

Este ZIP es la versión completa para ejecutar y revisar. Como ya subiste el esquema, integra después los aportes por ramas y PR según `docs/REPARTO_7.md`. No reemplaces toda main con este ZIP si necesitas conservar el proceso individual de cada integrante. No contiene `.git` ni un historial de commits inventado. Cada integrante debe comprender, validar y declarar el apoyo de IA en su PR.
