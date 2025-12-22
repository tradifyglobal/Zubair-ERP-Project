# Manual Deployment Instructions - TradifyERP New Servers

## Server Information

### App Server: 192.168.2.69
- User: zubair  
- Password: erp
- Sudo password: erp

### DB Server: 192.168.2.59
- User: zubair
- Password: sql  
- Sudo password: sql

---

## PHASE 1: Database Server Setup (192.168.2.59)

### Step 1: SSH to DB Server
```bash
ssh zubair@192.168.2.59
```

### Step 2: Update System and Install PostgreSQL
```bash
echo sql | sudo -S bash -c '
  apt-get update -y
  apt-get upgrade -y
  apt-get install -y postgresql postgresql-16 postgresql-contrib postgresql-client
  systemctl start postgresql
  systemctl enable postgresql
  systemctl status postgresql
'
```

### Step 3: Create Database and User
```bash
sudo -u postgres psql -c "
  CREATE DATABASE tradify ENCODING UTF8;
  CREATE USER zubair WITH PASSWORD '\''zubair@0862'\'';
  GRANT ALL PRIVILEGES ON DATABASE tradify TO zubair;
  ALTER USER zubair SUPERUSER CREATEDB;
"
```

### Step 4: Configure Remote Access
```bash
PG_VER=$(echo sql | sudo -S -u postgres psql --version | awk '{print $3}' | cut -d. -f1)
echo sql | sudo -S sed -i "s/#listen_addresses = '\''localhost'\''/listen_addresses = '\''*'\''/g" /etc/postgresql/${PG_VER}/main/postgresql.conf

echo sql | sudo -S bash -c "
  echo '' >> /etc/postgresql/${PG_VER}/main/pg_hba.conf
  echo 'host    tradify    zubair    192.168.2.69/32    md5' >> /etc/postgresql/${PG_VER}/main/pg_hba.conf  
  echo 'host    all        all       192.168.2.0/24     md5' >> /etc/postgresql/${PG_VER}/main/pg_hba.conf
  systemctl restart postgresql
"
```

### Step 5: Test Connection
```bash
psql -h 127.0.0.1 -U zubair -d tradify
```

---

## PHASE 2: Application Server Setup (192.168.2.69)

### Step 1: SSH to App Server
```bash
ssh zubair@192.168.2.69
```

### Step 2: Update System  
```bash
echo erp | sudo -S bash -c '
  apt-get update -y
  apt-get upgrade -y
'
```

### Step 3: Install Dependencies
```bash
echo erp | sudo -S bash -c '
  apt-get install -y python3.12 python3.12-venv python3.12-dev
  apt-get install -y python3-pip git curl wget nginx
  apt-get install -y build-essential libpq-dev postgresql-client
'
```

### Step 4: Create App Directory and Virtual Environment
```bash
echo erp | sudo -S mkdir -p /var/www/tradifyerp
echo erp | sudo -S chown zubair:zubair /var/www/tradifyerp

cd /var/www/tradifyerp
python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
```

### Step 5: Install Python Packages
```bash
source /var/www/tradifyerp/venv/bin/activate
pip install django==5.2.9
pip install gunicorn==23.0.0
pip install psycopg2-binary
pip install djangorestframework
pip install django-cors-headers
pip install pillow
```

### Step 6: Verify Installation
```bash
source /var/www/tradifyerp/venv/bin/activate
python -c "import django; print('Django', django.get_version())"
python -c "import psycopg2; print('psycopg2 OK')"
```

---

## PHASE 3: Deploy Application Code

From your local machine:

```bash
scp -r TradifyERP/ zubair@192.168.2.69:/var/www/tradifyerp/
```

---

## PHASE 4: Setup Django

### On App Server:
```bash
cd /var/www/tradifyerp
cp TradifyERP/settings_production.py TradifyERP/settings.py
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test Django
python manage.py check
python manage.py test --no-input 2>&1 | head -20
```

---

## PHASE 5: Configure Gunicorn and Nginx

### Configure Gunicorn
```bash
echo erp | sudo -S bash -c '
cat > /etc/systemd/system/gunicorn_tradifyerp.service << EOF
[Unit]
Description=Gunicorn instance for TradifyERP
After=network.target

[Service]
User=zubair
WorkingDirectory=/var/www/tradifyerp
ExecStart=/var/www/tradifyerp/venv/bin/gunicorn --workers=4 --bind unix:/var/www/tradifyerp/gunicorn.sock --timeout=120 TradifyERP.wsgi_production:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gunicorn_tradifyerp
systemctl start gunicorn_tradifyerp
systemctl status gunicorn_tradifyerp
'
```

### Configure Nginx
```bash
echo erp | sudo -S bash -c '
cp nginx_tradifyglobal_prod.conf /etc/nginx/sites-available/tradifyglobal_prod
ln -sf /etc/nginx/sites-available/tradifyglobal_prod /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
'
```

---

## PHASE 6: Import Production Data

```bash
cd /var/www/tradifyerp
source venv/bin/activate

# Load data from fixture
python manage.py loaddata prod_data_complete_backup.json

# Verify
python manage.py shell << EOF
from django.contrib.auth.models import User
print(f"Users: {User.objects.count()}")
EOF
```

---

## PHASE 7: Test End-to-End

1. Test Gunicorn:
```bash
curl -s http://127.0.0.1:8000/ | head -20
```

2. Test Nginx:
```bash
curl -s http://192.168.2.69/ | head -20
```

3. Test database connection:
```bash
psql -h 192.168.2.59 -U zubair -d tradify -c "SELECT count(*) FROM auth_user;"
```

4. Access via browser:
```
http://192.168.2.69/
```

---

## Troubleshooting

### PostgreSQL won't start
```bash
sudo systemctl status postgresql -l
sudo tail -50 /var/log/postgresql/postgresql-*.log
```

### Gunicorn won't start
```bash
systemctl status gunicorn_tradifyerp -l
journalctl -u gunicorn_tradifyerp -n 50
```

### Check logs
```bash
tail -f /var/log/tradifyerp/gunicorn_error.log
tail -f /var/log/nginx/error.log
```

---

## Quick Status Check Commands

```bash
# DB Server status
ssh zubair@192.168.2.59 'sudo systemctl status postgresql'

# App Server status  
ssh zubair@192.168.2.69 'sudo systemctl status gunicorn_tradifyerp'
ssh zubair@192.168.2.69 'sudo systemctl status nginx'

# Test connectivity
ssh zubair@192.168.2.69 'psql -h 192.168.2.59 -U zubair -d tradify -c "SELECT 1"'
```
