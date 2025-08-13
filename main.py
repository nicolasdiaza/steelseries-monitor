# main_minimal.py - Versión Final Limpia y Completa
import time
import json
import requests
import sys
import os
import threading
from pathlib import Path

# Import hardware monitor
sys.path.insert(0, str(Path(__file__).parent))
from src.monitors.hardware_monitor import HardwareMonitor

def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados con PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_gg_url():
    """Obtiene URL de SteelSeries GG"""
    try:
        with open("C:/ProgramData/SteelSeries/GG/coreProps.json", 'r') as f:
            return f"http://{json.load(f)['address']}"
    except:
        return None

def setup_gg(url):
    """Configura SteelSeries GG"""
    try:
        # Register game
        requests.post(f"{url}/game_metadata", json={
            "game": "ARCTIS_MIN", "game_display_name": "Arctic Min"
        }, timeout=3).raise_for_status()
        
        # Setup display event
        requests.post(f"{url}/bind_game_event", json={
            "game": "ARCTIS_MIN", "event": "DISPLAY",
            "handlers": [{
                "device-type": "screened", "zone": "one", "mode": "screen",
                "datas": [{
                    "lines": [
                        {"has-text": True, "context-frame-key": f"line{i}"} 
                        for i in range(1, 4)
                    ]
                }]
            }],
            "value_optional": True
        }, timeout=3).raise_for_status()
        
        return True
    except:
        return False

def send_to_oled(url, cpu_usage, cpu_temp, gpu_usage, gpu_temp, ram_used_gb, ram_total_gb, ram_percent, display_active=True):
    """Envía datos a OLED con duración corta para no bloquear otras apps"""
    if not display_active:
        return True
    
    try:
        frame_data = {
            "line1": f"CPU ⇾ {cpu_usage:>2}%🌡{cpu_temp:>2}°C",
            "line2": f"GPU ⇾ {gpu_usage:>2}%🌡{gpu_temp:>2}°C",
            "line3": f"RAM ⇾ {ram_used_gb:.1f}/{ram_total_gb:.0f}GB"
        }
        
        requests.post(f"{url}/game_event", json={
            "game": "ARCTIS_MIN", 
            "event": "DISPLAY",
            "data": {
                "frame": frame_data,
                "length-millis": 800  # Solo mostrar por 800ms, dar espacio a otras apps
            }
        }, timeout=0.5)
        return True
    except:
        return False

def send_disk_info_to_oled(url):
    """Envía información de discos a OLED"""
    try:
        import psutil
        
        # Obtener info del disco principal (C:)
        disk_c = psutil.disk_usage('C:')
        used_gb = disk_c.used / (1024**3)
        total_gb = disk_c.total / (1024**3)
        free_gb = disk_c.free / (1024**3)
        usage_percent = (disk_c.used / disk_c.total) * 100
        
        frame_data = {
            "line1": f"DISK C: {usage_percent:.0f}%",
            "line2": f"Used: {used_gb:.0f}GB",
            "line3": f"Free: {free_gb:.0f}GB"
        }
        
        requests.post(f"{url}/game_event", json={
            "game": "ARCTIS_MIN", 
            "event": "DISPLAY",
            "data": {
                "frame": frame_data,
                "length-millis": 800  # Misma duración que hardware para compartir
            }
        }, timeout=0.5)
        return True
    except:
        return False

def deactivate_display(url):
    """Desactiva display - vuelve a pantalla principal"""
    try:
        requests.post(f"{url}/remove_game_event", json={
            "game": "ARCTIS_MIN", "event": "DISPLAY"
        }, timeout=2)
        return True
    except:
        return False

def reactivate_display(url):
    """Reactiva display"""
    try:
        requests.post(f"{url}/bind_game_event", json={
            "game": "ARCTIS_MIN", "event": "DISPLAY",
            "handlers": [{
                "device-type": "screened", "zone": "one", "mode": "screen",
                "datas": [{
                    "lines": [
                        {"has-text": True, "context-frame-key": f"line{i}"} 
                        for i in range(1, 4)
                    ]
                }]
            }],
            "value_optional": True
        }, timeout=3).raise_for_status()
        return True
    except:
        return False

def show_activation_message(url):
    """Muestra mensaje de activación"""
    try:
        requests.post(f"{url}/game_event", json={
            "game": "ARCTIS_MIN", "event": "DISPLAY",
            "data": {"frame": {
                "line1": "",
                "line2": "  ✅ MONITOR ON",
                "line3": ""
            }}
        }, timeout=0.5)
        time.sleep(1.5)
        return True
    except:
        return False

def cleanup_gg(url):
    """Limpia SteelSeries GG"""
    try:
        requests.post(f"{url}/remove_game", json={"game": "ARCTIS_MIN"}, timeout=3)
    except:
        pass

class KeybindListener:
    """Maneja Ctrl+F9 (inmediato) y F10 (3s hold) keybinds"""
    
    def __init__(self):
        self.toggle_callback = None
        self.disk_callback = None
        self.keyboard_available = False
        
        # Estado para F10
        self.f10_pressed = False
        self.f10_timer = None
        self.hold_duration = 3.0  # 3 segundos
        
        self._setup_keyboard()
    
    def _setup_keyboard(self):
        try:
            import keyboard
            import threading
            self.keyboard_available = True
            
            # Ctrl+F9 inmediato para toggle
            keyboard.add_hotkey('ctrl+f9', self._execute_toggle)
            
            # F10 con hold para modo
            keyboard.on_press_key('f10', self._on_f10_press)
            keyboard.on_release_key('f10', self._on_f10_release)
            
            print("⌨️  Ctrl+F9 = Toggle Monitor | F10 (hold 3s) = Change Mode")
        except ImportError:
            print("⚠️  'keyboard' no disponible - instala con: pip install keyboard")
        except Exception as e:
            print(f"⚠️  Error configurando keybinds: {e}")
    
    def _execute_toggle(self):
        """Ejecuta toggle inmediatamente"""
        print(f"\n⚡ Ctrl+F9 - Toggle ejecutado")
        if self.toggle_callback:
            self.toggle_callback()
    
    def _on_f10_press(self, event):
        if not self.f10_pressed:
            self.f10_pressed = True
            print(f"\n⏳ F10 presionado - ejecutará cambio de modo en 3s...")
            
            # Programar ejecución automática en 3 segundos
            import threading
            self.f10_timer = threading.Timer(self.hold_duration, self._execute_f10)
            self.f10_timer.start()
    
    def _on_f10_release(self, event):
        if self.f10_pressed:
            self.f10_pressed = False
            
            # Cancelar timer si se suelta antes de 3 segundos
            if self.f10_timer and self.f10_timer.is_alive():
                self.f10_timer.cancel()
                print(f"❌ F10 soltado antes de 3s - cancelado")
    
    def _execute_f10(self):
        """Ejecuta cambio de modo después de 3 segundos"""
        if self.f10_pressed:  # Solo si sigue presionado
            print(f"✅ F10 ejecutado después de 3s")
            if self.disk_callback:
                self.disk_callback()
        self.f10_pressed = False
    
    def set_toggle_callback(self, callback):
        self.toggle_callback = callback
    
    def set_disk_callback(self, callback):
        self.disk_callback = callback
    
    def cleanup(self):
        # Cancelar timers activos
        if self.f10_timer and self.f10_timer.is_alive():
            self.f10_timer.cancel()
            
        if self.keyboard_available:
            try:
                import keyboard
                keyboard.unhook_all()
            except:
                pass

def main():
    print("🎮 ARCTIC MONITOR - MINIMAL")
    print("=" * 30)
    
    # Setup SteelSeries GG
    gg_url = get_gg_url()
    if not gg_url or not setup_gg(gg_url):
        print("❌ SteelSeries GG setup failed")
        return
    
    # Setup Hardware Monitor
    hw_monitor = HardwareMonitor()
    if not hw_monitor.start():
        print("❌ Hardware monitor failed")
        return
    
    # Setup Keybinds
    keybind_listener = KeybindListener()
    display_active = True
    display_mode = "hardware"  # "hardware" o "disk"
    
    def toggle_display():
        nonlocal display_active
        display_active = not display_active
        
        if display_active:
            if reactivate_display(gg_url):
                threading.Thread(target=lambda: show_activation_message(gg_url), daemon=True).start()
        else:
            deactivate_display(gg_url)
        
        print(f"\n📺 Display: {'ON' if display_active else 'OFF'}")
    
    def toggle_disk_mode():
        nonlocal display_mode
        if display_mode == "hardware":
            display_mode = "disk"
            print(f"\n💽 Cambiado a modo DISCO (actualización cada 5s)")
        else:
            display_mode = "hardware"
            print(f"\n🔧 Cambiado a modo HARDWARE (actualización cada 2s)")
    
    keybind_listener.set_toggle_callback(toggle_display)
    keybind_listener.set_disk_callback(toggle_disk_mode)
    
    controls_msg = "| Ctrl+F9 = Toggle | F10 (3s) = Mode |" if keybind_listener.keyboard_available else "|"
    print(f"✅ Ready {controls_msg} Press Ctrl+C to stop")
    print("🔧 Hardware: cada 2s | 💽 Disk: cada 5s")
    print("⚡ Ctrl+F9 = Inmediato | ⏳ F10 = Hold 3s")
    
    try:
        count = 0
        last_hardware_update = 0
        last_disk_update = 0
        hardware_interval = 2.0  # Hardware cada 2 segundos
        disk_interval = 5.0     # Disk cada 5 segundos
        
        while True:
            current_time = time.time()
            
            if display_active:
                if display_mode == "hardware":
                    # Modo hardware: actualizar cada 2 segundos
                    if current_time - last_hardware_update >= hardware_interval:
                        # Get hardware data from LibreHardwareMonitor
                        hw = hw_monitor.get_quick_stats()
                        cpu_usage = int(hw.get('cpu_usage', 0) or 0)
                        cpu_temp = int(hw.get('cpu_temp', 0) or 0) if hw.get('cpu_temp') else 0
                        gpu_usage = int(hw.get('gpu_usage', 0) or 0)
                        gpu_temp = int(hw.get('gpu_temp', 0) or 0) if hw.get('gpu_temp') else 0
                        
                        # RAM desde LibreHardwareMonitor
                        ram_used_gb = hw.get('ram_used_gb', 0) or 0
                        ram_total_gb = hw.get('ram_total_gb', 0) or 16
                        ram_percent = hw.get('ram_usage', 0) or 0
                        
                        # Send hardware data to OLED
                        send_to_oled(gg_url, cpu_usage, cpu_temp, gpu_usage, gpu_temp, ram_used_gb, ram_total_gb, ram_percent, display_active)
                        
                        last_hardware_update = current_time
                        count += 1
                        
                        # Console status
                        status_icon = "🟢"
                        print(f"\r{status_icon} [HW-{count}] CPU:{cpu_usage}% GPU:{gpu_usage}% RAM:{ram_used_gb:.1f}/{ram_total_gb:.0f}GB", end='')
                
                elif display_mode == "disk":
                    if current_time - last_disk_update >= disk_interval:
                        # Send disk data to OLED
                        send_disk_info_to_oled(gg_url)
                        
                        last_disk_update = current_time
                        count += 1
                        
                        # Console status
                        status_icon = "💽"
                        next_update = int(disk_interval - (current_time - last_disk_update))
                        print(f"\r{status_icon} [DISK-{count}] Próxima actualización en {max(0, next_update)}s", end='')
            else:
                # Console status cuando display está OFF
                status_icon = "🔴"
                print(f"\r{status_icon} [OFF] Monitor desactivado - Ctrl+F9 para activar", end='')
            
            time.sleep(1.0)  # Sleep de 1 segundo para Ctrl+F9/F10 responsivo
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        keybind_listener.cleanup()
        hw_monitor.stop()
        cleanup_gg(gg_url)
        print("👋 Done")

if __name__ == "__main__":
    main()