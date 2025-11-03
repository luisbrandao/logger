#!/usr/bin/env python3
"""
Fake HTTP Log Generator
Simulates nginx access logs for testing scaling systems
"""

import yaml
import time
import random
import sys
from datetime import datetime
from threading import Thread
from typing import List, Dict
from flask import Flask, jsonify


class LogGenerator:
    """Generates fake nginx-style access logs"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the log generator with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.routes = self.config.get('routes', [])
        self.fake_ips = self._generate_fake_ips()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        ]
        self.app = self._setup_flask_app()
    
    def _setup_flask_app(self) -> Flask:
        """Setup Flask app with health endpoint"""
        app = Flask(__name__)
        
        @app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'routes': len(self.routes),
                'timestamp': datetime.now().isoformat()
            }), 200
        
        return app
    
    def _run_health_server(self):
        """Run Flask health check server"""
        print("Starting health check server on port 8080...", file=sys.stderr)
        self.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    
    def _generate_fake_ips(self) -> List[str]:
        """Generate a pool of fake IP addresses"""
        ips = []
        for _ in range(50):
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
            ips.append(ip)
        return ips
    
    def _format_nginx_log(self, endpoint: str, status_code: int) -> str:
        """Format a log entry to mimic nginx access log"""
        ip = random.choice(self.fake_ips)
        timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")
        if not timestamp.endswith('+0000'):
            timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
        
        method = "GET"
        path = f"/{endpoint}"
        protocol = "HTTP/1.1"
        bytes_sent = random.randint(200, 5000) if status_code == 200 else random.randint(150, 500)
        referer = "-"
        user_agent = random.choice(self.user_agents)
        response_time = round(random.uniform(0.001, 0.500), 3) if status_code == 200 else round(random.uniform(0.001, 2.0), 3)
        
        # Standard nginx log format
        log_entry = (
            f'{ip} - - [{timestamp}] '
            f'"{method} {path} {protocol}" '
            f'{status_code} {bytes_sent} '
            f'"{referer}" "{user_agent}"'
        )
        
        return log_entry
    
    def _generate_logs_for_route(self, route_config: Dict):
        """Generate logs for a specific route based on its configuration"""
        endpoint = route_config['endpoint']
        rate = route_config['rate']  # logs per second
        fail_percentage = route_config.get('fail', 0)  # percentage of 500 errors
        
        interval = 1.0 / rate  # time between each log in seconds
        
        print(f"Starting log generation for /{endpoint} at {rate} logs/sec with {fail_percentage}% failures", 
              file=sys.stderr)
        
        while True:
            try:
                # Determine if this request should fail
                status_code = 500 if random.random() * 100 < fail_percentage else 200
                
                # Generate and print the log
                log_entry = self._format_nginx_log(endpoint, status_code)
                print(log_entry, flush=True)
                
                # Wait for the next log entry
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error generating log for {endpoint}: {e}", file=sys.stderr)
                time.sleep(1)
    
    def start(self):
        """Start generating logs for all configured routes"""
        if not self.routes:
            print("No routes configured!", file=sys.stderr)
            sys.exit(1)
        
        print(f"Starting log generator with {len(self.routes)} routes...", file=sys.stderr)
        
        # Start health check server in a separate thread
        health_thread = Thread(target=self._run_health_server, daemon=True)
        health_thread.start()
        
        # Create a thread for each route
        threads = []
        for route in self.routes:
            thread = Thread(target=self._generate_logs_for_route, args=(route,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down log generator...", file=sys.stderr)
            sys.exit(0)


if __name__ == '__main__':
    generator = LogGenerator()
    generator.start()
