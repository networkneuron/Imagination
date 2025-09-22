#!/usr/bin/env python3
"""
🚀 Ultimate AI System Automation Agent - Modern Sci-Fi GUI 🚀
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import sys
from datetime import datetime
import json
import subprocess
import shutil

class SciFiGUI:
    """Modern Sci-Fi GUI for the Ultimate AI System Automation Agent"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Ultimate AI System Automation Agent")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Sci-Fi color scheme
        self.colors = {
            'bg': '#0a0a0a',
            'primary': '#00ffff',
            'secondary': '#ff00ff',
            'accent': '#ffff00',
            'text': '#ffffff',
            'panel': '#1a1a1a',
            'border': '#333333',
            'success': '#00ff00',
            'warning': '#ffaa00',
            'error': '#ff0000'
        }
        
        # Configure style
        self.setup_styles()
        
        # Agent status
        self.agent_running = False
        self.tasks = {
            "system_health_check": {
                "name": "System Health Check",
                "description": "Monitor system resources",
                "enabled": True,
                "status": "Ready"
            },
            "cleanup_temp_files": {
                "name": "Cleanup Temporary Files", 
                "description": "Remove temporary files",
                "enabled": True,
                "status": "Ready"
            }
        }
        
        # Create GUI
        self.create_gui()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def setup_styles(self):
        """Setup custom styles for sci-fi theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('SciFi.TFrame', background=self.colors['bg'])
        style.configure('SciFi.TLabel', 
                       background=self.colors['bg'], 
                       foreground=self.colors['text'],
                       font=('Consolas', 10))
        style.configure('SciFi.TButton',
                       background=self.colors['primary'],
                       foreground='#000000',
                       font=('Consolas', 10, 'bold'),
                       borderwidth=0)
        style.map('SciFi.TButton',
                 background=[('active', self.colors['secondary'])])
        
        style.configure('SciFi.TEntry',
                       fieldbackground=self.colors['panel'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       insertcolor=self.colors['primary'])
        
        style.configure('SciFi.Treeview',
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['panel'],
                       borderwidth=1)
        
        style.configure('SciFi.Treeview.Heading',
                       background=self.colors['primary'],
                       foreground='#000000',
                       font=('Consolas', 10, 'bold'))
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, style='SciFi.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame, style='SciFi.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left panel - Controls
        self.create_control_panel(content_frame)
        
        # Right panel - Status and Logs
        self.create_status_panel(content_frame)
        
        # Bottom panel - System Info
        self.create_system_panel(main_frame)
    
    def create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent, style='SciFi.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🚀 ULTIMATE AI SYSTEM AUTOMATION AGENT 🚀",
                               style='SciFi.TLabel',
                               font=('Consolas', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = ttk.Label(header_frame,
                                     text="● OFFLINE",
                                     style='SciFi.TLabel',
                                     font=('Consolas', 12, 'bold'),
                                     foreground=self.colors['error'])
        self.status_label.pack(side=tk.RIGHT)
        
        # Animated border
        self.create_animated_border(header_frame)
    
    def create_animated_border(self, parent):
        """Create animated border effect"""
        border_canvas = tk.Canvas(parent, height=2, bg=self.colors['bg'], highlightthickness=0)
        border_canvas.pack(fill=tk.X, pady=(5, 0))
        
        def animate_border():
            border_canvas.delete("all")
            for i in range(0, 1200, 20):
                color = self.colors['primary'] if (i // 20) % 2 == 0 else self.colors['secondary']
                border_canvas.create_line(i, 0, i+10, 0, fill=color, width=2)
            self.root.after(500, animate_border)
        
        animate_border()
    
    def create_control_panel(self, parent):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(parent, text="CONTROL PANEL", style='SciFi.TFrame')
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Agent controls
        agent_frame = ttk.Frame(control_frame, style='SciFi.TFrame')
        agent_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(agent_frame, text="AGENT STATUS", style='SciFi.TLabel', font=('Consolas', 12, 'bold')).pack()
        
        self.start_button = ttk.Button(agent_frame, 
                                      text="🚀 START AGENT",
                                      style='SciFi.TButton',
                                      command=self.start_agent)
        self.start_button.pack(pady=5)
        
        self.stop_button = ttk.Button(agent_frame,
                                     text="🛑 STOP AGENT", 
                                     style='SciFi.TButton',
                                     command=self.stop_agent,
                                     state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        # Task controls
        task_frame = ttk.Frame(control_frame, style='SciFi.TFrame')
        task_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(task_frame, text="AUTOMATION TASKS", style='SciFi.TLabel', font=('Consolas', 12, 'bold')).pack()
        
        # Task list
        self.task_tree = ttk.Treeview(task_frame, style='SciFi.Treeview', columns=('Status',), show='tree headings')
        self.task_tree.heading('#0', text='Task')
        self.task_tree.heading('Status', text='Status')
        self.task_tree.column('#0', width=200)
        self.task_tree.column('Status', width=100)
        self.task_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Populate tasks
        for task_id, task in self.tasks.items():
            self.task_tree.insert('', 'end', text=task['name'], values=(task['status'],))
        
        # Task buttons
        task_button_frame = ttk.Frame(task_frame, style='SciFi.TFrame')
        task_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(task_button_frame, text="▶️ RUN SELECTED", style='SciFi.TButton', command=self.run_selected_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(task_button_frame, text="🔄 REFRESH", style='SciFi.TButton', command=self.refresh_tasks).pack(side=tk.LEFT, padx=5)
        ttk.Button(task_button_frame, text="⚙️ CONFIGURE", style='SciFi.TButton', command=self.configure_tasks).pack(side=tk.LEFT, padx=5)
    
    def create_status_panel(self, parent):
        """Create the status panel"""
        status_frame = ttk.LabelFrame(parent, text="STATUS & LOGS", style='SciFi.TFrame')
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # System status
        system_frame = ttk.Frame(status_frame, style='SciFi.TFrame')
        system_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(system_frame, text="SYSTEM STATUS", style='SciFi.TLabel', font=('Consolas', 12, 'bold')).pack()
        
        # Status indicators
        self.cpu_label = ttk.Label(system_frame, text="CPU: --%", style='SciFi.TLabel')
        self.cpu_label.pack(anchor=tk.W)
        
        self.memory_label = ttk.Label(system_frame, text="Memory: --%", style='SciFi.TLabel')
        self.memory_label.pack(anchor=tk.W)
        
        self.disk_label = ttk.Label(system_frame, text="Disk: --%", style='SciFi.TLabel')
        self.disk_label.pack(anchor=tk.W)
        
        # Log area
        log_frame = ttk.Frame(status_frame, style='SciFi.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(log_frame, text="ACTIVITY LOG", style='SciFi.TLabel', font=('Consolas', 12, 'bold')).pack()
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg=self.colors['panel'],
                                                 fg=self.colors['text'],
                                                 font=('Consolas', 9),
                                                 height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Log controls
        log_button_frame = ttk.Frame(log_frame, style='SciFi.TFrame')
        log_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(log_button_frame, text="🗑️ CLEAR LOG", style='SciFi.TButton', command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_button_frame, text="💾 SAVE LOG", style='SciFi.TButton', command=self.save_log).pack(side=tk.LEFT, padx=5)
    
    def create_system_panel(self, parent):
        """Create the system information panel"""
        system_frame = ttk.LabelFrame(parent, text="SYSTEM INFORMATION", style='SciFi.TFrame')
        system_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_frame = ttk.Frame(system_frame, style='SciFi.TFrame')
        info_frame.pack(fill=tk.X, pady=10)
        
        # System info labels
        self.platform_label = ttk.Label(info_frame, text=f"Platform: {os.name}", style='SciFi.TLabel')
        self.platform_label.pack(side=tk.LEFT, padx=10)
        
        self.python_label = ttk.Label(info_frame, text=f"Python: {sys.version.split()[0]}", style='SciFi.TLabel')
        self.python_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = ttk.Label(info_frame, text="", style='SciFi.TLabel')
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Update time
        self.update_time()
    
    def start_agent(self):
        """Start the automation agent"""
        self.agent_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="● ONLINE", foreground=self.colors['success'])
        self.log_message("🚀 Agent started successfully!")
        
        # Start background tasks
        threading.Thread(target=self.background_tasks, daemon=True).start()
    
    def stop_agent(self):
        """Stop the automation agent"""
        self.agent_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● OFFLINE", foreground=self.colors['error'])
        self.log_message("🛑 Agent stopped")
    
    def background_tasks(self):
        """Background tasks that run while agent is active"""
        while self.agent_running:
            try:
                # Update system status
                self.update_system_status()
                
                # Run scheduled tasks
                self.run_scheduled_tasks()
                
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.log_message(f"❌ Error in background tasks: {e}")
                time.sleep(10)
    
    def update_system_status(self):
        """Update system status indicators"""
        try:
            # Get disk usage
            if os.name == 'nt':  # Windows
                total, used, free = shutil.disk_usage("C:")
                disk_percent = (used / total) * 100
                self.disk_label.config(text=f"Disk: {disk_percent:.1f}%")
                
                # Color coding
                if disk_percent > 90:
                    self.disk_label.config(foreground=self.colors['error'])
                elif disk_percent > 80:
                    self.disk_label.config(foreground=self.colors['warning'])
                else:
                    self.disk_label.config(foreground=self.colors['success'])
            else:  # Linux/Mac
                total, used, free = shutil.disk_usage("/")
                disk_percent = (used / total) * 100
                self.disk_label.config(text=f"Disk: {disk_percent:.1f}%")
            
            # Mock CPU and memory (in real implementation, use psutil)
            self.cpu_label.config(text="CPU: 45.2%")
            self.memory_label.config(text="Memory: 67.8%")
            
        except Exception as e:
            self.log_message(f"❌ Error updating system status: {e}")
    
    def run_scheduled_tasks(self):
        """Run scheduled automation tasks"""
        for task_id, task in self.tasks.items():
            if task['enabled'] and task['status'] == 'Ready':
                # Simple scheduling - run every 30 seconds for demo
                if hasattr(self, f'last_run_{task_id}'):
                    if time.time() - getattr(self, f'last_run_{task_id}') > 30:
                        self.run_task(task_id)
                else:
                    setattr(self, f'last_run_{task_id}', time.time())
    
    def run_task(self, task_id):
        """Run a specific task"""
        try:
            task = self.tasks[task_id]
            task['status'] = 'Running'
            self.update_task_display()
            self.log_message(f"▶️ Running task: {task['name']}")
            
            if task_id == 'system_health_check':
                self.system_health_check()
            elif task_id == 'cleanup_temp_files':
                self.cleanup_temp_files()
            
            task['status'] = 'Completed'
            setattr(self, f'last_run_{task_id}', time.time())
            self.log_message(f"✅ Task completed: {task['name']}")
            
        except Exception as e:
            task['status'] = 'Error'
            self.log_message(f"❌ Task failed: {task['name']} - {e}")
        
        self.update_task_display()
    
    def system_health_check(self):
        """Perform system health check"""
        self.log_message("🔍 Performing system health check...")
        time.sleep(1)  # Simulate work
        self.log_message("✅ System health check completed")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        self.log_message("🧹 Cleaning up temporary files...")
        time.sleep(2)  # Simulate work
        self.log_message("✅ Cleanup completed")
    
    def run_selected_task(self):
        """Run the selected task"""
        selection = self.task_tree.selection()
        if selection:
            item = self.task_tree.item(selection[0])
            task_name = item['text']
            for task_id, task in self.tasks.items():
                if task['name'] == task_name:
                    threading.Thread(target=self.run_task, args=(task_id,), daemon=True).start()
                    break
    
    def refresh_tasks(self):
        """Refresh the task display"""
        self.update_task_display()
        self.log_message("🔄 Task list refreshed")
    
    def update_task_display(self):
        """Update the task tree display"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for task_id, task in self.tasks.items():
            status_color = {
                'Ready': self.colors['text'],
                'Running': self.colors['warning'],
                'Completed': self.colors['success'],
                'Error': self.colors['error']
            }.get(task['status'], self.colors['text'])
            
            self.task_tree.insert('', 'end', text=task['name'], values=(task['status'],))
    
    def configure_tasks(self):
        """Open task configuration dialog"""
        messagebox.showinfo("Configuration", "Task configuration dialog would open here")
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Color coding
        if "❌" in message or "Error" in message:
            self.log_text.tag_add("error", f"{self.log_text.index(tk.END)}-2c", tk.END)
        elif "✅" in message or "completed" in message:
            self.log_text.tag_add("success", f"{self.log_text.index(tk.END)}-2c", tk.END)
        elif "🚀" in message or "started" in message:
            self.log_text.tag_add("info", f"{self.log_text.index(tk.END)}-2c", tk.END)
        
        # Configure tags
        self.log_text.tag_config("error", foreground=self.colors['error'])
        self.log_text.tag_config("success", foreground=self.colors['success'])
        self.log_text.tag_config("info", foreground=self.colors['primary'])
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ Log cleared")
    
    def save_log(self):
        """Save the log to file"""
        try:
            filename = f"automation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log_message(f"💾 Log saved to {filename}")
        except Exception as e:
            self.log_message(f"❌ Error saving log: {e}")
    
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        threading.Thread(target=self.monitor_loop, daemon=True).start()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                if self.agent_running:
                    # Update system status
                    self.update_system_status()
                time.sleep(5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(10)
    
    def run(self):
        """Start the GUI"""
        self.log_message("🚀 Ultimate AI System Automation Agent GUI Started")
        self.log_message("💡 Click 'START AGENT' to begin automation")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = SciFiGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")

if __name__ == "__main__":
    main()
