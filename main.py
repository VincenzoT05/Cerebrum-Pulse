import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import time
import csv
from math import pi
from scipy.interpolate import make_interp_spline
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CerebrumPulsePro:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.max_points = 40
        self.start_time = time.time()

        self.cpu_history = []
        self.ram_history = []
        self.net_history = []
        self.time_history = []
        self.temp_history = []
        self.disk_history = []

        self.paused = False

        self.setup_style()
        self.create_splash()

    def setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # Palette JetBrains-like dark theme
        bg_main = '#242424'
        bg_frame = '#2d2d2d'
        fg_primary = '#bbbbbb'
        fg_highlight = '#a6e22e'  # verde lime
        btn_bg = '#3c3f41'
        btn_hover = '#4caf50'
        btn_fg = '#eeeeee'

        # Main window bg
        self.root.configure(bg=bg_main)

        style.configure('.', background=bg_main, foreground=fg_primary, font=('JetBrains Mono', 11))
        style.configure('TFrame', background=bg_frame)
        style.configure('TLabel', background=bg_main, foreground=fg_primary, font=('JetBrains Mono', 12))

        style.configure('Header.TLabel', font=('JetBrains Mono', 22, 'bold'), foreground=fg_highlight, background=bg_main)

        style.configure('TButton',
                        background=btn_bg,
                        foreground=btn_fg,
                        font=('JetBrains Mono', 12, 'bold'),
                        padding=10,
                        relief='flat')
        style.map('TButton',
                  background=[('active', btn_hover), ('!disabled', btn_bg)],
                  foreground=[('active', '#ffffff'), ('!disabled', btn_fg)])

        style.configure('TProgressbar', troughcolor=bg_frame, background=btn_hover, thickness=14)

    def create_splash(self):
        self.splash = tk.Toplevel()
        self.splash.title("Cerebrum Pulse - Avvio")
        self.splash.geometry("450x320")
        self.splash.configure(bg='#1e1e1e')
        self.splash.resizable(False, False)
        ttk.Label(self.splash, text="CEREBRUM PULSE PRO",
                  font=("JetBrains Mono", 30, "bold"),
                  background='#1e1e1e',
                  foreground='#a6e22e').pack(pady=(50, 20))
        self.progress = ttk.Progressbar(self.splash, orient=tk.HORIZONTAL, length=350, mode='determinate')
        self.progress.pack(pady=20)
        self.status = ttk.Label(self.splash, text="Avvio del sistema...", font=("JetBrains Mono", 14), background='#1e1e1e', foreground='#bbbbbb')
        self.status.pack()
        self.progress_val = 0
        self.splash.after(50, self.progress_step)

    def progress_step(self):
        self.progress_val += 3
        self.progress['value'] = self.progress_val
        dots = (self.progress_val // 10) % 4
        self.status.config(text=f"Avvio del sistema{'.' * dots}")
        if self.progress_val < 100:
            self.splash.after(50, self.progress_step)
        else:
            self.splash.destroy()
            self.launch_main()

    def launch_main(self):
        self.root.deiconify()
        self.root.title("Cerebrum Pulse Pro - Monitor Sistema")
        self.root.geometry("900x820")
        self.root.configure(bg='#242424')

        header = ttk.Label(self.root, text="Cerebrum Pulse Pro - Monitoraggio in tempo reale", style='Header.TLabel')
        header.pack(pady=15)

        info_frame = ttk.Frame(self.root)
        info_frame.pack(pady=10, fill='x', padx=10)

        label_args = dict(font=('JetBrains Mono', 15, 'bold'), padding=8)

        self.cpu_label = ttk.Label(info_frame, text="CPU: -- %", **label_args)
        self.cpu_label.grid(row=0, column=0, padx=20, pady=6)

        self.ram_label = ttk.Label(info_frame, text="RAM: -- %", **label_args)
        self.ram_label.grid(row=0, column=1, padx=20, pady=6)

        self.net_label = ttk.Label(info_frame, text="Rete: -- MB", **label_args)
        self.net_label.grid(row=0, column=2, padx=20, pady=6)

        self.temp_label = ttk.Label(info_frame, text="Temperatura CPU: -- °C", **label_args)
        self.temp_label.grid(row=1, column=0, padx=20, pady=6)

        self.disk_label = ttk.Label(info_frame, text="Disco: -- % usato", **label_args)
        self.disk_label.grid(row=1, column=1, padx=20, pady=6)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)

        self.pause_btn = ttk.Button(btn_frame, text="Pausa", command=self.toggle_pause)
        self.pause_btn.grid(row=0, column=0, padx=15)

        self.export_btn = ttk.Button(btn_frame, text="Esporta CSV", command=self.export_csv)
        self.export_btn.grid(row=0, column=1, padx=15)

        self.exit_btn = ttk.Button(btn_frame, text="Esci", command=self.root.quit)
        self.exit_btn.grid(row=0, column=2, padx=15)

        # Grafici: Figure con 2 subplot e styling moderno
        self.fig = Figure(figsize=(8.5, 7), dpi=110, facecolor='#242424')

        self.ax_line = self.fig.add_subplot(211, facecolor='#2d2d2d')
        self.ax_radar = self.fig.add_subplot(223, polar=True, facecolor='#2d2d2d')
        self.ax_doughnut = self.fig.add_subplot(224, facecolor='#242424')

        self.fig.tight_layout(pad=4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.update_stats()

    # (Restante codice identico, no cambiamenti)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="Riprendi" if self.paused else "Pausa")

    def export_csv(self):
        if not self.time_history:
            messagebox.showwarning("Nessun dato", "Nessun dato da esportare.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                title="Salva dati monitoraggio")
        if not filepath:
            return
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Tempo (s)", "CPU %", "RAM %", "Rete MB", "Temp CPU (°C)", "Uso Disco %"])
                for i in range(len(self.time_history)):
                    writer.writerow([
                        f"{self.time_history[i]:.1f}",
                        f"{self.cpu_history[i]:.1f}",
                        f"{self.ram_history[i]:.1f}",
                        f"{self.net_history[i]:.2f}",
                        f"{self.temp_history[i] if i < len(self.temp_history) else '--'}",
                        f"{self.disk_history[i] if i < len(self.disk_history) else '--'}"
                    ])
            messagebox.showinfo("Esportazione completata", f"Dati esportati in {filepath}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione: {e}")

    def smooth_line(self, x, y, points=200):
        if len(x) < 4:
            return x, y
        x = np.array(x)
        y = np.array(y)
        x_new = np.linspace(x.min(), x.max(), points)
        spl = make_interp_spline(x, y, k=3)
        y_smooth = spl(x_new)
        return x_new, y_smooth

    def radar_chart(self, values, labels):
        N = len(values)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        values += values[:1]

        self.ax_radar.clear()
        self.ax_radar.set_theta_offset(pi / 2)
        self.ax_radar.set_theta_direction(-1)
        self.ax_radar.set_rlabel_position(0)
        self.ax_radar.set_ylim(0, 100)
        self.ax_radar.grid(color='#555555', linestyle='dotted')
        self.ax_radar.set_facecolor('#2d2d2d')

        self.ax_radar.plot(angles, values, color='#a6e22e', linewidth=2, linestyle='solid')
        self.ax_radar.fill(angles, values, color='#a6e22e', alpha=0.25)

        self.ax_radar.set_xticks(angles[:-1])
        self.ax_radar.set_xticklabels(labels, color='white', fontsize=11)

    def doughnut_chart(self, used_percent):
        self.ax_doughnut.clear()
        sizes = [used_percent, 100 - used_percent]
        colors = ['#f44336', '#444444']
        wedges, _ = self.ax_doughnut.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.35))
        self.ax_doughnut.text(0, 0, f"{used_percent:.1f}%", ha='center', va='center', fontsize=22, color='#a6e22e', fontweight='bold')

    def update_stats(self):
        if not self.paused:
            now = time.time() - self.start_time
            self.time_history.append(now)

            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            net = psutil.net_io_counters().bytes_sent / 1024 / 1024  # MB inviati
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    temp = temps['coretemp'][0].current
                elif 'cpu-thermal' in temps:
                    temp = temps['cpu-thermal'][0].current
                else:
                    temp = None
            except Exception:
                temp = None

            disk = psutil.disk_usage('/').percent

            self.cpu_history.append(cpu)
            self.ram_history.append(ram)
            self.net_history.append(net)
            if temp is not None:
                self.temp_history.append(temp)
            self.disk_history.append(disk)

            if len(self.cpu_history) > self.max_points:
                self.cpu_history.pop(0)
                self.ram_history.pop(0)
                self.net_history.pop(0)
                if self.temp_history:
                    self.temp_history.pop(0)
                self.disk_history.pop(0)
                self.time_history.pop(0)

            self.cpu_label.config(text=f"CPU: {cpu:.1f} %")
            self.ram_label.config(text=f"RAM: {ram:.1f} %")
            self.net_label.config(text=f"Rete: {net:.2f} MB")
            self.temp_label.config(text=f"Temperatura CPU: {temp:.1f} °C" if temp else "Temperatura CPU: -- °C")
            self.disk_label.config(text=f"Disco: {disk:.1f} % usato")

            # Grafico a linea smooth CPU e RAM
            self.ax_line.clear()
            self.ax_line.set_facecolor('#2d2d2d')
            self.ax_line.grid(color='#555555', linestyle='dotted', alpha=0.7)
            self.ax_line.set_xlim(self.time_history[0], self.time_history[-1])
            self.ax_line.set_ylim(0, 100)
            self.ax_line.set_ylabel('Percentuale %', color='white')
            self.ax_line.set_xlabel('Tempo (s)', color='white')
            self.ax_line.tick_params(axis='x', colors='white')
            self.ax_line.tick_params(axis='y', colors='white')

            x_smooth, y_cpu = self.smooth_line(self.time_history, self.cpu_history)
            _, y_ram = self.smooth_line(self.time_history, self.ram_history)

            self.ax_line.plot(x_smooth, y_cpu, color='#a6e22e', linewidth=2, label='CPU %')
            self.ax_line.plot(x_smooth, y_ram, color='#66d9ef', linewidth=2, label='RAM %')
            self.ax_line.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='#a6e22e', labelcolor='white')

            # Radar chart con statistiche correnti
            radar_values = [cpu, ram, disk, 100 - disk, 100 - ram]
            radar_labels = ['CPU', 'RAM', 'Disco Usato', 'Disco Libero', 'RAM Libera']
            self.radar_chart(radar_values, radar_labels)

            # Doughnut chart uso disco
            self.doughnut_chart(disk)

            self.canvas.draw()

        self.root.after(900, self.update_stats)


if __name__ == '__main__':
    root = tk.Tk()
    app = CerebrumPulsePro(root)
    root.mainloop()
