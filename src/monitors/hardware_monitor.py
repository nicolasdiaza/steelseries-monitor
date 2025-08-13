# src/monitors/hardware_monitor.py - Versión Final Simplificada
import platform
import statistics
import threading
import time
from collections import deque
from typing import Dict, Any

try:
    import pythoncom
    import wmi
    WMI_AVAILABLE = platform.system() == 'Windows'
except ImportError:
    WMI_AVAILABLE = False

class HardwareMonitor:
    """Monitor de hardware simplificado"""

    def __init__(self):
        if not WMI_AVAILABLE:
            raise ImportError("HardwareMonitor requiere WMI y Windows.")
        
        self.running = False
        self.thread = None
        self.current_data = {
            'cpu_usage': 0, 'cpu_temp': None,
            'gpu_usage': 0, 'gpu_temp': None,
            'ram_usage': 0
        }
        self.data_lock = threading.Lock()
        
        # Samples para promedios
        self.cpu_usage_samples = deque(maxlen=5)
        self.gpu_usage_samples = deque(maxlen=5)

    def start(self) -> bool:
        """Inicia el monitor"""
        if self.running:
            return True
        
        try:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            return True
        except Exception:
            return False

    def stop(self):
        """Detiene el monitor"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3.0)

    def _monitor_loop(self):
        """Bucle principal de monitoreo"""
        while self.running:
            try:
                data = self._collect_data()
                with self.data_lock:
                    self.current_data = data
            except Exception:
                pass  # Continuar en caso de error
            
            time.sleep(1.0)

    def _collect_data(self) -> Dict[str, Any]:
        """Recolecta datos de hardware"""
        try:
            pythoncom.CoInitialize()
            lhm_client = wmi.WMI(namespace="root\\LibreHardwareMonitor")

            # Identificar hardware
            cpu_identifier, gpu_identifier = None, None
            nvidia_gpu_id, amd_gpu_id = None, None

            for hw in lhm_client.Hardware():
                hw_type_lower = hw.HardwareType.lower()
                if 'cpu' in hw_type_lower:
                    cpu_identifier = hw.Identifier
                elif 'gpunvidia' in hw_type_lower:
                    nvidia_gpu_id = hw.Identifier
                elif 'gpuamd' in hw_type_lower:
                    amd_gpu_id = hw.Identifier
            
            # Prioridad NVIDIA > AMD
            gpu_identifier = nvidia_gpu_id or amd_gpu_id
            
            # Obtener sensores
            temp_sensors = lhm_client.query("SELECT * FROM Sensor WHERE SensorType='Temperature'")
            load_sensors = lhm_client.query("SELECT * FROM Sensor WHERE SensorType='Load'")
            data_sensors = lhm_client.query("SELECT * FROM Sensor WHERE SensorType='Data'")  # Para memoria
            all_sensors = temp_sensors + load_sensors + data_sensors

        except Exception:
            raise ConnectionError("Error accediendo a sensores WMI")
        finally:
            pythoncom.CoUninitialize()

        # Procesar datos
        cpu_load, cpu_temp, gpu_load, gpu_temp = None, None, None, None
        memory_used_gb, memory_total_gb = None, None
        
        cpu_temp_sensors = {"CCD1 (Tdie)": None, "Core (Tctl/Tdie)": None, "CPU Package": None}
        cpu_core_loads = []

        for sensor in all_sensors:
            # CPU
            if cpu_identifier and sensor.Parent == cpu_identifier:
                if sensor.SensorType == 'Load' and 'cpu core' in sensor.Name.lower():
                    cpu_core_loads.append(sensor.Value)
                elif sensor.SensorType == 'Temperature' and sensor.Name in cpu_temp_sensors:
                    cpu_temp_sensors[sensor.Name] = sensor.Value

            # GPU
            elif gpu_identifier and sensor.Parent == gpu_identifier:
                if sensor.SensorType == 'Load' and 'gpu core' in sensor.Name.lower():
                    gpu_load = sensor.Value
                elif sensor.SensorType == 'Temperature' and 'gpu core' in sensor.Name.lower():
                    gpu_temp = sensor.Value
            
            # MEMORIA - buscar sensores específicos de LibreHardwareMonitor
            elif sensor.SensorType == 'Data':                
                # Probar diferentes variaciones de nombres
                if sensor.Name == 'Memory Used':
                    memory_used_gb = sensor.Value
                elif sensor.Name == 'Memory Available':
                    memory_available_gb = sensor.Value
                    if memory_used_gb is not None:
                        memory_total_gb = memory_used_gb + memory_available_gb
        
        # Calcular promedios CPU
        if cpu_core_loads:
            cpu_load = statistics.mean(cpu_core_loads)
            
        cpu_temp = (cpu_temp_sensors.get("CCD1 (Tdie)") or 
                   cpu_temp_sensors.get("Core (Tctl/Tdie)") or 
                   cpu_temp_sensors.get("CPU Package"))

        # Agregar a muestras para promedio
        if cpu_load is not None: 
            self.cpu_usage_samples.append(cpu_load)
        if gpu_load is not None: 
            self.gpu_usage_samples.append(gpu_load)
        
        # Si no pudimos obtener memoria de LibreHardwareMonitor, usar psutil como fallback
        if memory_used_gb is None or memory_total_gb is None:
            import psutil
            ram_info = psutil.virtual_memory()
            memory_used_gb = ram_info.used / (1024**3)
            memory_total_gb = ram_info.total / (1024**3)

        return {
            'cpu_usage': statistics.mean(self.cpu_usage_samples) if self.cpu_usage_samples else 0,
            'cpu_temp': cpu_temp,
            'gpu_usage': statistics.mean(self.gpu_usage_samples) if self.gpu_usage_samples else 0,
            'gpu_temp': gpu_temp,
            'ram_used_gb': memory_used_gb,
            'ram_total_gb': memory_total_gb,
            'ram_usage': (memory_used_gb / memory_total_gb * 100) if memory_total_gb > 0 else 0,
        }

    def get_quick_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas actuales"""
        with self.data_lock:
            return self.current_data.copy()