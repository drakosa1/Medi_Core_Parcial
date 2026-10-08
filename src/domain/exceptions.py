"""Errores de negocio que la interfaz puede presentar al usuario."""
class MediCoreError(Exception):
    """Error controlado de la aplicación."""

class ValidacionError(MediCoreError):
    pass

class NoEncontradoError(MediCoreError):
    pass

class ConflictoAgendaError(MediCoreError):
    pass

class PersistenciaError(MediCoreError):
    pass
