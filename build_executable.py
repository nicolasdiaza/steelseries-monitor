# build_executable.py - Constructor de Ejecutable Final
import subprocess
import sys
import os
from pathlib import Path
import shutil

class ExecutableBuilder:
    """Construye ejecutable independiente"""
    
    def __init__(self):
        self.app_name = "ArcticMonitor"
        self.main_script = "main_minimal.py"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.spec_file = f"{self.app_name}.spec"
        
        print("🔨 ARCTIC MONITOR EXECUTABLE BUILDER")
        print("=" * 45)
    
    def check_pyinstaller(self) -> bool:
        """Verifica PyInstaller"""
        try:
            result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ PyInstaller {result.stdout.strip()} detectado")
                return True
        except Exception:
            pass
        
        print("❌ PyInstaller no encontrado")
        return False
    
    def install_pyinstaller(self) -> bool:
        """Instala PyInstaller"""
        print("📦 Instalando PyInstaller...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pyinstaller'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ PyInstaller instalado")
                return True
            else:
                print(f"❌ Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_spec_file(self) -> bool:
        """Crea archivo .spec"""
        print("📄 Creando archivo de especificaciones...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'wmi',
        'pythoncom',
        'win32com.client',
        'psutil',
        'requests',
        'keyboard'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        try:
            with open(self.spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            print(f"✅ {self.spec_file} creado")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def build_executable(self) -> bool:
        """Construye el ejecutable"""
        print("🔨 Construyendo ejecutable...")
        print("   (Esto puede tomar varios minutos)")
        
        try:
            # Clean previous builds
            for dir_path in [self.build_dir, self.dist_dir]:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
            
            # Build
            cmd = [sys.executable, '-m', 'PyInstaller', '--clean', self.spec_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                exe_path = self.dist_dir / f"{self.app_name}.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    print(f"✅ Ejecutable creado: {exe_path}")
                    print(f"📊 Tamaño: {size_mb:.1f} MB")
                    return True
                else:
                    print("❌ Ejecutable no encontrado")
                    return False
            else:
                print(f"❌ Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def cleanup_build_files(self):
        """Limpia archivos temporales"""
        print("🧹 Limpiando archivos temporales...")
        
        for item in [self.build_dir, self.spec_file]:
            try:
                item_path = Path(item)
                if item_path.exists():
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                    else:
                        item_path.unlink()
                    print(f"   ✅ {item} eliminado")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {item}: {e}")
    
    def build(self) -> bool:
        """Proceso completo"""
        print("🚀 INICIANDO CONSTRUCCIÓN")
        print("=" * 30)
        
        # Check PyInstaller
        if not self.check_pyinstaller():
            if not self.install_pyinstaller():
                return False
        
        # Verify main script
        if not Path(self.main_script).exists():
            print(f"❌ Script no encontrado: {self.main_script}")
            return False
        
        # Create spec and build
        if not self.create_spec_file():
            return False
        
        if not self.build_executable():
            return False
        
        # Cleanup
        choice = input("\n¿Limpiar archivos temporales? (Y/n): ")
        if choice.lower() != 'n':
            self.cleanup_build_files()
        
        print(f"\n🎉 CONSTRUCCIÓN COMPLETADA")
        print(f"📦 Ejecutable: dist/{self.app_name}.exe")
        return True

def main():
    print("Verificando archivos...")
    
    # Check main script
    main_scripts = ["main_minimal.py", "main.py"]
    found_script = None
    
    for script in main_scripts:
        if Path(script).exists():
            found_script = script
            break
    
    if not found_script:
        print("❌ No se encontró script principal")
        print("   Scripts buscados:", ", ".join(main_scripts))
        input("Presiona Enter para salir...")
        return
    
    print(f"✅ Usando: {found_script}")
    
    builder = ExecutableBuilder()
    builder.main_script = found_script
    
    try:
        if builder.build():
            print(f"\n✅ ¡Ejecutable creado exitosamente!")
        else:
            print(f"\n❌ Error en la construcción")
    except KeyboardInterrupt:
        print(f"\n🛑 Construcción cancelada")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()