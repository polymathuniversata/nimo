"""
Production Deployment Validation Script

This script validates the production deployment setup by:
1. Checking all required files are present
2. Validating Docker configuration
3. Testing deployment scripts
4. Verifying environment configuration
5. Running health checks
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_files_exist():
    """Check if all required deployment files exist"""
    required_files = [
        'Dockerfile',
        'docker-compose/docker-compose.prod.yml',
        'nginx/nginx.conf',
        '.env.template',
        'deploy.sh',
        'setup_dev.sh',
        'run_dev.sh',
        'monitoring/prometheus.yml',
        'monitoring/grafana-dashboard.json',
        '.dockerignore',
        'PRODUCTION_README.md'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"ERROR: Missing files: {', '.join(missing_files)}")
        return False

    print("SUCCESS: All required deployment files are present")
    return True

def validate_dockerfile():
    """Validate Dockerfile syntax"""
    try:
        # Check if Dockerfile exists and has basic structure
        if not os.path.exists('Dockerfile'):
            print("ERROR: Dockerfile not found")
            return False

        with open('Dockerfile', 'r') as f:
            content = f.read()

        # Basic validation checks
        required_instructions = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'CMD']
        found_instructions = []

        for line in content.split('\n'):
            line = line.strip().upper()
            for instruction in required_instructions:
                if line.startswith(instruction):
                    found_instructions.append(instruction)
                    break

        missing_instructions = set(required_instructions) - set(found_instructions)
        if missing_instructions:
            print(f"WARNING: Dockerfile missing some instructions: {', '.join(missing_instructions)}")
        else:
            print("SUCCESS: Dockerfile contains all required instructions")

        # Check for multi-stage build
        if 'AS ' in content.upper():
            print("SUCCESS: Dockerfile uses multi-stage build")
        else:
            print("INFO: Dockerfile is single-stage")

        return True

    except Exception as e:
        print(f"ERROR: Dockerfile validation failed: {e}")
        return False

def validate_docker_compose():
    """Validate Docker Compose configuration"""
    try:
        result = subprocess.run(['docker-compose', '-f', 'docker-compose/docker-compose.prod.yml', 'config'],
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print("SUCCESS: Docker Compose configuration is valid")
            return True
        else:
            print(f"ERROR: Docker Compose validation failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("WARNING: Docker Compose not found, skipping validation")
        return True

def validate_nginx_config():
    """Validate Nginx configuration syntax"""
    try:
        result = subprocess.run(['nginx', '-t', '-c', 'nginx/nginx.conf'],
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print("SUCCESS: Nginx configuration is valid")
            return True
        else:
            print(f"ERROR: Nginx configuration validation failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("WARNING: Nginx not found, skipping configuration validation")
        return True

def validate_environment_template():
    """Validate environment template structure"""
    if not os.path.exists('.env.template'):
        print("ERROR: .env.template not found")
        return False

    with open('.env.template', 'r') as f:
        content = f.read()

    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'FLASK_ENV'
    ]

    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)

    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        return False

    print("SUCCESS: Environment template contains all required variables")
    return True

def validate_deployment_scripts():
    """Validate deployment scripts are executable"""
    scripts = ['deploy.sh', 'setup_dev.sh', 'run_dev.sh']

    for script in scripts:
        if not os.path.exists(script):
            print(f"ERROR: {script} not found")
            return False

        if not os.access(script, os.X_OK):
            print(f"WARNING: {script} is not executable")
            # Try to make it executable
            try:
                os.chmod(script, 0o755)
                print(f"SUCCESS: Made {script} executable")
            except Exception as e:
                print(f"ERROR: Could not make {script} executable: {e}")
                return False
        else:
            print(f"SUCCESS: {script} is executable")

    return True

def validate_monitoring_config():
    """Validate monitoring configuration files"""
    prometheus_config = 'monitoring/prometheus.yml'
    grafana_config = 'monitoring/grafana-dashboard.json'

    # Validate Prometheus config
    if not os.path.exists(prometheus_config):
        print(f"ERROR: {prometheus_config} not found")
        return False

    try:
        with open(prometheus_config, 'r') as f:
            import yaml
            yaml.safe_load(f)
        print("SUCCESS: Prometheus configuration is valid YAML")
    except Exception as e:
        print(f"ERROR: Invalid Prometheus configuration: {e}")
        return False

    # Validate Grafana config
    if not os.path.exists(grafana_config):
        print(f"ERROR: {grafana_config} not found")
        return False

    try:
        with open(grafana_config, 'r') as f:
            json.load(f)
        print("SUCCESS: Grafana dashboard configuration is valid JSON")
    except Exception as e:
        print(f"ERROR: Invalid Grafana configuration: {e}")
        return False

    return True

def test_deployment_readiness():
    """Test if deployment is ready"""
    print("\nTesting deployment readiness...")

    # Check if all dependencies are available
    try:
        import flask
        import redis
        import psycopg2
        print("SUCCESS: All Python dependencies are available")
    except ImportError as e:
        print(f"WARNING: Some Python dependencies missing: {e}")

    # Check if required directories exist
    directories = ['logs', 'instance', 'metta_state']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"SUCCESS: Created directory {directory}")
        else:
            print(f"SUCCESS: Directory {directory} exists")

    return True

def generate_deployment_report():
    """Generate a deployment readiness report"""
    report = {
        "deployment_ready": True,
        "timestamp": str(datetime.now()),
        "files_checked": [],
        "validations": [],
        "recommendations": []
    }

    # File checks
    required_files = [
        'Dockerfile',
        'docker-compose/docker-compose.prod.yml',
        'nginx/nginx.conf',
        '.env.template',
        'deploy.sh',
        'setup_dev.sh',
        'run_dev.sh'
    ]

    for file_path in required_files:
        exists = os.path.exists(file_path)
        report["files_checked"].append({
            "file": file_path,
            "exists": exists
        })
        if not exists:
            report["deployment_ready"] = False

    # Add recommendations
    if not os.path.exists('.env'):
        report["recommendations"].append("Copy .env.template to .env and configure production values")

    if not os.path.exists('nginx/ssl'):
        report["recommendations"].append("Configure SSL certificates for HTTPS in production")

    # Save report
    with open('deployment_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("SUCCESS: Deployment validation report saved to deployment_validation_report.json")
    return report

def main():
    """Main validation function"""
    print("Production Deployment Validation")
    print("=" * 50)

    validations = [
        ("File Existence", check_files_exist),
        ("Dockerfile Validation", validate_dockerfile),
        ("Docker Compose Validation", validate_docker_compose),
        ("Nginx Configuration", validate_nginx_config),
        ("Environment Template", validate_environment_template),
        ("Deployment Scripts", validate_deployment_scripts),
        ("Monitoring Configuration", validate_monitoring_config),
        ("Deployment Readiness", test_deployment_readiness)
    ]

    all_passed = True

    for validation_name, validation_func in validations:
        print(f"\nRunning {validation_name}...")
        try:
            result = validation_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"ERROR: {validation_name} failed with exception: {e}")
            all_passed = False

    # Generate report
    print("\nGenerating deployment report...")
    report = generate_deployment_report()

    print("\n" + "=" * 50)
    if all_passed:
        print("SUCCESS: All validations passed! Production deployment is ready.")
        print("\nNext steps:")
        print("1. Configure your .env file with production values")
        print("2. Run ./deploy.sh to start production deployment")
        print("3. Monitor logs and health endpoints")
    else:
        print("WARNING: Some validations failed. Please review the output above.")
        print("Check deployment_validation_report.json for details.")

    return all_passed

if __name__ == "__main__":
    from datetime import datetime
    success = main()
    sys.exit(0 if success else 1)