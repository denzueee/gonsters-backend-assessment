#!/usr/bin/env python3
"""
GONSTERS Continuous Data Simulator
Simulates realistic sensor data ingestion via REST API
Automatically fetches all machines and continuously sends data
"""

import time
import random
import json
import requests
from datetime import datetime
from typing import List, Dict


class DataSimulator:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
        self.machines = []
        self.gateway_id = f"gateway-{random.randint(1000, 9999)}"
        
    def login(self, username: str = "manager1", password: str = "Password123!"):
        """Login and get access token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                print(f"✅ Authenticated as {username}")
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def fetch_machines(self, limit: int = 1000):
        """Fetch all active machines from API"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/data/machines",
                headers=headers,
                params={"limit": limit},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.machines = data.get("machines", [])
                print(f"📊 Loaded {len(self.machines)} machine(s)")
                for m in self.machines:
                    print(f"   • {m['name']} ({m['sensor_type']}) @ {m['location']}")
                return True
            return False
        except Exception as e:
            print(f"⚠️  Failed to fetch machines: {e}")
            return False
    
    def generate_reading(self):
        """Generate single realistic sensor reading"""
        # Base values dengan variasi realistis
        base_temp = random.uniform(65, 75)
        base_pressure = random.uniform(98, 102)
        base_speed = random.uniform(1400, 1600)
        
        # Add random variation ±5%
        temperature = round(base_temp + random.uniform(-3, 3), 2)
        pressure = round(base_pressure + random.uniform(-2, 2), 2)
        speed = round(base_speed + random.uniform(-50, 50), 2)
        
        # Occasional anomalies (10% temperature spike, 5% pressure drop)
        if random.random() < 0.10:
            temperature += random.uniform(5, 15)
        if random.random() < 0.05:
            pressure -= random.uniform(5, 10)
        
        return {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "temperature": temperature,
            "pressure": pressure,
            "speed": speed
        }
    
    def ingest_data(self):
        """Send batch sensor data via /ingest endpoint"""
        if not self.machines:
            return False, 0
        
        # Build batch untuk semua machines
        batch = []
        for machine in self.machines:
            batch.append({
                "machine_id": machine["machine_id"],
                "sensor_type": machine["sensor_type"],
                "location": machine["location"],
                "readings": [self.generate_reading()]
            })
        
        payload = {
            "gateway_id": self.gateway_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "batch": batch
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/data/ingest",
                headers=headers,
                json=payload,
                timeout=5
            )
            
            if response.status_code in [201, 207]:
                result = response.json()
                summary = result.get("summary", {})
                total_readings = summary.get("total_readings", len(batch))
                return True, total_readings
            else:
                print(f"⚠️  Ingest failed: {response.status_code}")
                return False, 0
        except Exception as e:
            print(f"⚠️  Ingest error: {e}")
            return False, 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GONSTERS Data Simulator')
    parser.add_argument('--limit', type=int, default=1000, help='Limit number of machines to simulate')
    args = parser.parse_args()

    simulator = DataSimulator()
    
    # Step 1: Login
    print("\n🔐 Authenticating...")
    if not simulator.login():
        print("\n❌ Authentication failed. Please check credentials.")
        print("💡 Default: username='manager1', password='Manager123!'")
        return
    
    # Step 2: Fetch all machines
    print(f"\n📊 Fetching machines from database (Limit: {args.limit})...")
    if not simulator.fetch_machines(limit=args.limit) or not simulator.machines:
        print("\n⚠️  No machines found!")
        print("💡 Add machines first via API or dashboard")
        return
    
    # Step 3: Start continuous ingestion
    print(f"\n▶️  Starting continuous data ingestion")
    print(f"🔄 Interval: 3 seconds")
    print(f"🔗 Endpoint: POST /api/v1/data/ingest")
    print(f"🎯 Machines: {len(simulator.machines)}")
    print(f"🛑 Press Ctrl+C to stop\n")
    
    iteration = 0
    success_count = 0
    total_count = 0
    
    try:
        while True:
            iteration += 1
            total_count += 1
            timestamp = datetime.utcnow().strftime("%H:%M:%S")
            
            success, readings = simulator.ingest_data()
            
            if success:
                success_count += 1
                success_rate = (success_count / total_count) * 100
                
                # Detect potential anomaly
                anomaly_indicator = "🔴" if random.random() < 0.1 else "🟢"
                
                print(f"[{timestamp}] #{iteration:04d} {anomaly_indicator} "
                      f"INGEST | Machines: {len(simulator.machines)} | "
                      f"Readings: {readings} | Success: {success_rate:.0f}%")
            else:
                print(f"[{timestamp}] #{iteration:04d} ❌ INGEST | FAILED")
            
            # Refresh machine list periodically (every 50 iterations)
            if iteration % 50 == 0:
                print(f"\n🔄 Refreshing machine list...")
                simulator.fetch_machines(limit=args.limit)
                print()
            
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping simulator...")
        print(f"\n📊 Final Statistics:")
        print(f"   • Total iterations: {total_count}")
        print(f"   • Successful: {success_count}")
        print(f"   • Failed: {total_count - success_count}")
        print(f"   • Success rate: {(success_count/total_count)*100:.1f}%")
        print(f"   • Total readings: {success_count * len(simulator.machines)}")
        print("\n✅ Simulator stopped gracefully")
        print("=" * 70)


if __name__ == "__main__":
    main()
