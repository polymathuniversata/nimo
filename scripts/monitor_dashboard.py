#!/usr/bin/env python3
"""
Nimo Platform - Real-time Performance Monitoring Dashboard

This script provides real-time monitoring and performance metrics for the Nimo platform,
including:
- Service health monitoring
- Performance metrics collection
- Resource usage tracking
- Alert generation
- Historical data analysis
"""

import os
import sys
import json
import time
import psutil
import requests
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import curses
import redis
from collections import defaultdict, deque

class PerformanceMonitor:
    """Real-time performance monitoring dashboard"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.monitoring_active = False
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 data points
        self.alerts = []
        self.last_health_check = None
        self.performance_history = []

        # Redis connection for cache metrics
        self.redis_client = None
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        except:
            pass

    def start_monitoring(self, interval: int = 5):
        """Start real-time monitoring"""
        self.monitoring_active = True
        self.log("📊 Starting real-time performance monitoring...")

        try:
            while self.monitoring_active:
                self.collect_metrics()
                self.check_alerts()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stop monitoring and save data"""
        self.monitoring_active = False
        self.save_performance_data()
        self.log("⏹️  Performance monitoring stopped")

    def collect_metrics(self):
        """Collect all performance metrics"""
        timestamp = datetime.now()

        # System metrics
        self.collect_system_metrics(timestamp)

        # Service health metrics
        self.collect_service_metrics(timestamp)

        # Application metrics
        self.collect_application_metrics(timestamp)

        # Cache metrics
        if self.redis_client:
            self.collect_cache_metrics(timestamp)

    def collect_system_metrics(self, timestamp: datetime):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append((timestamp, cpu_percent))

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append((timestamp, memory.percent))
            self.metrics['memory_total'].append((timestamp, memory.total / (1024**3)))  # GB

            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'].append((timestamp, disk.percent))

            # Network I/O
            network = psutil.net_io_counters()
            self.metrics['network_sent'].append((timestamp, network.bytes_sent / (1024**2)))  # MB
            self.metrics['network_recv'].append((timestamp, network.bytes_recv / (1024**2)))  # MB

            # Process count
            self.metrics['process_count'].append((timestamp, len(psutil.pids())))

        except Exception as e:
            self.log(f"Error collecting system metrics: {e}", "ERROR")

    def collect_service_metrics(self, timestamp: datetime):
        """Collect service health metrics"""
        try:
            # Backend API health
            api_result = self.check_endpoint('/api/health')
            if api_result:
                self.metrics['api_response_time'].append((timestamp, api_result.get('response_time', 0)))
                self.metrics['api_status'].append((timestamp, 1 if api_result.get('status_code') == 200 else 0))

            # Redis health
            redis_result = self.check_endpoint('/api/health/services/redis')
            if redis_result:
                cache_stats = redis_result.get('cache_stats', {})
                self.metrics['redis_hit_rate'].append((timestamp, cache_stats.get('hit_rate', 0)))
                self.metrics['redis_memory_used'].append((timestamp, self._parse_memory_usage(cache_stats.get('memory_used', '0M'))))

            # IPFS health
            ipfs_result = self.check_endpoint('/api/health/services/ipfs')
            if ipfs_result:
                self.metrics['ipfs_response_time'].append((timestamp, ipfs_result.get('response_time', 0)))

            # Cardano health
            cardano_result = self.check_endpoint('/api/cardano/network-info')
            if cardano_result:
                self.metrics['cardano_response_time'].append((timestamp, cardano_result.get('response_time', 0)))

        except Exception as e:
            self.log(f"Error collecting service metrics: {e}", "ERROR")

    def collect_application_metrics(self, timestamp: datetime):
        """Collect application-specific metrics"""
        try:
            # Simulate application metrics (in production, these would come from application logs)
            # For now, we'll generate some sample data
            self.metrics['active_users'].append((timestamp, self._get_random_metric(10, 100)))
            self.metrics['contributions_per_minute'].append((timestamp, self._get_random_metric(1, 20)))
            self.metrics['transactions_per_minute'].append((timestamp, self._get_random_metric(5, 50)))
            self.metrics['ai_requests_per_minute'].append((timestamp, self._get_random_metric(2, 30)))

        except Exception as e:
            self.log(f"Error collecting application metrics: {e}", "ERROR")

    def collect_cache_metrics(self, timestamp: datetime):
        """Collect Redis cache metrics"""
        if not self.redis_client:
            return

        try:
            # Redis info
            info = self.redis_client.info()

            self.metrics['redis_connected_clients'].append((timestamp, info.get('connected_clients', 0)))
            self.metrics['redis_used_memory'].append((timestamp, info.get('used_memory', 0) / (1024**2)))  # MB
            self.metrics['redis_commands_per_sec'].append((timestamp, info.get('instantaneous_ops_per_sec', 0)))
            self.metrics['redis_keyspace_hits'].append((timestamp, info.get('keyspace_hits', 0)))
            self.metrics['redis_keyspace_misses'].append((timestamp, info.get('keyspace_misses', 0)))

            # Calculate hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            self.metrics['redis_calculated_hit_rate'].append((timestamp, hit_rate))

        except Exception as e:
            self.log(f"Error collecting cache metrics: {e}", "ERROR")

    def check_endpoint(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Check a single endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms

            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'data': response.json() if response.content else None
            }
        except Exception:
            return None

    def check_alerts(self):
        """Check for alert conditions"""
        try:
            # CPU alert
            if self.metrics['cpu_usage']:
                latest_cpu = self.metrics['cpu_usage'][-1][1]
                if latest_cpu > 90:
                    self.add_alert('HIGH_CPU_USAGE', f'CPU usage at {latest_cpu".1f"}%', 'WARNING')

            # Memory alert
            if self.metrics['memory_usage']:
                latest_memory = self.metrics['memory_usage'][-1][1]
                if latest_memory > 85:
                    self.add_alert('HIGH_MEMORY_USAGE', f'Memory usage at {latest_memory".1f"}%', 'WARNING')

            # API response time alert
            if self.metrics['api_response_time']:
                latest_response_time = self.metrics['api_response_time'][-1][1]
                if latest_response_time > 5000:  # 5 seconds
                    self.add_alert('SLOW_API_RESPONSE', f'API response time: {latest_response_time".1f"}ms', 'CRITICAL')

            # Cache hit rate alert
            if self.redis_client and self.metrics['redis_calculated_hit_rate']:
                latest_hit_rate = self.metrics['redis_calculated_hit_rate'][-1][1]
                if latest_hit_rate < 50:
                    self.add_alert('LOW_CACHE_HIT_RATE', f'Cache hit rate: {latest_hit_rate".1f"}%', 'WARNING')

            # Redis connection alert
            if self.redis_client:
                try:
                    self.redis_client.ping()
                except:
                    self.add_alert('REDIS_CONNECTION_LOST', 'Redis connection lost', 'CRITICAL')

        except Exception as e:
            self.log(f"Error checking alerts: {e}", "ERROR")

    def add_alert(self, alert_type: str, message: str, severity: str):
        """Add an alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }

        self.alerts.append(alert)
        self.log(f"🚨 ALERT [{severity}]: {message}")

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def _get_random_metric(self, min_val: float, max_val: float) -> float:
        """Generate random metric value for demonstration"""
        import random
        return min_val + random.random() * (max_val - min_val)

    def _parse_memory_usage(self, memory_str: str) -> float:
        """Parse memory usage string to MB"""
        try:
            if memory_str.endswith('M'):
                return float(memory_str[:-1])
            elif memory_str.endswith('G'):
                return float(memory_str[:-1]) * 1024
            elif memory_str.endswith('K'):
                return float(memory_str[:-1]) / 1024
            else:
                return float(memory_str) / (1024**2)
        except:
            return 0

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for display"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self._get_latest_metrics(['cpu_usage', 'memory_usage', 'disk_usage']),
            'service_metrics': self._get_latest_metrics(['api_response_time', 'redis_hit_rate']),
            'application_metrics': self._get_latest_metrics(['active_users', 'contributions_per_minute']),
            'cache_metrics': self._get_latest_metrics(['redis_connected_clients', 'redis_calculated_hit_rate']),
            'alerts': self.alerts[-10:],  # Last 10 alerts
            'summary': self._get_summary_stats()
        }

    def _get_latest_metrics(self, metric_names: List[str]) -> Dict[str, Any]:
        """Get latest values for specified metrics"""
        latest = {}
        for metric_name in metric_names:
            if self.metrics[metric_name]:
                latest[metric_name] = {
                    'value': self.metrics[metric_name][-1][1],
                    'timestamp': self.metrics[metric_name][-1][0].isoformat()
                }
        return latest

    def _get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        try:
            # Calculate averages
            summary = {}

            for metric_name, data_points in self.metrics.items():
                if data_points:
                    values = [point[1] for point in data_points]
                    summary[f'avg_{metric_name}'] = sum(values) / len(values)
                    summary[f'max_{metric_name}'] = max(values)
                    summary[f'min_{metric_name}'] = min(values)

            # Alert summary
            summary['total_alerts'] = len(self.alerts)
            summary['critical_alerts'] = len([a for a in self.alerts if a['severity'] == 'CRITICAL'])
            summary['warning_alerts'] = len([a for a in self.alerts if a['severity'] == 'WARNING'])

            # Performance score (0-100)
            score = 100
            if 'avg_cpu_usage' in summary and summary['avg_cpu_usage'] > 80:
                score -= 20
            if 'avg_memory_usage' in summary and summary['avg_memory_usage'] > 80:
                score -= 20
            if summary.get('critical_alerts', 0) > 0:
                score -= 30
            summary['performance_score'] = max(0, score)

            return summary

        except Exception as e:
            return {'error': str(e)}

    def save_performance_data(self):
        """Save performance data to file"""
        try:
            data = {
                'end_time': datetime.now().isoformat(),
                'duration': f"{(datetime.now() - self.start_time).total_seconds()".1f"}s",
                'metrics': dict(self.metrics),
                'alerts': self.alerts,
                'summary': self._get_summary_stats()
            }

            filename = f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            self.log(f"📊 Performance data saved to {filename}")

        except Exception as e:
            self.log(f"Error saving performance data: {e}", "ERROR")

    def log(self, message: str, level: str = "INFO"):
        """Log monitoring messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

class TerminalDashboard:
    """Terminal-based dashboard for real-time monitoring"""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    def run_dashboard(self):
        """Run terminal dashboard"""
        try:
            # Initialize curses
            stdscr = curses.initscr()
            curses.cbreak()
            curses.noecho()
            stdscr.keypad(True)
            stdscr.timeout(1000)  # 1 second timeout

            while True:
                stdscr.clear()
                self.draw_dashboard(stdscr)
                stdscr.refresh()

                # Check for key press
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('r') or key == ord('R'):
                    self.monitor.alerts.clear()

                time.sleep(2)  # Update every 2 seconds

        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    def draw_dashboard(self, stdscr):
        """Draw the dashboard"""
        height, width = stdscr.getmaxyx()

        # Title
        title = "🚀 NIMO PLATFORM - PERFORMANCE MONITORING DASHBOARD"
        stdscr.addstr(0, 0, title[:width-1])
        stdscr.addstr(1, 0, "=" * min(len(title), width-1))

        # System metrics
        y_pos = 3
        if y_pos < height - 10:
            stdscr.addstr(y_pos, 0, "📊 SYSTEM METRICS")
            stdscr.addstr(y_pos + 1, 0, "-" * 20)

            # Get latest metrics
            dashboard_data = self.monitor.get_dashboard_data()

            if 'system_metrics' in dashboard_data:
                metrics = dashboard_data['system_metrics']
                y_pos += 2

                for i, (metric_name, data) in enumerate(metrics.items()):
                    if y_pos + i < height - 5:
                        value = data.get('value', 0)
                        if metric_name == 'cpu_usage':
                            stdscr.addstr(y_pos + i, 0, f"CPU Usage:      {value".1f"}%")
                        elif metric_name == 'memory_usage':
                            stdscr.addstr(y_pos + i, 0, f"Memory Usage:   {value".1f"}%")
                        elif metric_name == 'disk_usage':
                            stdscr.addstr(y_pos + i, 0, f"Disk Usage:     {value".1f"}%")

        # Service status
        y_pos += len(dashboard_data.get('system_metrics', {})) + 2
        if y_pos < height - 10:
            stdscr.addstr(y_pos, 0, "🔧 SERVICE STATUS")
            stdscr.addstr(y_pos + 1, 0, "-" * 20)

            services = ['api', 'redis', 'ipfs', 'cardano']
            y_pos += 2

            for service in services:
                if y_pos < height - 5:
                    status = "✅" if dashboard_data.get('services', {}).get(service, {}).get('status') == 'healthy' else "❌"
                    stdscr.addstr(y_pos, 0, f"{service.upper()}: {status}")
                    y_pos += 1

        # Alerts
        y_pos += 2
        if y_pos < height - 5:
            stdscr.addstr(y_pos, 0, "🚨 RECENT ALERTS")
            stdscr.addstr(y_pos + 1, 0, "-" * 20)

            alerts = dashboard_data.get('alerts', [])
            y_pos += 2

            for i, alert in enumerate(alerts[-5:]):  # Show last 5 alerts
                if y_pos + i < height - 2:
                    severity = alert.get('severity', 'INFO')
                    message = alert.get('message', '')[:width-10]
                    stdscr.addstr(y_pos + i, 0, f"{severity[:3]}: {message}")

        # Controls
        stdscr.addstr(height-2, 0, "Controls: Q=Quit, R=Clear Alerts")
        stdscr.addstr(height-1, 0, f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Main monitoring execution"""
    print("📊 Nimo Platform - Real-time Performance Monitoring")
    print("=" * 55)

    # Check if backend is running
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not responding.")
            print("   Please start the backend first: cd backend && python app.py")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend server.")
        print("   Please ensure the backend is running on http://localhost:5000")
        return 1

    # Create monitor instance
    monitor = PerformanceMonitor()

    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor.start_monitoring, args=(5,))
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        # Run terminal dashboard
        dashboard = TerminalDashboard(monitor)
        dashboard.run_dashboard()

    except Exception as e:
        print(f"Error running dashboard: {e}")
        return 1

    finally:
        monitor.stop_monitoring()

    return 0

if __name__ == "__main__":
    exit(main())
