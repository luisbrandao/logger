#!/usr/bin/env python3
"""
Simple JSON Log Generator
Generates JSON logs for testing logging systems
"""

import json
import yaml
import time
import random
import sys
from datetime import datetime
from threading import Thread, Lock
from typing import Dict
from flask import Flask, jsonify


class LogGenerator:
    """Generates simple JSON logs"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the log generator with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.routes = self.config.get('routes', [])
        self.print_lock = Lock()  # Lock for thread-safe printing
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
    
    def _format_log_entry(self, endpoint: str, status_code: int) -> str:
        """Format a log entry as JSON"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "route": f"/{endpoint}",
            "code": status_code
        }
        
        return json.dumps(log_entry)
    
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
                
                # Generate and print the log (thread-safe)
                log_entry = self._format_log_entry(endpoint, status_code)
                with self.print_lock:
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
