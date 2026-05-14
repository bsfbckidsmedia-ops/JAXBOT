#!/usr/bin/env python3
"""
VRChat Bot Launcher
Interactive GUI launcher for selecting bot modes and features.
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, List
import json

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

class BotLauncher:
    """Interactive bot launcher with GUI and CLI options."""
    
    def __init__(self):
        self.bot_process = None
        self.current_mode = None
        self.log_file = "launcher.log"
        self.config_file = "launcher_config.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Available modes
        self.modes = {
            "1": {
                "name": "VRChat Mode",
                "description": "Full VRChat integration with system helper",
                "script": "dual_mode_bot.py",
                "env": {"DEFAULT_MODE": "vrchat"},
                "icon": "🎮"
            },
            "2": {
                "name": "Standby Mode", 
                "description": "Minimal resource usage with system monitoring",
                "script": "dual_mode_bot.py",
                "env": {"DEFAULT_MODE": "standby"},
                "icon": "⏸️"
            },
            "3": {
                "name": "System Helper Mode",
                "description": "Disk cleanup and system optimization only",
                "script": "dual_mode_bot.py", 
                "env": {"DEFAULT_MODE": "system_helper"},
                "icon": "🛠️"
            },
            "4": {
                "name": "Minimal VRChat",
                "description": "Lightweight VRChat mode for low resources",
                "script": "minimal_main.py",
                "env": {},
                "icon": "🎯"
            },
            "5": {
                "name": "Exit Launcher",
                "description": "Close the launcher",
                "script": None,
                "env": {},
                "icon": "🚪"
            }
        }
    
    def load_config(self) -> Dict:
        """Load launcher configuration."""
        default_config = {
            "last_mode": "1",
            "auto_start": False,
            "show_console": True,
            "window_position": {"x": 100, "y": 100},
            "window_size": {"width": 600, "height": 500}
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
        except Exception:
            pass
        
        return default_config
    
    def save_config(self):
        """Save launcher configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def log(self, message: str):
        """Log message to file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        except Exception:
            pass
    
    def start_bot(self, mode_key: str) -> bool:
        """Start the bot in the specified mode."""
        if mode_key not in self.modes or self.modes[mode_key]["script"] is None:
            return False
        
        mode = self.modes[mode_key]
        script = mode["script"]
        
        if not os.path.exists(script):
            self.log(f"Script not found: {script}")
            return False
        
        try:
            # Stop existing bot if running
            if self.bot_process and self.bot_process.poll() is None:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            
            # Prepare environment
            env = os.environ.copy()
            env.update(mode["env"])
            
            # Start the bot
            self.log(f"Starting bot in {mode['name']} with script {script}")
            
            if self.config.get("show_console", True):
                # Show console window
                self.bot_process = subprocess.Popen(
                    [sys.executable, script],
                    env=env,
                    cwd=os.getcwd(),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
            else:
                # Hide console window
                if os.name == 'nt':
                    self.bot_process = subprocess.Popen(
                        [sys.executable, script],
                        env=env,
                        cwd=os.getcwd(),
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    self.bot_process = subprocess.Popen(
                        [sys.executable, script],
                        env=env,
                        cwd=os.getcwd(),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            
            self.current_mode = mode_key
            self.config["last_mode"] = mode_key
            self.save_config()
            
            return True
            
        except Exception as e:
            self.log(f"Failed to start bot: {e}")
            return False
    
    def stop_bot(self) -> bool:
        """Stop the running bot."""
        if self.bot_process and self.bot_process.poll() is None:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
                self.log("Bot stopped successfully")
                return True
            except Exception as e:
                self.log(f"Failed to stop bot: {e}")
                try:
                    self.bot_process.kill()
                    self.bot_process.wait(timeout=5)
                    self.log("Bot killed forcefully")
                    return True
                except Exception:
                    pass
        
        return False
    
    def is_bot_running(self) -> bool:
        """Check if bot is currently running."""
        return self.bot_process and self.bot_process.poll() is None

class LauncherGUI:
    """GUI version of the launcher."""
    
    def __init__(self):
        self.launcher = BotLauncher()
        self.root = None
        self.status_var = None
        self.log_text = None
        
    def create_gui(self):
        """Create the GUI interface."""
        self.root = tk.Tk()
        self.root.title("VRChat Bot Launcher")
        self.root.geometry(f"{self.launcher.config['window_size']['width']}x{self.launcher.config['window_size']['height']}")
        self.root.resizable(True, True)
        
        # Set window position
        x = self.launcher.config['window_position']['x']
        y = self.launcher.config['window_position']['y']
        self.root.geometry(f"+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 VRChat Bot Launcher", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Select Mode", padding="10")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        mode_frame.columnconfigure(0, weight=1)
        
        # Create mode buttons
        for i, (key, mode) in enumerate(self.launcher.modes.items()):
            if mode["script"] is None:  # Skip exit option in GUI
                continue
                
            btn_frame = ttk.Frame(mode_frame)
            btn_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            btn_frame.columnconfigure(1, weight=1)
            
            # Mode number
            num_label = ttk.Label(btn_frame, text=f"[{key}]", font=('Arial', 10, 'bold'))
            num_label.grid(row=0, column=0, padx=(0, 10))
            
            # Mode button
            btn_text = f"{mode['icon']} {mode['name']}"
            btn = ttk.Button(btn_frame, text=btn_text, 
                           command=lambda k=key: self.start_mode(k))
            btn.grid(row=0, column=1, sticky=(tk.W, tk.E))
            
            # Description
            desc_label = ttk.Label(btn_frame, text=mode['description'], 
                                 font=('Arial', 8), foreground='gray')
            desc_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(2, 0))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready to start bot...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, pady=(10, 0))
        
        # Stop button
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop Bot", 
                                 command=self.stop_bot, state='disabled')
        self.stop_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Clear log button
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear Log", 
                             command=self.clear_log)
        clear_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Settings button
        settings_btn = ttk.Button(control_frame, text="⚙️ Settings", 
                                command=self.show_settings)
        settings_btn.grid(row=0, column=2)
        
        # Start status update loop
        self.update_status()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        return self.root
    
    def start_mode(self, mode_key: str):
        """Start bot in selected mode."""
        if self.launcher.is_bot_running():
            messagebox.showwarning("Bot Running", 
                                  "Please stop the current bot before starting a new mode.")
            return
        
        mode = self.launcher.modes[mode_key]
        success = self.launcher.start_bot(mode_key)
        
        if success:
            self.log_text.insert(tk.END, f"✅ Started {mode['name']}\n")
            self.log_text.see(tk.END)
            self.stop_btn.config(state='normal')
        else:
            messagebox.showerror("Error", f"Failed to start {mode['name']}")
            self.log_text.insert(tk.END, f"❌ Failed to start {mode['name']}\n")
            self.log_text.see(tk.END)
    
    def stop_bot(self):
        """Stop the running bot."""
        success = self.launcher.stop_bot()
        
        if success:
            self.log_text.insert(tk.END, "⏹️ Bot stopped\n")
            self.log_text.see(tk.END)
            self.stop_btn.config(state='disabled')
        else:
            messagebox.showerror("Error", "Failed to stop bot")
    
    def clear_log(self):
        """Clear the log text area."""
        self.log_text.delete(1.0, tk.END)
    
    def update_status(self):
        """Update status display."""
        if self.launcher.is_bot_running():
            mode = self.launcher.modes.get(self.launcher.current_mode, {})
            status = f"🟢 Running: {mode.get('name', 'Unknown')}"
            self.status_var.set(status)
        else:
            self.status_var.set("🔴 Bot stopped")
        
        # Schedule next update
        if self.root:
            self.root.after(1000, self.update_status)
    
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Make it modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings frame
        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Show console checkbox
        show_console_var = tk.BooleanVar(value=self.launcher.config.get("show_console", True))
        show_console_cb = ttk.Checkbutton(frame, text="Show console window", 
                                         variable=show_console_var)
        show_console_cb.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Auto-start checkbox
        auto_start_var = tk.BooleanVar(value=self.launcher.config.get("auto_start", False))
        auto_start_cb = ttk.Checkbutton(frame, text="Auto-start last mode", 
                                       variable=auto_start_var)
        auto_start_cb.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Last mode selection
        ttk.Label(frame, text="Default mode:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        mode_var = tk.StringVar(value=self.launcher.config.get("last_mode", "1"))
        mode_combo = ttk.Combobox(frame, textvariable=mode_var, state="readonly")
        mode_combo['values'] = [f"{k} - {v['name']}" for k, v in self.launcher.modes.items() if v["script"]]
        mode_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, pady=10)
        
        def save_settings():
            self.launcher.config["show_console"] = show_console_var.get()
            self.launcher.config["auto_start"] = auto_start_var.get()
            # Extract mode key from combo selection
            selected = mode_var.get()
            if selected:
                self.launcher.config["last_mode"] = selected.split(" - ")[0]
            self.launcher.save_config()
            settings_window.destroy()
        
        save_btn = ttk.Button(btn_frame, text="Save", command=save_settings)
        save_btn.grid(row=0, column=0, padx=(0, 5))
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=settings_window.destroy)
        cancel_btn.grid(row=0, column=1)
    
    def on_closing(self):
        """Handle window closing."""
        # Save window position
        if self.root:
            self.launcher.config['window_position']['x'] = self.root.winfo_x()
            self.launcher.config['window_position']['y'] = self.root.winfo_y()
            self.launcher.config['window_size']['width'] = self.root.winfo_width()
            self.launcher.config['window_size']['height'] = self.root.winfo_height()
            self.launcher.save_config()
        
        # Stop bot if running
        if self.launcher.is_bot_running():
            if messagebox.askokcancel("Quit", "Bot is still running. Stop it and quit?"):
                self.launcher.stop_bot()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run the GUI."""
        if not TKINTER_AVAILABLE:
            print("❌ Tkinter not available. Falling back to CLI mode.")
            return False
        
        try:
            root = self.create_gui()
            root.mainloop()
            return True
        except Exception as e:
            print(f"❌ GUI error: {e}")
            return False

class LauncherCLI:
    """CLI version of the launcher."""
    
    def __init__(self):
        self.launcher = BotLauncher()
    
    def show_menu(self):
        """Display the menu."""
        print("\n" + "="*50)
        print("🤖 VRChat Bot Launcher")
        print("="*50)
        
        for key, mode in self.launcher.modes.items():
            if mode["script"] is None:
                print(f"[{key}] {mode['icon']} {mode['name']}")
            else:
                print(f"[{key}] {mode['icon']} {mode['name']}")
                print(f"     {mode['description']}")
        
        print("="*50)
        
        # Show current status
        if self.launcher.is_bot_running():
            mode = self.launcher.modes.get(self.launcher.current_mode, {})
            print(f"🟢 Currently running: {mode.get('name', 'Unknown')}")
        else:
            print("🔴 No bot running")
        
        print()
    
    def run(self):
        """Run the CLI interface."""
        while True:
            self.show_menu()
            
            try:
                choice = input("Select option [1-5]: ").strip()
                
                if choice not in self.launcher.modes:
                    print("❌ Invalid choice. Please try again.")
                    input("Press Enter to continue...")
                    continue
                
                mode = self.launcher.modes[choice]
                
                if mode["script"] is None:
                    # Exit option
                    if self.launcher.is_bot_running():
                        stop = input("Bot is running. Stop it? (y/n): ").lower()
                        if stop == 'y':
                            self.launcher.stop_bot()
                    print("👋 Goodbye!")
                    break
                
                # Start bot
                if self.launcher.is_bot_running():
                    stop = input("Bot is already running. Stop it first? (y/n): ").lower()
                    if stop == 'y':
                        self.launcher.stop_bot()
                    else:
                        continue
                
                print(f"🚀 Starting {mode['name']}...")
                success = self.launcher.start_bot(choice)
                
                if success:
                    print(f"✅ {mode['name']} started successfully!")
                    print("📝 Bot is running in the background.")
                    print("💡 Press Enter to return to menu, or Ctrl+C to exit")
                    
                    try:
                        input()
                    except KeyboardInterrupt:
                        print("\n👋 Goodbye!")
                        break
                else:
                    print(f"❌ Failed to start {mode['name']}")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point."""
    print("🤖 VRChat Bot Launcher")
    print("Loading...")
    
    # Check if we should use GUI
    use_gui = TKINTER_AVAILABLE and "--cli" not in sys.argv
    
    if use_gui:
        # Try GUI first
        gui = LauncherGUI()
        if not gui.run():
            # Fallback to CLI
            print("Falling back to CLI mode...")
            cli = LauncherCLI()
            cli.run()
    else:
        # Use CLI
        cli = LauncherCLI()
        cli.run()

if __name__ == "__main__":
    main()
