# MediCore — Gestión de un Centro Médico

MediCore es una aplicación de escritorio desarrollada en Python para gestionar pacientes, médicos, citas e historias clínicas.

El sistema lo utiliza un encargado del centro médico, quien registra los datos y administra las atenciones. El proyecto representa un negocio B2C: el centro médico presta servicios directamente a sus pacientes.

## Funcionalidades

- Registrar pacientes y médicos.
- Programar citas y validar disponibilidad.
- Evitar cruces de horarios entre pacientes y médicos.
- Consultar la agenda y cancelar citas.
- Registrar una atención con diagnóstico e indicaciones.
- Consultar historias clínicas por paciente.
- Mostrar indicadores de citas y atenciones.
- Guardar la información localmente en archivos JSON.
- Exportar información de la agenda a CSV.

Una cita se contabiliza como atendida cuando el encargado registra la atención. Programarla no aumenta el contador de atenciones.

## Tecnologías

- Python 3.10 o superior.
- Tkinter y ttk para la interfaz gráfica.
- JSON para almacenamiento local.
- unittest para pruebas.
- Git y GitHub para control de versiones y colaboración.

## Estructura del proyecto

```text
Medi_Core_Parcial/
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   └── REPARTO_7.md
├── src/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── app_service.py
│   │   └── data_manager.py
│   ├── ui/
│   │   ├── assets/
│   │   ├── __init__.py
│   │   ├── cli_interface.py
│   │   └── widgets.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_domain.py
├── .gitignore
├── architecture.md
├── main.py
├── README.md
└── requirements.txt
```

Los iconos e imágenes se encuentran en `src/ui/assets/`.

## Arquitectura

El proyecto se organiza en tres capas:

| Capa | Responsabilidad |
|---|---|
| Dominio | Define las entidades, sus atributos, validaciones y excepciones. |
| Servicios y datos | Gestiona las operaciones, las reglas de las citas y la persistencia. |
| Interfaz | Presenta los formularios, tablas y acciones disponibles para el encargado. |

La interfaz utiliza los servicios, y los servicios trabajan con las entidades del dominio. El diseño aplica encapsulamiento, herencia y polimorfismo.

El diagrama y las decisiones de arquitectura se documentan en `architecture.md`.

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/drakosa1/Medi_Core_Parcial.git
cd Medi_Core_Parcial
```

### 2. Verificar Python

```bash
python --version
```

Se requiere Python 3.10 o superior con Tkinter disponible.

### 3. Ejecutar la aplicación

Desde la raíz del proyecto:

```bash
python main.py
```

También se puede ejecutar con:

```bash
python -m src.main
```

La aplicación utiliza la biblioteca estándar de Python y no requiere paquetes externos de pip.

## Uso del sistema

1. Registrar al paciente y al médico.
2. Seleccionar al paciente, al médico y un horario disponible.
3. Programar la cita.
4. Consultar la cita en la agenda.
5. Al realizarse la atención, registrar el diagnóstico y las indicaciones.
6. Consultar la historia clínica y los indicadores actualizados.

La información se conserva localmente entre ejecuciones. Los datos de demostración son ficticios.

## Pruebas

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

Las pruebas verifican validaciones del dominio y operaciones del sistema, como programación, conflictos de horarios, atención y persistencia.

## Organización del equipo

El equipo está formado por siete integrantes:

| Área | Integrantes | Rama |
|---|---:|---|
| Dominio | 2 | `feature/dominio` |
| Servicios y datos | 2 | `feature/servicios` |
| Interfaz | 2 | `feature/ui` |
| Integración y documentación | 1 | `fix/integracion` |

El GitMaster revisa los cambios, coordina la integración y resuelve los conflictos junto con los responsables de cada parte.

Cada integrante debe realizar sus propios commits y Pull Requests para dejar evidencia de su participación.

## Flujo de colaboración

1. Actualizar el repositorio antes de trabajar.
2. Cambiar a la rama correspondiente.
3. Modificar y probar los archivos asignados.
4. Crear un commit con un mensaje descriptivo.
5. Subir los cambios a GitHub.
6. Abrir un Pull Request hacia `main`.
7. Revisar e integrar los cambios.

Cuando dos integrantes comparten una rama, deben coordinar sus subidas y actualizarla antes de continuar.

## Uso de inteligencia artificial

Este proyecto utiliza asistencia de inteligencia artificial para apoyar el desarrollo y la documentación.

Cada integrante debe declarar en su Pull Request los prompts utilizados, los cambios realizados y las pruebas que ejecutó realmente. También debe revisar y comprender el código que presenta.

## Alcance

MediCore es un prototipo académico de gestión interna. No incluye un portal de pacientes ni pagos en línea.

Para utilizarlo con datos reales, se requiere incorporar autenticación, permisos, protección de información y procedimientos de respaldo.
