"""Composición de dependencias y punto de entrada obligatorio."""
import argparse
import sys
from pathlib import Path

# Permite tanto python src/main.py como python -m src.main.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.data_manager import DataManager
from src.services.app_service import AppService
from src.domain.exceptions import MediCoreError


def main():
    parser = argparse.ArgumentParser(description='MediCore: gestión de citas e historias clínicas')
    parser.add_argument('--cli', action='store_true', help='Mostrar resumen en terminal')
    parser.add_argument('--sin-demo', action='store_true', help='Crear datos vacíos si el archivo aún no existe')
    parser.add_argument('--datos', type=Path, default=ROOT/'data'/'medicore.json', help='Archivo JSON local')
    args = parser.parse_args()
    try:
        servicio = AppService(DataManager(args.datos), demo=not args.sin_demo)
        if args.cli:
            # La CLI funciona incluso si la instalación de Python no dispone de Tk.
            print('MediCore · Resumen local')
            print(f'Pacientes: {len(servicio.pacientes)} | Médicos: {len(servicio.medicos)}')
            for estado, total in servicio.indicadores().items(): print(f'{estado}: {total}')
        else:
            from src.ui.cli_interface import iniciar
            iniciar(servicio)
    except MediCoreError as exc:
        print(f'MediCore: {exc}', file=sys.stderr)
        return 1
    except ImportError as exc:
        print(f'Falta un componente de Python: {exc}. Instala Python con soporte Tcl/Tk.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
