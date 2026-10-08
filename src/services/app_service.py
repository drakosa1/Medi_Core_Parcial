"""Casos de uso de recepción, gestión de atención y CLI."""
from datetime import datetime, timedelta, date, time
from copy import deepcopy
from uuid import uuid4
from src.domain.models import Paciente, Medico, Cita, RegistroClinico
from src.domain.exceptions import ValidacionError, NoEncontradoError, ConflictoAgendaError, PersistenciaError


class AppService:
    def __init__(self, data_manager, demo=True, reloj=None):
        self.data_manager = data_manager
        self.ahora = reloj or datetime.now
        datos = data_manager.cargar()
        if datos is None:
            self.pacientes, self.medicos, self.citas, self.registros = {}, {}, {}, {}
            if demo:
                self._sembrar_demo()
            self.data_manager.guardar(self._datos())
        else:
            self._restaurar(datos)

    @staticmethod
    def _id(): return uuid4().hex[:12]

    def _datos(self):
        return dict(version=1, **{k: [o.to_dict() for o in getattr(self, k).values()]
                                 for k in ('pacientes', 'medicos', 'citas', 'registros')})

    def _restaurar(self, datos):
        try:
            for key, cls in [('pacientes', Paciente), ('medicos', Medico), ('citas', Cita), ('registros', RegistroClinico)]:
                objects = [cls(**d) for d in datos[key]]
                if len({o.id for o in objects}) != len(objects):
                    raise ValueError('IDs duplicados')
                setattr(self, key, {o.id: o for o in objects})
            if len({p.dni for p in self.pacientes.values()}) != len(self.pacientes):
                raise ValueError('DNI duplicado')
            if len({m.cmp for m in self.medicos.values()}) != len(self.medicos):
                raise ValueError('CMP duplicado')
            for c in self.citas.values():
                if c.paciente_id not in self.pacientes or c.medico_id not in self.medicos:
                    raise ValueError('Cita con referencias inexistentes')
            seen = set()
            for r in self.registros.values():
                if r.cita_id not in self.citas or self.citas[r.cita_id].estado != 'ATENDIDA' or r.cita_id in seen:
                    raise ValueError('Historia clínica inconsistente')
                seen.add(r.cita_id)
            if any(c.estado == 'ATENDIDA' and c.id not in seen for c in self.citas.values()):
                raise ValueError('Atención sin historia clínica')
        except (KeyError, TypeError, ValueError, ValidacionError) as exc:
            raise PersistenciaError(f'Los datos guardados son inconsistentes. No se modificaron: {exc}') from exc

    def _transaccion(self, operacion):
        backup = deepcopy((self.pacientes, self.medicos, self.citas, self.registros))
        try:
            resultado = operacion()
            self.data_manager.guardar(self._datos())
            return resultado
        except Exception:
            self.pacientes, self.medicos, self.citas, self.registros = backup
            raise

    def _obtener(self, coleccion, id, nombre):
        if id not in coleccion:
            raise NoEncontradoError(f'{nombre} no encontrado.')
        return coleccion[id]

    def paciente(self, id): return self._obtener(self.pacientes, id, 'Paciente')
    def medico(self, id): return self._obtener(self.medicos, id, 'Médico')
    def cita(self, id): return self._obtener(self.citas, id, 'Cita')

    def listar_pacientes(self): return sorted(self.pacientes.values(), key=lambda p: p.nombre)
    def listar_medicos(self): return sorted(self.medicos.values(), key=lambda m: m.nombre)
    def especialidades(self): return sorted({m.especialidad for m in self.medicos.values()})

    def registrar_paciente(self, nombre, dni, telefono='', correo=''):
        p = Paciente(self._id(), nombre, dni, telefono, correo)
        if any(x.dni == p.dni for x in self.pacientes.values()):
            raise ValidacionError('Ya existe un paciente con ese DNI.')
        return self._transaccion(lambda: self._insertar(self.pacientes, p))

    def registrar_medico(self, nombre, especialidad, cmp, tarifa, descripcion='Atención presencial en Cusco.'):
        m = Medico(self._id(), nombre, especialidad, cmp, tarifa, descripcion)
        if any(x.cmp == m.cmp for x in self.medicos.values()):
            raise ValidacionError('Ya existe un médico con ese CMP.')
        return self._transaccion(lambda: self._insertar(self.medicos, m))

    @staticmethod
    def _insertar(coleccion, entidad):
        coleccion[entidad.id] = entidad
        return entidad

    def _validar_horario(self, inicio):
        if not isinstance(inicio, datetime) or inicio.tzinfo is not None:
            raise ValidacionError('Fecha inválida.')
        if inicio <= self.ahora():
            raise ValidacionError('Elige una fecha y hora futuras.')
        if inicio.date() > self.ahora().date() + timedelta(days=180):
            raise ValidacionError('Puedes reservar hasta 180 días por adelantado.')
        if inicio.weekday() == 6:
            raise ValidacionError('La clínica no atiende los domingos.')
        if inicio.hour < 8 or inicio.hour >= 18 or inicio.minute not in (0, 30) or inicio.second or inicio.microsecond:
            raise ValidacionError('Horario: lunes a sábado de 08:00 a 18:00, en turnos de 30 minutos.')

    def _hay_cruce(self, medico_id, paciente_id, inicio):
        fin = inicio + timedelta(minutes=30)
        return any(c.estado != 'CANCELADA' and (c.medico_id == medico_id or c.paciente_id == paciente_id)
                   and inicio < c.inicio + timedelta(minutes=30) and fin > c.inicio for c in self.citas.values())

    def horarios_disponibles(self, medico_id, fecha, paciente_id=None):
        self.medico(medico_id)
        if paciente_id: self.paciente(paciente_id)
        try:
            fecha = date.fromisoformat(fecha) if isinstance(fecha, str) else fecha
            base = datetime.combine(fecha, time(8))
        except (ValueError, TypeError):
            raise ValidacionError('Usa una fecha válida con formato AAAA-MM-DD.') from None
        if fecha.weekday() == 6 or fecha < self.ahora().date() or fecha > self.ahora().date() + timedelta(days=180):
            return []
        return [base + timedelta(minutes=30*i) for i in range(20)
                if base + timedelta(minutes=30*i) > self.ahora()
                and not self._hay_cruce(medico_id, paciente_id, base + timedelta(minutes=30*i))]

    def programar_cita(self, paciente_id, medico_id, inicio, motivo):
        self.paciente(paciente_id)
        medico = self.medico(medico_id)
        self._validar_horario(inicio)
        if self._hay_cruce(medico_id, paciente_id, inicio):
            raise ConflictoAgendaError('El médico o paciente ya tiene una cita en ese horario. Elige otro turno.')
        c = Cita(self._id(), paciente_id, medico_id, inicio, motivo, medico.tarifa)
        return self._transaccion(lambda: self._insertar(self.citas, c))

    def cancelar_cita(self, cita_id):
        return self._transaccion(lambda: self.cita(cita_id).cancelar())

    def registrar_atencion(self, cita_id, diagnostico, indicaciones):
        c = self.cita(cita_id)
        if c.inicio > self.ahora():
            raise ValidacionError('La cita aún no ha comenzado. Solo puedes atender desde su hora programada.')
        r = RegistroClinico(self._id(), cita_id, diagnostico, indicaciones, self.ahora().isoformat())
        def operacion():
            self.cita(cita_id).atender()
            return self._insertar(self.registros, r)
        return self._transaccion(operacion)

    def listar_citas(self, paciente_id=None, estado=None, fecha=None):
        return sorted((c for c in self.citas.values()
                       if (not paciente_id or c.paciente_id == paciente_id)
                       and (not estado or c.estado == estado)
                       and (not fecha or c.inicio.date().isoformat() == fecha)), key=lambda c: c.inicio, reverse=True)

    def obtener_historia(self, paciente_id):
        self.paciente(paciente_id)
        return sorted((r for r in self.registros.values() if self.cita(r.cita_id).paciente_id == paciente_id),
                      key=lambda r: r.fecha, reverse=True)

    def indicadores(self, paciente_id=None):
        citas = self.listar_citas(paciente_id)
        return {e: sum(c.estado == e for c in citas) for e in Cita.ESTADOS}

    def _sembrar_demo(self):
        p = Paciente('pac-demo', 'Alex Torres (demo)', '00000001', '900000001', 'alex@example.com')
        self.pacientes[p.id] = p
        for args in [
            ('med-1','Valeria Ríos','Medicina general','DEMO-001',65,'Consulta integral, prevención y seguimiento de tu salud.'),
            ('med-2','Mateo Salas','Odontología','DEMO-002',85,'Evaluación dental y orientación para cuidar tu sonrisa.'),
            ('med-3','Lucía Vega','Dermatología','DEMO-003',110,'Evaluación y seguimiento del cuidado de tu piel.'),
            ('med-4','Gabriel Paredes','Pediatría','DEMO-004',95,'Atención y seguimiento para niños y adolescentes.')]:
            m = Medico(*args); self.medicos[m.id] = m
        ayer = (self.ahora()-timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        c = Cita('cita-demo', p.id, 'med-1', ayer, 'Consulta de seguimiento de demostración', 65)
        self.citas[c.id] = c
