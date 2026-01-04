# ERP Security Implementation Checklist & Guide

## 1. IMMEDIATE ACTIONS (CRITICAL)

### A. Environment Variables Setup
```bash
# Create .env file (NEVER commit to git)
DJANGO_SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ENCRYPTION_KEY=<base64-encoded-encryption-key>
DB_PASSWORD=<strong-postgres-password>
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Generate strong secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### B. Update Django Settings
1. Copy `SECURITY_SETTINGS_TEMPLATE.py` settings to your `settings.py`
2. Set `DEBUG = False` in production
3. Configure environment variables
4. Enable HTTPS and SSL

### C. Install Security Packages
```bash
pip install django-cors-headers
pip install django-ratelimit
pip install cryptography
pip install django-redis
pip install psycopg2-binary
```

### D. Update INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_extensions',
    'rest_framework',
    'corsheaders',
    # Add audit logging
    # 'TradifyERP.audit_models',  # Create app for this
]
```

### E. Update MIDDLEWARE
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'TradifyERP.security_middleware.SecurityHeadersMiddleware',
    'TradifyERP.security_middleware.RateLimitMiddleware',
    'TradifyERP.security_middleware.AuditLoggingMiddleware',
    'TradifyERP.security_middleware.SQLInjectionProtectionMiddleware',
    # ... rest of middleware
]
```

---

## 2. DATABASE SECURITY

### A. PostgreSQL Configuration
```sql
-- Create dedicated database user with limited permissions
CREATE ROLE tradifyerp_user WITH LOGIN PASSWORD 'strong_random_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE tradifyerp_db TO tradifyerp_user;
GRANT USAGE ON SCHEMA public TO tradifyerp_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tradifyerp_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO tradifyerp_user;

-- Enable SSL connection
-- In postgresql.conf: ssl = on
-- Generate SSL certificate for database server
```

### B. Regular Backups
```bash
# Automated daily backup to S3
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
pg_dump tradifyerp_db | gzip > backups/tradifyerp_$TIMESTAMP.sql.gz

# Upload to S3
aws s3 cp backups/tradifyerp_$TIMESTAMP.sql.gz s3://my-backups/erp/

# Test restore regularly
pg_restore -d test_db backups/tradifyerp_latest.sql.gz
```

### C. Database Encryption
```python
# In your model for sensitive data:
from TradifyERP.encryption import DataEncryption, EncryptedField

encryptor = DataEncryption()

# Encrypt customer data
customer.phone = encryptor.encrypt(phone_number)
customer.ssn = encryptor.encrypt(ssn)
customer.save()

# Decrypt when needed
decrypted_phone = encryptor.decrypt(customer.phone)
```

---

## 3. ACCESS CONTROL & AUTHENTICATION

### A. User Permissions
```python
# In Django admin or programmatically
from django.contrib.auth.models import Permission, Group

# Create roles
customer_support_group = Group.objects.create(name='Customer Support')
accounting_group = Group.objects.create(name='Accounting')
admin_group = Group.objects.create(name='Administrators')

# Assign permissions to groups
customer_support_perms = Permission.objects.filter(
    codename__in=['view_customer', 'view_invoice']
)
customer_support_group.permissions.set(customer_support_perms)

# Add user to group
user.groups.add(customer_support_group)
```

### B. Two-Factor Authentication
```bash
pip install django-otp qrcode pillow

# In settings.py
INSTALLED_APPS += ['django_otp', 'django_otp.plugins.otp_totp']

MIDDLEWARE += ['django_otp.middleware.OTPMiddleware']

# Protect admin
from django_otp.admin import OTPAdminSite
admin.site.__class__ = OTPAdminSite
```

### C. Password Policy
```python
# In settings.py
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Force password change
MAX_LOGIN_ATTEMPTS = 5
PASSWORD_EXPIRY_DAYS = 90
```

---

## 4. DATA PROTECTION & COMPLIANCE

### A. GDPR Compliance
```python
# Add to User model
from django.db import models

class UserConsent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_processing = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Consent: {self.consent_date}"

# Right to be forgotten
def delete_user_data(user_id):
    """Securely delete all user personal data"""
    user = User.objects.get(id=user_id)
    # Anonymize or delete sensitive data
    user.email = f"deleted_user_{user.id}@deleted.local"
    user.save()
```

### B. Data Masking for Display
```python
from TradifyERP.encryption import FieldEncryption

# Mask sensitive data in lists/exports
class CustomerListView(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for customer in context['customers']:
            customer.phone = FieldEncryption.mask_sensitive_field(customer.phone)
            customer.ssn = FieldEncryption.mask_sensitive_field(customer.ssn)
        return context
```

### C. Data Classification
```python
"""
CONFIDENTIAL (Level 4) - Highest Security
- Customer financial data
- Passwords, API keys
- Payment information
- PHI/PII

RESTRICTED (Level 3)
- Customer contact information
- Invoice data
- Employee records

INTERNAL (Level 2)
- Internal processes
- Non-sensitive business data

PUBLIC (Level 1)
- Marketing materials
- Public documentation
"""
```

---

## 5. AUDIT LOGGING

### A. Enable Audit Logging
```python
# In views
from TradifyERP.audit_models import AuditLog, DataAccessLog

def customer_detail_view(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    
    # Log access to sensitive data
    DataAccessLog.log_access(
        user=request.user,
        data_type='Customer',
        object_id=customer_id,
        action='view',
        ip_address=get_client_ip(request),
        reason='Customer inquiry'
    )
    
    return render(request, 'customer_detail.html', {'customer': customer})

def update_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    old_values = model_to_dict(customer)
    
    # Update customer
    customer.name = request.POST['name']
    customer.save()
    
    new_values = model_to_dict(customer)
    
    # Log change
    AuditLog.log_action(
        user=request.user,
        action='UPDATE',
        model_name='Customer',
        object_id=customer_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=get_client_ip(request)
    )
```

### B. Review Audit Logs
```python
# Django shell
from TradifyERP.audit_models import AuditLog

# Who accessed a customer?
logs = AuditLog.objects.filter(model_name='Customer', object_id=123)

# Failed login attempts
failed_logins = AuditLog.objects.filter(
    action='FAILED_LOGIN',
    success=False
)

# Export audit trail
logs.values().to_csv('audit_report.csv')
```

---

## 6. NETWORK SECURITY

### A. Nginx Configuration
```nginx
# /etc/nginx/sites-available/tradifyerp

server {
    listen 443 ssl http2;
    server_name tradifyglobal.com www.tradifyglobal.com;
    
    # SSL Certificate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tradifyglobal.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tradifyglobal.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name tradifyglobal.com www.tradifyglobal.com;
    return 301 https://$server_name$request_uri;
}
```

### B. Firewall Rules (UFW)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (change port from 22 if possible)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block everything else
sudo ufw default deny incoming

# Rate limit SSH
sudo ufw limit 22/tcp
```

---

## 7. MONITORING & ALERTING

### A. Security Monitoring
```python
# Dashboard view for security alerts
from TradifyERP.audit_models import SecurityEvent

def security_dashboard(request):
    recent_alerts = SecurityEvent.objects.filter(
        resolved=False,
        severity__gte=3
    ).order_by('-timestamp')[:10]
    
    return render(request, 'security_dashboard.html', {
        'alerts': recent_alerts
    })
```

### B. Automated Alerts
```python
# Send email on critical events
from django.core.mail import send_mail

if event.severity >= 3:
    send_mail(
        f"[SECURITY ALERT] {event.event_type}",
        f"Critical security event detected:\n{event.description}",
        'security@tradifyglobal.com',
        ['admin@tradifyglobal.com']
    )
```

### C. Log Monitoring Tools
```bash
# Install ELK Stack or similar
docker run -d --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:8.0.0
docker run -d --name kibana docker.elastic.co/kibana/kibana:8.0.0

# Forward Django logs to ELK
# Configure in logging.py to send to Elasticsearch
```

---

## 8. INFRASTRUCTURE SECURITY

### A. Server Hardening
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban

# Disable root login
sudo sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# SSH Key authentication only
sudo sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart ssh
```

### B. Regular Security Audits
```bash
# Run Django security check
python manage.py check --deploy

# Scan dependencies for vulnerabilities
pip install safety
safety check

# Run static security analysis
pip install bandit
bandit -r TradifyERP/
```

---

## 9. INCIDENT RESPONSE PLAN

### A. Breach Notification Procedure
1. **Detect** → Security team identifies breach
2. **Contain** → Isolate affected systems
3. **Investigate** → Determine scope and impact
4. **Notify** → Inform affected users within 72 hours (GDPR)
5. **Restore** → Recover from backups
6. **Document** → Record everything for audit

### B. Emergency Contacts
```python
SECURITY_CONTACTS = {
    'CTO': 'cto@tradifyglobal.com',
    'Security_Team': 'security@tradifyglobal.com',
    'Legal': 'legal@tradifyglobal.com',
    'Public_Relations': 'pr@tradifyglobal.com',
}
```

---

## 10. ONGOING MAINTENANCE

### Weekly
- Review security logs
- Check failed login attempts
- Monitor for suspicious activity

### Monthly
- Update dependencies (`pip list --outdated`)
- Review access logs
- Test disaster recovery
- Update security policies

### Quarterly
- Penetration testing
- Security training for staff
- Audit user permissions
- Review and update incident response plan

### Annually
- Full security audit
- Compliance certification
- Update security documentation
- Review all security controls

---

## DEPLOYMENT CHECKLIST

- [ ] DEBUG = False
- [ ] SECRET_KEY from environment variable
- [ ] HTTPS enabled (SSL certificate)
- [ ] Database SSL connection required
- [ ] Strong database password
- [ ] Encryption key generated
- [ ] Security middleware installed
- [ ] Audit logging enabled
- [ ] Backups automated
- [ ] Monitoring/alerting configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Password policy enforced
- [ ] Two-factor authentication enabled
- [ ] Access control configured
- [ ] Firewall configured
- [ ] SSH hardened
- [ ] Security team trained
- [ ] Incident response plan documented
- [ ] GDPR compliance confirmed

---

## REFERENCES

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/cis-controls/)
- [GDPR Compliance Guide](https://gdpr-info.eu/)
