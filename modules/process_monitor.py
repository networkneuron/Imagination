"""
Process and Resource Monitoring Module

Monitors system processes, CPU, memory, and disk usage with alerting capabilities.
"""

import os
import psutil
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ProcessInfo:
    """Information about a running process"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: datetime
    command_line: str

@dataclass
class SystemAlert:
    """System alert information"""
    timestamp: datetime
    alert_type: str
    message: str
    severity: str  # low, medium, high, critical
    value: float
    threshold: float

class ProcessMonitor:
    """Monitors system processes and resources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alerts: List[SystemAlert] = []
        self.monitoring = False
        self.alert_callbacks: List[Callable[[SystemAlert], None]] = []
        
        # Default thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "temperature": 80.0,
            "process_count": 1000,
        }
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous system monitoring"""
        if self.monitoring:
            self.logger.warning("Monitoring is already running")
            return
        
        self.monitoring = True
        self.logger.info(f"Starting system monitoring with {interval}s interval")
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.check_system_health()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        self.logger.info("Stopped system monitoring")
    
    def add_alert_callback(self, callback: Callable[[SystemAlert], None]):
        """Add a callback function for system alerts"""
        self.alert_callbacks.append(callback)
    
    def check_system_health(self):
        """Check overall system health and generate alerts"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds["cpu_percent"]:
                self.create_alert(
                    "cpu_high",
                    f"High CPU usage: {cpu_percent:.1f}%",
                    "high" if cpu_percent < 95 else "critical",
                    cpu_percent,
                    self.thresholds["cpu_percent"]
                )
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds["memory_percent"]:
                self.create_alert(
                    "memory_high",
                    f"High memory usage: {memory.percent:.1f}%",
                    "high" if memory.percent < 95 else "critical",
                    memory.percent,
                    self.thresholds["memory_percent"]
                )
            
            # Check disk usage
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            if disk_percent > self.thresholds["disk_percent"]:
                self.create_alert(
                    "disk_high",
                    f"High disk usage: {disk_percent:.1f}%",
                    "high" if disk_percent < 95 else "critical",
                    disk_percent,
                    self.thresholds["disk_percent"]
                )
            
            # Check temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current and entry.current > self.thresholds["temperature"]:
                                self.create_alert(
                                    "temperature_high",
                                    f"High temperature: {name} = {entry.current}°C",
                                    "high" if entry.current < 90 else "critical",
                                    entry.current,
                                    self.thresholds["temperature"]
                                )
            except:
                pass  # Temperature monitoring not available
            
            # Check process count
            process_count = len(psutil.pids())
            if process_count > self.thresholds["process_count"]:
                self.create_alert(
                    "process_count_high",
                    f"High process count: {process_count}",
                    "medium",
                    process_count,
                    self.thresholds["process_count"]
                )
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
    
    def create_alert(self, alert_type: str, message: str, severity: str, value: float, threshold: float):
        """Create a new system alert"""
        alert = SystemAlert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            message=message,
            severity=severity,
            value=value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"ALERT [{severity.upper()}]: {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                "timestamp": datetime.now(),
                "cpu": {
                    "count": cpu_count,
                    "percent": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else None,
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": (disk_usage.used / disk_usage.total) * 100,
                },
                "system": {
                    "boot_time": boot_time,
                    "uptime": datetime.now() - boot_time,
                    "process_count": process_count,
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_processes(self, sort_by: str = "cpu", limit: int = 20) -> List[ProcessInfo]:
        """Get list of running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'cmdline']):
                try:
                    proc_info = proc.info
                    
                    process = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        memory_percent=proc_info['memory_percent'] or 0.0,
                        memory_mb=(proc_info['memory_info'].rss / 1024 / 1024) if proc_info['memory_info'] else 0.0,
                        status=proc_info['status'],
                        create_time=datetime.fromtimestamp(proc_info['create_time']),
                        command_line=' '.join(proc_info['cmdline']) if proc_info['cmdline'] else '',
                    )
                    
                    processes.append(process)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x.memory_percent, reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x.name.lower())
            
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting processes: {e}")
            return []
    
    def get_process_by_name(self, name: str) -> List[ProcessInfo]:
        """Get processes by name"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'cmdline']):
                try:
                    proc_info = proc.info
                    
                    if name.lower() in proc_info['name'].lower():
                        process = ProcessInfo(
                            pid=proc_info['pid'],
                            name=proc_info['name'],
                            cpu_percent=proc_info['cpu_percent'] or 0.0,
                            memory_percent=proc_info['memory_percent'] or 0.0,
                            memory_mb=(proc_info['memory_info'].rss / 1024 / 1024) if proc_info['memory_info'] else 0.0,
                            status=proc_info['status'],
                            create_time=datetime.fromtimestamp(proc_info['create_time']),
                            command_line=' '.join(proc_info['cmdline']) if proc_info['cmdline'] else '',
                        )
                        processes.append(process)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Error getting processes by name {name}: {e}")
            return []
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            
            if force:
                proc.kill()
                self.logger.info(f"Force killed process {pid}")
            else:
                proc.terminate()
                self.logger.info(f"Terminated process {pid}")
            
            return True
            
        except psutil.NoSuchProcess:
            self.logger.warning(f"Process {pid} not found")
            return False
        except psutil.AccessDenied:
            self.logger.error(f"Access denied to kill process {pid}")
            return False
        except Exception as e:
            self.logger.error(f"Error killing process {pid}: {e}")
            return False
    
    def kill_processes_by_name(self, name: str, force: bool = False) -> int:
        """Kill all processes with a specific name"""
        try:
            killed_count = 0
            processes = self.get_process_by_name(name)
            
            for process in processes:
                if self.kill_process(process.pid, force):
                    killed_count += 1
            
            self.logger.info(f"Killed {killed_count} processes with name '{name}'")
            return killed_count
            
        except Exception as e:
            self.logger.error(f"Error killing processes by name {name}: {e}")
            return 0
    
    def get_network_connections(self) -> List[Dict[str, Any]]:
        """Get network connections"""
        try:
            connections = []
            
            for conn in psutil.net_connections(kind='inet'):
                connection_info = {
                    "fd": conn.fd,
                    "family": conn.family.name if conn.family else None,
                    "type": conn.type.name if conn.type else None,
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid,
                }
                connections.append(connection_info)
            
            return connections
            
        except Exception as e:
            self.logger.error(f"Error getting network connections: {e}")
            return []
    
    def get_disk_io(self) -> Dict[str, Any]:
        """Get disk I/O statistics"""
        try:
            io_counters = psutil.disk_io_counters()
            
            if io_counters:
                return {
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                    "read_time": io_counters.read_time,
                    "write_time": io_counters.write_time,
                }
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting disk I/O: {e}")
            return {}
    
    def get_network_io(self) -> Dict[str, Any]:
        """Get network I/O statistics"""
        try:
            io_counters = psutil.net_io_counters()
            
            if io_counters:
                return {
                    "bytes_sent": io_counters.bytes_sent,
                    "bytes_recv": io_counters.bytes_recv,
                    "packets_sent": io_counters.packets_sent,
                    "packets_recv": io_counters.packets_recv,
                    "errin": io_counters.errin,
                    "errout": io_counters.errout,
                    "dropin": io_counters.dropin,
                    "dropout": io_counters.dropout,
                }
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting network I/O: {e}")
            return {}
    
    def set_threshold(self, metric: str, value: float):
        """Set alert threshold for a metric"""
        if metric in self.thresholds:
            self.thresholds[metric] = value
            self.logger.info(f"Set {metric} threshold to {value}")
        else:
            self.logger.warning(f"Unknown metric: {metric}")
    
    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[SystemAlert]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
        
        if severity:
            filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity]
        
        return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.logger.info("Cleared all alerts")
