import psutil
import time
import datetime
import csv
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

class BandwidthMonitor:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.total_download = 0
        self.total_upload = 0
        self.hourly_data = defaultdict(lambda: {'download': 0, 'upload': 0})
        self.interval = 2  # seconds
        self.running = True

    def get_network_usage(self):
        """Get current network I/O stats"""
        net_io = psutil.net_io_counters()
        return net_io.bytes_sent, net_io.bytes_recv

    def format_bytes(self, bytes_value):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} TB"

    def monitor(self, duration_seconds=None):
        """Start monitoring"""
        print("🚀 Bandwidth Monitor Started (Press Ctrl+C to stop)")
        print("="*60)
        print(f"Session Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        last_download = 0
        last_upload = 0

        try:
            while self.running:
                upload, download = self.get_network_usage()

                # Calculate speed
                down_speed = (download - last_download) / self.interval
                up_speed = (upload - last_upload) / self.interval

                # Update totals
                self.total_download += (download - last_download)
                self.total_upload += (upload - last_upload)

                # Hourly tracking
                current_hour = datetime.datetime.now().hour
                self.hourly_data[current_hour]['download'] += (download - last_download)
                self.hourly_data[current_hour]['upload'] += (upload - last_upload)

                # Display
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
                      f"↓ {self.format_bytes(down_speed)}/s | "
                      f"↑ {self.format_bytes(up_speed)}/s | "
                      f"Total ↓ {self.format_bytes(self.total_download)} | "
                      f"↑ {self.format_bytes(self.total_upload)}", end='\r')

                last_download = download
                last_upload = upload

                time.sleep(self.interval)

                if duration_seconds and (time.time() - self.start_time.timestamp() > duration_seconds):
                    break

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user.")
        finally:
            self.save_report()

    def save_report(self):
        """Save data and generate report"""
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time

        # Save to CSV
        with open('bandwidth_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Total_Download_GB', 'Total_Upload_GB', 'Duration_Minutes'])
            writer.writerow([
                end_time.strftime('%Y-%m-%d %H:%M'),
                round(self.total_download / (1024**3), 4),
                round(self.total_upload / (1024**3), 4),
                round(duration.total_seconds() / 60, 2)
            ])

        # Generate Report
        print("\n" + "="*60)
        print("📊 BANDWIDTH REPORT")
        print("="*60)
        print(f"Session Duration : {duration}")
        print(f"Total Downloaded : {self.format_bytes(self.total_download)}")
        print(f"Total Uploaded   : {self.format_bytes(self.total_upload)}")
        print(f"Peak Hour        : {max(self.hourly_data, key=lambda h: self.hourly_data[h]['download'])}:00")

        self.generate_graph()

    def generate_graph(self):
        """Generate usage graph"""
        hours = sorted(self.hourly_data.keys())
        downloads = [self.hourly_data[h]['download'] / (1024**2) for h in hours]  # in MB

        plt.figure(figsize=(10, 6))
        plt.bar(hours, downloads, color='skyblue')
        plt.title('Hourly Download Usage (MB)')
        plt.xlabel('Hour of Day')
        plt.ylabel('Data Downloaded (MB)')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        plt.savefig('bandwidth_usage.png')
        plt.show()

        print("📈 Graph saved as 'bandwidth_usage.png'")


# ====================== RUN THE MONITOR ======================
if __name__ == "__main__":
    monitor = BandwidthMonitor()
    monitor.monitor()  # Run indefinitely until Ctrl+C