"""JSON local con escritura atómica. Nunca reemplaza un archivo corrupto al cargar."""
import json
import os
import tempfile
from pathlib import Path
from src.domain.exceptions import PersistenciaError


class DataManager:
    def __init__(self, ruta):
        self.ruta = Path(ruta)

    def cargar(self):
        if not self.ruta.exists():
            return None
        try:
            data = json.loads(self.ruta.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or data.get('version') != 1:
                raise ValueError('Versión de datos no compatible')
            for key in ('pacientes', 'medicos', 'citas', 'registros'):
                if not isinstance(data.get(key), list):
                    raise ValueError(f'Colección inválida: {key}')
            return data
        except (OSError, ValueError) as exc:
            raise PersistenciaError(f'No se pudo leer {self.ruta}. El archivo se conserva. Detalle: {exc}') from exc

    def guardar(self, datos):
        tmp = None
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.ruta.parent,
                                             prefix='.medicore-', suffix='.tmp', delete=False) as f:
                tmp = Path(f.name)
                json.dump(datos, f, indent=2, ensure_ascii=False, allow_nan=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.ruta)
        except (OSError, ValueError) as exc:
            raise PersistenciaError(f'No se pudieron guardar los cambios: {exc}') from exc
        finally:
            if tmp is not None and tmp.exists():
                tmp.unlink(missing_ok=True)
