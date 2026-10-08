"""Entidades encapsuladas e independientes de la interfaz y el almacenamiento."""
from datetime import datetime
from math import isfinite
from .exceptions import ValidacionError


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValidacionError(f'{campo} es obligatorio.')
    return valor.strip()


class Entidad:
    def __init__(self, id):
        self.__id = texto(id, 'Identificador')

    @property
    def id(self):
        return self.__id


class Persona(Entidad):
    def __init__(self, id, nombre):
        super().__init__(id)
        self.__nombre = texto(nombre, 'Nombre')

    @property
    def nombre(self):
        return self.__nombre

    def descripcion(self):
        return self.nombre


class Paciente(Persona):
    def __init__(self, id, nombre, dni, telefono='', correo=''):
        super().__init__(id, nombre)
        dni = str(dni).strip()
        if len(dni) != 8 or not dni.isascii() or not dni.isdigit():
            raise ValidacionError('El DNI debe tener exactamente 8 dígitos.')
        telefono = str(telefono).strip()
        if telefono and (len(telefono) != 9 or not telefono.isascii() or not telefono.isdigit()):
            raise ValidacionError('El teléfono debe tener 9 dígitos o quedar vacío.')
        correo = str(correo).strip()
        if correo and ('@' not in correo or '.' not in correo.split('@')[-1]):
            raise ValidacionError('Ingresa un correo válido o deja el campo vacío.')
        self.__dni, self.__telefono, self.__correo = dni, telefono, correo

    @property
    def dni(self): return self.__dni
    @property
    def telefono(self): return self.__telefono
    @property
    def correo(self): return self.__correo

    def descripcion(self):
        return f'{self.nombre} · DNI {self.dni}'

    def to_dict(self):
        return dict(id=self.id, nombre=self.nombre, dni=self.dni, telefono=self.telefono, correo=self.correo)


class Medico(Persona):
    def __init__(self, id, nombre, especialidad, cmp, tarifa, descripcion='Atención presencial en Cusco.'):
        super().__init__(id, nombre)
        self.__especialidad = texto(especialidad, 'Especialidad')
        self.__cmp = texto(str(cmp), 'CMP')
        try:
            tarifa = float(tarifa)
        except (ValueError, TypeError):
            raise ValidacionError('La tarifa debe ser un número.') from None
        if not isfinite(tarifa) or tarifa <= 0:
            raise ValidacionError('La tarifa debe ser mayor que cero.')
        self.__tarifa = round(tarifa, 2)
        self.__descripcion = str(descripcion).strip()

    @property
    def especialidad(self): return self.__especialidad
    @property
    def cmp(self): return self.__cmp
    @property
    def tarifa(self): return self.__tarifa
    @property
    def detalle(self): return self.__descripcion

    def descripcion(self):
        return f'{self.nombre} · {self.especialidad}'

    def to_dict(self):
        return dict(id=self.id, nombre=self.nombre, especialidad=self.especialidad, cmp=self.cmp,
                    tarifa=self.tarifa, descripcion=self.detalle)


class Cita(Entidad):
    ESTADOS = ('PROGRAMADA', 'ATENDIDA', 'CANCELADA')

    def __init__(self, id, paciente_id, medico_id, inicio, motivo, tarifa, estado='PROGRAMADA'):
        super().__init__(id)
        self.__paciente_id = texto(paciente_id, 'Paciente')
        self.__medico_id = texto(medico_id, 'Médico')
        try:
            inicio = datetime.fromisoformat(inicio) if isinstance(inicio, str) else inicio
            if not isinstance(inicio, datetime) or inicio.tzinfo is not None:
                raise ValueError
        except (ValueError, TypeError):
            raise ValidacionError('Fecha y hora inválidas.') from None
        if estado not in self.ESTADOS:
            raise ValidacionError('Estado de cita inválido.')
        self.__inicio = inicio
        self.__motivo = texto(motivo, 'Motivo de consulta')
        try:
            tarifa = float(tarifa)
        except (ValueError, TypeError):
            raise ValidacionError('Tarifa inválida.') from None
        if not isfinite(tarifa) or tarifa <= 0:
            raise ValidacionError('Tarifa inválida.')
        self.__tarifa, self.__estado = tarifa, estado

    @property
    def paciente_id(self): return self.__paciente_id
    @property
    def medico_id(self): return self.__medico_id
    @property
    def inicio(self): return self.__inicio
    @property
    def motivo(self): return self.__motivo
    @property
    def tarifa(self): return self.__tarifa
    @property
    def estado(self): return self.__estado

    def atender(self):
        self._exigir_programada()
        self.__estado = 'ATENDIDA'

    def cancelar(self):
        self._exigir_programada()
        self.__estado = 'CANCELADA'

    def _exigir_programada(self):
        if self.estado != 'PROGRAMADA':
            raise ValidacionError('Solo se puede modificar una cita programada.')

    def to_dict(self):
        return dict(id=self.id, paciente_id=self.paciente_id, medico_id=self.medico_id,
                    inicio=self.inicio.isoformat(), motivo=self.motivo, tarifa=self.tarifa, estado=self.estado)


class RegistroClinico(Entidad):
    def __init__(self, id, cita_id, diagnostico, indicaciones, fecha):
        super().__init__(id)
        self.__cita_id = texto(cita_id, 'Cita')
        self.__diagnostico = texto(diagnostico, 'Diagnóstico')
        self.__indicaciones = texto(indicaciones, 'Indicaciones')
        try:
            datetime.fromisoformat(fecha)
        except (ValueError, TypeError):
            raise ValidacionError('Fecha del registro inválida.') from None
        self.__fecha = fecha

    @property
    def cita_id(self): return self.__cita_id
    @property
    def diagnostico(self): return self.__diagnostico
    @property
    def indicaciones(self): return self.__indicaciones
    @property
    def fecha(self): return self.__fecha

    def to_dict(self):
        return dict(id=self.id, cita_id=self.cita_id, diagnostico=self.diagnostico,
                    indicaciones=self.indicaciones, fecha=self.fecha)
