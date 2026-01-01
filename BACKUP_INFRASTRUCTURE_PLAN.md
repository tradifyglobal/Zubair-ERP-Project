# ERP System Backup & Replication Infrastructure Plan
**Date**: December 23, 2025  
**Status**: Design & Planning Phase

---

## 📋 Current Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRODUCTION ENVIRONMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  App Server (Primary)                 Database Server (Primary) │
│  192.168.20.10                        192.168.20.11             │
│  ├─ Nginx (port 80)                   ├─ PostgreSQL 16 (5432)  │
│  ├─ Gunicorn (port 8000)              ├─ Database: tradifyerp  │
│  └─ Django App                        └─ User: tradifyerp_user │
│                                                                   │
│  Network: 192.168.20.0/24 (production subnet)                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Proposed Backup Infrastructure

### **Option A: Full Redundancy (Recommended)**

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRODUCTION ENVIRONMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Primary App Server           Primary Database Server           │
│  192.168.20.10                192.168.20.11                     │
│  ├─ Nginx                     ├─ PostgreSQL Master              │
│  ├─ Gunicorn                  └─ (replication source)           │
│  └─ Django                                                       │
│                                                                   │
│         ↕  (Replication)                                        │
│                                                                   │
│  Backup App Server            Backup Database Server           │
│  192.168.20.20                192.168.20.21                     │
│  ├─ Nginx (Standby)           ├─ PostgreSQL Replica             │
│  ├─ Gunicorn (Standby)        └─ (read-only/failover)          │
│  └─ Django (Same Code)                                          │
│                                                                   │
│         ↑  (Load Balancer)                                      │
│                                                                   │
│  Load Balancer / Failover Controller                           │
│  192.168.20.30                                                   │
│  ├─ HAProxy or Keepalived     (automatic failover)             │
│  └─ Virtual IP: 192.168.20.50 (users access this)             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### **Option B: Minimal Backup (Cost-Effective)**

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRODUCTION ENVIRONMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Primary App Server           Primary Database Server           │
│  192.168.20.10                192.168.20.11                     │
│  ├─ Nginx                     ├─ PostgreSQL Master              │
│  ├─ Gunicorn                  └─ (replication source)           │
│  └─ Django                                                       │
│                                                                   │
│                                        ↓ (Replication)          │
│                                                                   │
│                              Backup Database Server             │
│                              192.168.20.21                      │
│                              ├─ PostgreSQL Replica               │
│                              └─ (read-only backup)              │
│                                                                   │
│  Note: App server not replicated, only database is backed up   │
│        App server can be restored from backup manually           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Comparison

| Feature | Option A (Full) | Option B (Minimal) |
|---------|-----------------|-------------------|
| **App Server Redundancy** | ✓ Yes | ✗ No |
| **Database Redundancy** | ✓ Yes | ✓ Yes |
| **Auto-Failover** | ✓ Yes | ~ Manual |
| **Zero Downtime Updates** | ✓ Yes | ✗ No |
| **Cost** | Higher (3 servers) | Lower (2 servers) |
| **Complexity** | Medium | Low |
| **Recovery Time** | <1 minute | 5-30 minutes |
| **Data Loss Risk** | Minimal | Minimal |
| **Recommended For** | Production/Enterprise | Small Business |

---

## 🔧 Recommended Setup: Option A (Full Redundancy)

### **Infrastructure Summary**

| Server | IP | Role | Services | Purpose |
|--------|-----|------|----------|---------|
| Primary App | 192.168.20.10 | Active | Nginx, Gunicorn, Django | Main application |
| Primary DB | 192.168.20.11 | Active | PostgreSQL Master | Primary database |
| Backup App | 192.168.20.20 | Standby | Nginx, Gunicorn, Django | Failover app |
| Backup DB | 192.168.20.21 | Standby | PostgreSQL Replica | Failover database |
| Load Balancer | 192.168.20.30 | Controller | HAProxy/Keepalived | Route traffic |
| **Virtual IP** | **192.168.20.50** | **Alias** | **N/A** | **Users access this** |

---

## 📈 How It Works

### **Normal Operation**
```
User Browser
    ↓
192.168.20.50 (Virtual IP)
    ↓
Load Balancer (192.168.20.30)
    ↓
Primary App Server (192.168.20.10) ← Active
    ↓
Primary Database (192.168.20.11) ← Master
```

### **If Primary App Server Fails**
```
Automatic Failover (within 10-30 seconds):

Backup App Server (192.168.20.20) ← Becomes Active
    ↓
Primary Database (192.168.20.11) ← Still Master
    ↓
[Traffic automatically routed to backup app]
```

### **If Primary Database Fails**
```
Automatic Failover (within 10-30 seconds):

Primary App Server (192.168.20.10) ← Still Active
    ↓
Backup Database (192.168.20.21) ← Promoted to Master
    ↓
[Database writes now go to backup server]
```

### **If Both Primary Servers Fail**
```
Automatic Failover (within 30-60 seconds):

Backup App Server (192.168.20.20) ← Active
    ↓
Backup Database (192.168.20.21) ← Master
    ↓
[Complete backup system handles all traffic]
```

---

## 🚀 Implementation Phases

### **Phase 1: Backup Server Provisioning** (Week 1)
- [ ] Provision Backup App Server (192.168.20.20)
- [ ] Provision Backup Database Server (192.168.20.21)
- [ ] Provision Load Balancer/Failover Controller (192.168.20.30)
- [ ] Configure network connectivity between all servers
- [ ] Verify SSH access and passwordless auth setup

### **Phase 2: Database Replication** (Week 1-2)
- [ ] Install PostgreSQL 16 on backup database server
- [ ] Configure streaming replication on primary
- [ ] Set up standby mode on backup database
- [ ] Verify replication is working
- [ ] Test failover and promotion of replica

### **Phase 3: App Server Replication** (Week 2)
- [ ] Install Nginx, Gunicorn, Python on backup app server
- [ ] Deploy Django application code
- [ ] Configure to connect to primary database
- [ ] Test app server connectivity
- [ ] Synchronize app code updates

### **Phase 4: Load Balancer Setup** (Week 2-3)
- [ ] Install HAProxy/Keepalived on load balancer
- [ ] Configure failover rules
- [ ] Set up virtual IP (192.168.20.50)
- [ ] Test failover scenarios
- [ ] Configure health checks

### **Phase 5: Testing & Validation** (Week 3)
- [ ] Full system failover tests
- [ ] Database failover tests
- [ ] App server failover tests
- [ ] Verify zero-data-loss
- [ ] Document runbooks

### **Phase 6: Production Ready** (Week 4)
- [ ] Update DNS/connection strings to use virtual IP
- [ ] Monitor all systems
- [ ] Train ops team
- [ ] Create emergency procedures

---

## 💾 Data Replication Strategy

### **PostgreSQL Streaming Replication (Recommended)**

**Characteristics:**
- Nearly synchronous replication (can be truly synchronous)
- Continuous WAL streaming from master to standby
- Standby is read-only until promoted
- Minimal data loss (RPO ~0)
- Fast failover capability
- Backup automatically updated

**Architecture:**
```
Primary Database (192.168.20.11)
    ├─ PostgreSQL Master
    ├─ Listens on port 5432
    ├─ Write-Ahead Logs (WAL) stream to replica
    └─ Replication user: repuser
         ↓ (TCP/5432)
Backup Database (192.168.20.21)
    ├─ PostgreSQL Standby (recovery.conf)
    ├─ Receives WAL stream
    ├─ Applies changes continuously
    └─ Can promote to master on demand
```

**Replication Settings:**
```postgresql
-- Primary Server (192.168.20.11)
max_wal_senders = 10              -- Allow 10 concurrent replicas
wal_level = replica               -- Enable WAL streaming
max_replication_slots = 10        -- Reserve replication slots
synchronous_commit = on           -- Wait for replica confirmation

-- Standby Server (192.168.20.21)
-- Uses recovery.conf or recovery.signal for configuration
```

---

## 🔄 App Server Replication Strategy

### **Code Synchronization**

**Method 1: Git-based (Recommended)**
```
Primary App (192.168.20.10)
    ├─ /var/www/tradifyerp/
    ├─ Git repository with production code
    └─ On code push → webhook triggers backup sync
         ↓
Backup App (192.168.20.20)
    ├─ /var/www/tradifyerp/
    ├─ Git repository (pulls latest from GitHub)
    └─ Auto-synced via cron or webhook
```

**Method 2: Direct Sync (Rsync)**
```
Primary App → Backup App
Every 5 minutes via cron:
  rsync -avz --delete /var/www/tradifyerp/ backup-app:/var/www/tradifyerp/
```

**Method 3: Shared Storage (NFS)**
```
Primary App ─┐
             ├─ NFS Share (192.168.20.40:/exports/tradifyerp/)
Backup App ──┘

Both servers mount the same code directory
```

---

## 🔐 Security Considerations

### **Network Security**
- Backup servers on same subnet as primary (192.168.20.0/24)
- Internal replication traffic uses dedicated network
- SSH key-based authentication for all server access
- Firewall rules to restrict database replication port (5432)

### **Database Security**
- Separate replication user (not superuser)
- Replication connection requires SSL/TLS (optional but recommended)
- Backup database read-only until promotion
- Regular backup encryption

### **Application Security**
- Same environment variables/secrets on both servers
- Database connection string same on both
- Application code identical between servers
- Secrets stored in environment files (not in code)

---

## 📊 Network Architecture Details

### **Current Network**
```
192.168.20.0/24 subnet
├─ 192.168.20.10   - Primary App Server
├─ 192.168.20.11   - Primary Database Server
└─ (20-30 available for backup servers)
```

### **Proposed Network**
```
192.168.20.0/24 subnet
├─ 192.168.20.10   - Primary App Server
├─ 192.168.20.11   - Primary Database Server
├─ 192.168.20.20   - Backup App Server
├─ 192.168.20.21   - Backup Database Server
├─ 192.168.20.30   - Load Balancer / Failover Controller
└─ 192.168.20.50   - Virtual IP (for automatic failover)
```

### **Network Requirements**
- All servers must be reachable on port 22 (SSH)
- Database replication port: 5432 (master → backup)
- Load balancer port: 3306 (proxy frontend)
- Inter-server communication: unrestricted

---

## 📋 Pre-Implementation Checklist

Before setting up backup servers, you need:

### **Hardware/Infrastructure**
- [ ] 2 new servers provisioned (same specs as primary servers)
- [ ] Network connectivity to existing servers
- [ ] IPs assigned: 192.168.20.20, 192.168.20.21, 192.168.20.30
- [ ] Virtual IP available: 192.168.20.50

### **Software Requirements**
- [ ] Ubuntu 22.04 LTS or same OS as primary servers
- [ ] PostgreSQL 16 (same version)
- [ ] Python 3.12 (same version)
- [ ] Nginx and Gunicorn (same versions)

### **Access & Credentials**
- [ ] SSH keys generated and distributed
- [ ] Passwordless sudo configured
- [ ] GitHub access for code sync
- [ ] Database credentials secured

### **Documentation & Planning**
- [ ] Network diagram finalized
- [ ] IP scheme approved
- [ ] Replication method chosen
- [ ] Failover procedures documented
- [ ] Monitoring strategy defined

---

## ⚠️ Important Considerations

### **Complexity**
- Full redundancy adds operational complexity
- More servers to monitor and maintain
- Failover testing must be regular
- Training required for ops team

### **Cost**
- Additional hardware/VMs required
- More bandwidth for replication
- Load balancer/failover controller needed
- Higher overall infrastructure cost

### **Data Consistency**
- Replication lag (usually milliseconds)
- During failover, some in-flight transactions may be lost
- Configure synchronous replication for zero-loss
- Test failover procedures regularly

### **Monitoring & Alerting**
- Must monitor replication lag
- Must detect server failures quickly
- Must alert ops team of issues
- Must track system health continuously

---

## 🎯 Next Steps

1. **Decide**: Option A (Full) or Option B (Minimal)?
2. **Provision**: Get 2-3 new servers
3. **Network**: Configure IPs and connectivity
4. **Database**: Set up PostgreSQL replication
5. **Application**: Deploy backup app server
6. **Load Balancer**: Set up failover mechanism
7. **Test**: Verify all failover scenarios
8. **Deploy**: Update DNS/connection strings
9. **Monitor**: Set up continuous monitoring
10. **Train**: Ops team training

---

## 📞 Contact Points

For more information on each component:
- **PostgreSQL Replication**: PostgreSQL documentation (https://www.postgresql.org/docs/)
- **HAProxy Load Balancer**: HAProxy documentation (https://www.haproxy.com/)
- **Keepalived Failover**: Keepalived documentation (https://www.keepalived.org/)
- **Nginx/Gunicorn**: Django deployment guides

---

*Configuration & Planning Document*  
*Prepared for: Zubair ERP System*  
*Date: December 23, 2025*
