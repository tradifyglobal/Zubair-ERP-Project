#!/usr/bin/env python3
"""
Employee Expense Module Deployment Script

This script automates the deployment of the Employee Expense module to production.
It handles:
1. Copying module files to production
2. Running database migrations
3. Restarting services
4. Verification checks

Usage:
    python deploy_expenses.py --server 192.168.2.185 --user root
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Tuple, Optional

class ExpenseModuleDeployment:
    """Handles deployment of expense module to production"""
    
    def __init__(self, server: str, user: str, password: Optional[str] = None):
        self.server = server
        self.user = user
        self.password = password
        self.app_path = "/var/www/tradifyerp/TradifyERP"
        self.local_base = Path(__file__).parent / "TradifyERP"
        
    def run_command(self, cmd: str, local: bool = True) -> Tuple[int, str]:
        """Execute command locally or remotely"""
        try:
            if local:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                # Build SSH command
                ssh_cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{self.server} \"{cmd}\""
                result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
            
            return result.returncode, result.stdout + result.stderr
        except Exception as e:
            return 1, f"Error executing command: {str(e)}"
    
    def copy_module_files(self) -> bool:
        """Copy expense module files to production"""
        print("📁 Copying module files to production...")
        
        local_expenses = self.local_base / "expenses"
        if not local_expenses.exists():
            print("❌ Local expenses module not found!")
            return False
        
        # Build SCP command
        cmd = f'scp -r "{local_expenses}" {self.user}@{self.server}:{self.app_path}/'
        
        print(f"   Running: {cmd}")
        returncode, output = self.run_command(cmd, local=True)
        
        if returncode != 0:
            print(f"❌ Failed to copy files: {output}")
            return False
        
        print("✅ Module files copied successfully")
        return True
    
    def copy_navigation_files(self) -> bool:
        """Copy updated navigation templates to production"""
        print("📄 Copying navigation templates to production...")
        
        templates_path = self.local_base / "templates" / "partials"
        nav_files = ["sidebar.html", "hori-sidebar.html"]
        
        for nav_file in nav_files:
            local_file = templates_path / nav_file
            if not local_file.exists():
                print(f"❌ Navigation file not found: {nav_file}")
                return False
            
            remote_path = f"{self.app_path}/templates/partials/"
            cmd = f'scp "{local_file}" {self.user}@{self.server}:{remote_path}'
            
            print(f"   Copying {nav_file}...")
            returncode, output = self.run_command(cmd, local=True)
            
            if returncode != 0:
                print(f"❌ Failed to copy {nav_file}: {output}")
                return False
        
        print("✅ Navigation templates copied successfully")
        return True
    
    def copy_config_files(self) -> bool:
        """Copy updated Django configuration files"""
        print("⚙️  Copying configuration files to production...")
        
        config_files = [
            "TradifyERP/settings.py",
            "TradifyERP/urls.py"
        ]
        
        for config_file in config_files:
            local_file = self.local_base / config_file
            if not local_file.exists():
                print(f"❌ Config file not found: {config_file}")
                return False
            
            remote_path = f"{self.app_path}/{config_file}"
            cmd = f'scp "{local_file}" {self.user}@{self.server}:{remote_path}'
            
            print(f"   Copying {config_file}...")
            returncode, output = self.run_command(cmd, local=True)
            
            if returncode != 0:
                print(f"❌ Failed to copy {config_file}: {output}")
                return False
        
        print("✅ Configuration files copied successfully")
        return True
    
    def run_migrations(self) -> bool:
        """Run database migrations on production server"""
        print("🗄️  Running database migrations...")
        
        cmd = f"cd {self.app_path} && python manage.py migrate expenses"
        
        print(f"   Running: {cmd}")
        returncode, output = self.run_command(cmd, local=False)
        
        if returncode != 0:
            print(f"⚠️  Migration output: {output}")
            if "already exists" in output.lower() or "no migrations to apply" in output.lower():
                print("ℹ️  Migrations already applied or no new migrations")
                return True
            return False
        
        print("✅ Database migrations completed")
        return True
    
    def verify_installation(self) -> bool:
        """Verify the module is installed correctly"""
        print("✓  Verifying installation...")
        
        checks = [
            (f"test -d {self.app_path}/expenses", "Module directory exists"),
            (f"grep -q 'expenses' {self.app_path}/TradifyERP/settings.py", "expenses in INSTALLED_APPS"),
            (f"grep -q 'expenses' {self.app_path}/TradifyERP/urls.py", "expenses in URL patterns"),
        ]
        
        for cmd, description in checks:
            returncode, _ = self.run_command(cmd, local=False)
            status = "✅" if returncode == 0 else "❌"
            print(f"   {status} {description}")
            
            if returncode != 0:
                return False
        
        print("✅ Installation verification passed")
        return True
    
    def restart_services(self) -> bool:
        """Restart Gunicorn service"""
        print("🔄 Restarting services...")
        
        cmd = "systemctl restart gunicorn"
        
        print(f"   Restarting Gunicorn...")
        returncode, output = self.run_command(cmd, local=False)
        
        if returncode != 0:
            print(f"❌ Failed to restart Gunicorn: {output}")
            return False
        
        print("✅ Services restarted successfully")
        return True
    
    def test_endpoints(self) -> bool:
        """Test that module endpoints are accessible"""
        print("🌐 Testing module endpoints...")
        
        endpoints = [
            "/expenses/",
            "/expenses/dashboard/",
        ]
        
        base_url = f"http://{self.server}"
        
        for endpoint in endpoints:
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {base_url}{endpoint}"
            returncode, output = self.run_command(cmd, local=False)
            
            # Check if response code is 200 or 301/302 (redirect)
            status_code = output.strip().split()[-1] if output else "000"
            is_ok = status_code.startswith(("200", "301", "302"))
            status = "✅" if is_ok else "❌"
            
            print(f"   {status} {endpoint} -> {status_code}")
            
            if not is_ok:
                return False
        
        print("✅ Endpoint tests passed")
        return True
    
    def deploy(self) -> bool:
        """Execute full deployment"""
        print("\n" + "="*60)
        print("🚀 Starting Employee Expense Module Deployment")
        print("="*60 + "\n")
        
        print(f"📍 Target Server: {self.server}")
        print(f"👤 User: {self.user}")
        print(f"📂 App Path: {self.app_path}\n")
        
        steps = [
            ("Copy Module Files", self.copy_module_files),
            ("Copy Navigation Templates", self.copy_navigation_files),
            ("Copy Configuration Files", self.copy_config_files),
            ("Verify Installation", self.verify_installation),
            ("Run Database Migrations", self.run_migrations),
            ("Restart Services", self.restart_services),
            ("Test Endpoints", self.test_endpoints),
        ]
        
        for step_name, step_func in steps:
            print(f"\n[{steps.index((step_name, step_func)) + 1}/{len(steps)}] {step_name}")
            print("-" * 60)
            
            try:
                if not step_func():
                    print(f"❌ Deployment failed at: {step_name}")
                    return False
            except Exception as e:
                print(f"❌ Error during {step_name}: {str(e)}")
                return False
        
        print("\n" + "="*60)
        print("✅ Deployment completed successfully!")
        print("="*60 + "\n")
        
        print("📋 Post-Deployment Tasks:")
        print("   1. Create expense categories in admin panel")
        print("   2. Configure GL account mappings")
        print("   3. Set up approval workflows")
        print("   4. Configure employee budgets")
        print("   5. Test with sample expense reports")
        print("\n")
        
        return True


def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(
        description="Deploy Employee Expense Module to production"
    )
    
    parser.add_argument(
        "--server",
        default="192.168.2.185",
        help="Production server IP or hostname (default: 192.168.2.185)"
    )
    
    parser.add_argument(
        "--user",
        default="root",
        help="SSH user for production server (default: root)"
    )
    
    parser.add_argument(
        "--password",
        default=None,
        help="SSH password (optional, uses key-based auth by default)"
    )
    
    args = parser.parse_args()
    
    # Create deployment instance
    deployment = ExpenseModuleDeployment(args.server, args.user, args.password)
    
    # Execute deployment
    success = deployment.deploy()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
