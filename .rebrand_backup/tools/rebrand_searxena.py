#!/usr/bin/env python3
"""
searXena Rebranding Tool
=======================
Reemplaza referencias de searXena por searXena de forma inteligente,
manteniendo atribuciones de licencia donde corresponda.

Uso:
    python tools/rebrand_searxena.py --dry-run    # Ver cambios sin aplicar
    python tools/rebrand_searxena.py --apply      # Aplicar cambios
    python tools/rebrand_searxena.py --rollback   # Restaurar backup
"""

import os
import re
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set

# =============================================================================
# CONFIGURACION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent

# Directorios a excluir completamente
EXCLUDE_DIRS: Set[str] = {
    '.git', '__pycache__', 'node_modules', '.miku',
    'cache', 'build', 'dist', 'local', '.nvm', '.venv',
    '.idea', '.vscode', 'htmlcov', '.tox', ' *.egg-info'
}

# Extensiones de archivo a procesar (texto)
INCLUDE_EXTENSIONS: Set[str] = {
    '.py', '.js', '.ts', '.tsx', '.jsx',
    '.html', '.css', '.scss', '.less', '.sass',
    '.json', '.yaml', '.yml', '.toml',
    '.md', '.rst', '.txt', '.cfg', '.ini',
    '.sh', '.ps1', '.bat', '.cmd',
    '.xml', '.svg', '.pot', '.po',
    '.go', '.mod', '.sum',
    '.dockerfile', '.containerfile',
    '.gitignore', '.dockerignore',
    '.el', '.dot',
}

# Archivos específicos a incluir (sin extensión o nombres especiales)
INCLUDE_FILES: Set[str] = {
    'Makefile', 'makefile', 'Dockerfile', 'manage', 'LICENSE',
    'AUTHORS', 'CHANGELOG', 'README', 'CONTRIBUTING', 'SECURITY',
}

# Archivos donde NO reemplazar (mantener referencias originales)
KEEP_ORIGINAL: Set[str] = {
    'LICENSE', 'LICENSE.txt', 'LICENSE.md',
    'AUTHORS.rst', 'AUTHORS.txt', 'AUTHORS.md',
    'CHANGELOG.rst', 'CHANGELOG.md',
    '.gitattributes',
}

# Patrones de reemplazo (orden importa)
REPLACEMENTS: List[Tuple[str, str, str]] = [
    # (nombre_pattern, reemplazo, descripcion)
    # Variantes con mayusculas varias
    (r'SearXNG', 'searXena', 'SearXNG → searXena'),
    (r'searxng', 'searXena', 'searxng → searXena'),
    (r'SEARXNG', 'SEARXENA', 'SEARXNG → SEARXENA'),
    
    # Variantes con espacios/guiones
    (r'Searx', 'searXena', 'Searx → searXena'),
    (r'searx', 'searxena', 'searx → searxena'),
    
    # Nombres de paquete/modulo (evitar romper imports de searx. si no renombramos la carpeta searx)
    (r'searxng_extra', 'searxena_extra', 'modulo searxena_extra'),
    
    # URLs y dominios (cuidado aqui)
    # (r'searxng\.org', 'searxena.org', 'dominio'),  # Comentar si se quiere mantener
]

# Mensajes de atribucion a preservar/agregar
ATTRIBUTION_HEADER = """
"""

# =============================================================================
# CLASE PRINCIPAL
# =============================================================================

class RebrandTool:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.changes: List[Dict] = []
        self.backup_dir = PROJECT_ROOT / '.rebrand_backup'
        self.log_file = PROJECT_ROOT / '.rebrand_log.json'
        
    def should_process_file(self, filepath: Path) -> bool:
        """Determina si un archivo debe ser procesado."""
        name = filepath.name
        ext = filepath.suffix.lower()
        
        # Verificar si es archivo de atribucion a mantener
        if name in KEEP_ORIGINAL or name.startswith('COPYING'):
            return False
            
        # Archivos especificos a incluir
        if name in INCLUDE_FILES:
            return True
            
        # Extensiones validas
        return ext in INCLUDE_EXTENSIONS
    
    def should_process_dir(self, dirpath: Path) -> bool:
        """Determina si un directorio debe ser procesado."""
        return dirpath.name not in EXCLUDE_DIRS
    
    def get_all_files(self) -> List[Path]:
        """Obtiene lista de archivos a procesar."""
        files = []
        for root, dirs, filenames in os.walk(PROJECT_ROOT):
            root_path = Path(root)
            
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if self.should_process_dir(root_path / d)]
            
            for filename in filenames:
                filepath = root_path / filename
                if self.should_process_file(filepath):
                    files.append(filepath)
                    
        return files
    
    def apply_replacements(self, content: str) -> Tuple[str, List[str]]:
        """Aplica todos los reemplazos al contenido."""
        changes = []
        new_content = content
        
        for pattern, replacement, desc in REPLACEMENTS:
            matches = re.findall(pattern, content)
            if matches:
                new_content = re.sub(pattern, replacement, new_content)
                changes.append(f"{desc}: {len(matches)} ocurrencias")
                
        return new_content, changes
    
    def process_file(self, filepath: Path) -> Dict:
        """Procesa un archivo individual."""
        result = {
            'file': str(filepath.relative_to(PROJECT_ROOT)),
            'status': 'skipped',
            'changes': []
        }
        
        try:
            # Leer contenido
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                original = f.read()
            
            # Aplicar reemplazos
            new_content, changes = self.apply_replacements(original)
            
            if changes:
                result['status'] = 'modified'
                result['changes'] = changes
                
                if not self.dry_run:
                    # Crear backup
                    backup_path = self.backup_dir / filepath.relative_to(PROJECT_ROOT)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(filepath, backup_path)
                    
                    # Escribir cambios
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            else:
                result['status'] = 'no_changes'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
    
    def run(self) -> Dict:
        """Ejecuta el proceso de rebranding."""
        print(f"{'[DRY-RUN] ' if self.dry_run else ''}Escaneando archivos...")
        
        files = self.get_all_files()
        print(f"Archivos a procesar: {len(files)}")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'total_files': len(files),
            'modified': 0,
            'no_changes': 0,
            'errors': 0,
            'files': []
        }
        
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
        
        for filepath in files:
            result = self.process_file(filepath)
            results['files'].append(result)
            
            if result['status'] == 'modified':
                results['modified'] += 1
                print(f"  [MOD] {result['file']}")
                for change in result['changes']:
                    print(f"       - {change}")
            elif result['status'] == 'error':
                results['errors'] += 1
                print(f"  [ERR] {result['file']}: {result.get('error')}")
        
        results['no_changes'] = len(files) - results['modified'] - results['errors']
        
        # Guardar log
        if not self.dry_run:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nLog guardado en: {self.log_file}")
            print(f"Backup en: {self.backup_dir}")
        
        # Resumen
        print(f"\n{'='*60}")
        print(f"RESUMEN {'(DRY-RUN)' if self.dry_run else ''}")
        print(f"{'='*60}")
        print(f"Total archivos procesados: {results['total_files']}")
        print(f"Archivos modificados: {results['modified']}")
        print(f"Sin cambios: {results['no_changes']}")
        print(f"Errores: {results['errors']}")
        
        return results
    
    def rollback(self) -> bool:
        """Restaura archivos desde backup."""
        if not self.backup_dir.exists():
            print("No existe backup para restaurar.")
            return False
        
        print("Restaurando desde backup...")
        
        for backup_file in self.backup_dir.rglob('*'):
            if backup_file.is_file():
                original_path = PROJECT_ROOT / backup_file.relative_to(self.backup_dir)
                shutil.copy2(backup_file, original_path)
                print(f"  Restaurado: {original_path.relative_to(PROJECT_ROOT)}")
        
        print("Rollback completado.")
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='searXena Rebranding Tool - Reemplaza searXena por searXena'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Mostrar cambios sin aplicarlos'
    )
    parser.add_argument(
        '--apply', '-a',
        action='store_true',
        help='Aplicar cambios (crear backup automaticamente)'
    )
    parser.add_argument(
        '--rollback', '-r',
        action='store_true',
        help='Restaurar desde backup'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Mostrar reporte del ultimo log'
    )
    
    args = parser.parse_args()
    
    tool = RebrandTool(dry_run=args.dry_run or not args.apply)
    
    if args.rollback:
        tool.rollback()
    elif args.report:
        if tool.log_file.exists():
            with open(tool.log_file, 'r') as f:
                log = json.load(f)
            print(json.dumps(log, indent=2, ensure_ascii=False))
        else:
            print("No existe log previo.")
    else:
        tool.run()


if __name__ == '__main__':
    main()
