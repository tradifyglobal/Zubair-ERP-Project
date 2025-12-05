# User Journey: Auto-Login & Notifications

## Scenario: Safi User Logging In

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN SCREEN                            │
│                    Username: Safi                               │
│                    Password: ****                               │
│                                                                 │
│                    [LOGIN BUTTON]                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                         ✓ Authenticated
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              account_adapter.get_login_redirect_url()           │
│                                                                 │
│  1. Check if user is authenticated ✓                           │
│  2. Query UserEntity.objects.filter(                           │
│       user=safi,                                               │
│       is_default=True,                                         │
│       entity__is_active=True                                   │
│     ).first()                                                  │
│  3. Found: INT-005 (Internal) entity ✓                         │
│  4. Set session:                                               │
│     - selected_entity_id = 5                                   │
│     - selected_entity_code = "INT-005"                         │
│     - selected_entity_name = "Internal"                        │
│  5. Return: /dashboard/ ✓                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                   ✓ SKIP Entity Selection Page
                   ✓ Auto-Login to INT-005
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD PAGE LOADS                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ HEADER BAR                                              │  │
│  │  [LOGO] [MENU] [SEARCH] [SETTINGS] [ENTITY: INT-005]   │  │
│  │                                      [BELL] [USER: Safi]│  │
│  │                                       ∨ Red(2)          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  JavaScript triggers on page load:                            │
│  1. Call: fetch('/shareholder/api/notifications/')            │
│  2. Response: { total_pending: 2, ... }                       │
│  3. Update bell badge: "2" (shown in red)                     │
│  4. Check: total_pending > 0 ? Show Modal                     │
│  5. Initialize Bootstrap Modal                               │
│  6. Call: displayNotificationsModal(data)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         NOTIFICATION MODAL APPEARS (Bootstrap Fade-In)          │
│                                                                 │
│  ╔═════════════════════════════════════════════════════════╗   │
│  ║ 🔔 Pending Actions Required                        [×] ║   │
│  ╠═════════════════════════════════════════════════════════╣   │
│  ║                                                         ║   │
│  ║ ⚠️ AWAITING YOUR REVIEW (1)                           ║   │
│  ║ ┌─────────────────────────────────────────────────┐   ║   │
│  ║ │ Imteyazuddin Sameer Mohammed    [REVIEW BADGE] │   ║   │
│  ║ │ Amount: 100,000.00 INR                          │   ║   │
│  ║ │ Click to review this contribution               │   ║   │
│  ║ │ ↪ Links to: /shareholder/capital-contributions/3/│  ║   │
│  ║ └─────────────────────────────────────────────────┘   ║   │
│  ║                                                         ║   │
│  ║ ✓ AWAITING YOUR APPROVAL (1)                          ║   │
│  ║ ┌─────────────────────────────────────────────────┐   ║   │
│  ║ │ Johnmac macjohn                 [APPROVE BADGE]│   ║   │
│  ║ │ Amount: 50,000.00 INR                           │   ║   │
│  ║ │ Click to approve this contribution              │   ║   │
│  ║ │ ↪ Links to: /shareholder/capital-contributions/4/│  ║   │
│  ║ └─────────────────────────────────────────────────┘   ║   │
│  ║                                                         ║   │
│  ║                [Dismiss]  [View All Contributions]     ║   │
│  ╚═════════════════════════════════════════════════════════╝   │
│                                                                 │
│  Updates performed:                                            │
│  ✓ Bell badge text = "2"                                       │
│  ✓ Bell badge display = "block"                               │
│  ✓ Modal title updated with count                             │
│  ✓ Review items populated from API                            │
│  ✓ Approval items populated from API                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  User can take action:
```

## Action Path 1: Click Review Item

```
┌─────────────────────────────────────────────────────────────────┐
│  User clicks: "Imteyazuddin Sameer Mohammed"                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     Modal closes (Bootstrap modal fade-out)                    │
│     Redirects to:                                              │
│     /shareholder/capital-contributions/3/review/              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         CAPITAL CONTRIBUTION REVIEW PAGE LOADS                 │
│                                                                 │
│  Shows:                                                        │
│  - Contribution details (ID 3)                               │
│  - Stakeholder: Imteyazuddin                                 │
│  - Amount: 100,000 INR                                       │
│  - Status: SUBMITTED → can review                            │
│  - Files attached (documents)                                │
│  - Review form with:                                         │
│    * Notes textarea                                          │
│    * Approve / Reject buttons                                │
│                                                              │
│  [Review & Approve] or [Review & Reject]                    │
└─────────────────────────────────────────────────────────────────┘
```

## Action Path 2: Check Bell Icon Dropdown

```
┌─────────────────────────────────────────────────────────────────┐
│  At any time, user can click bell icon in header              │
│                                                                 │
│  Header before: [BELL with "2" badge] ← red circle            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          BELL ICON DROPDOWN OPENS (Bootstrap Dropdown)         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Awaiting Action                               2 pending │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                          │  │
│  │ AWAITING REVIEW (1)                                    │  │
│  │                                                          │  │
│  │ [⚠️] Imteyazuddin Sameer Mohammed                      │  │
│  │     Amount: 100,000.00 INR                            │  │
│  │     ↪ Click to review                                 │  │
│  │                                                          │  │
│  │ AWAITING APPROVAL (1)                                  │  │
│  │                                                          │  │
│  │ [✓] Johnmac macjohn                                    │  │
│  │     Amount: 50,000.00 INR                             │  │
│  │     ↪ Click to approve                                │  │
│  │                                                          │  │
│  │ [View All Contributions]                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## System Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       LOGIN SUCCESS                          │
└──────────────────────────────────────────────────────────────┘
                          ↓
                ┌─────────────────────┐
                │ account_adapter.py  │
                │ get_login_redirect  │
                └─────────────────────┘
                          ↓
              Query UserEntity.is_default
                          ↓
        ┌─────────────────────────────────┐
        ↓                                 ↓
    Found Default           No Default Entity
        ↓                                 ↓
   Set Session         EntitySelectionView
   Auto-redirect       Show Selection Page
   to /dashboard/      User picks entity
        ↓                                 ↓
        └─────────────────────────────────┘
                          ↓
        ┌──────────────────────────────┐
        │  Dashboard Page Loads        │
        │  SessionEntityMixin applies  │
        │  - Validates entity         │
        │  - Sets request.entity      │
        │  - Adds to context          │
        └──────────────────────────────┘
                          ↓
        ┌──────────────────────────────┐
        │ pending_notifications_modal  │
        │ JavaScript executes:         │
        │ 1. Wait for DOM ready       │
        │ 2. Fetch /api/notifications│
        │ 3. Update bell badge        │
        │ 4. Show modal if pending>0  │
        │ 5. Populate items           │
        └──────────────────────────────┘
                          ↓
        ┌──────────────────────────────┐
        │ User sees:                   │
        │ ✓ Dashboard with entity      │
        │ ✓ Notification modal popup   │
        │ ✓ Bell badge (red) "2"      │
        │ ✓ Ready to take action      │
        └──────────────────────────────┘
```

## Key Components

### 1. Session Entity Setup
```
Request Flow:
  Login → account_adapter → UserEntity.objects → Set Session → Dashboard
```

### 2. Notification Fetch
```
JavaScript Flow:
  DOMContentLoaded → fetch API → Receive JSON → Update UI → Show Modal
```

### 3. Bell Badge Update
```
Data Flow:
  API Response: { total_pending: 2 }
    ↓
  JavaScript processes
    ↓
  Badge element: <span id="notification-badge">2</span>
    ↓
  CSS display: block (red badge visible)
```

### 4. Modal Display Logic
```
JavaScript Decision:
  if (data.total_pending > 0) {
    showModal() ← Bootstrap Modal
    displayNotificationsModal(data) ← populate items
    updateBellBadge(data) ← sync badge
  }
```

---

## Timeline for Safi User

| Time | Action | Status |
|------|--------|--------|
| T+0s | Enters credentials | On login page |
| T+1s | Submits login form | Processing |
| T+2s | Authenticated | account_adapter runs |
| T+2.5s | Session set to INT-005 | Auto-entity selected |
| T+3s | Redirected to /dashboard/ | Navigating |
| T+4s | Dashboard HTML loads | Parsing |
| T+4.5s | JavaScript executes | Event listeners added |
| T+5s | fetch() called | API request sent |
| T+5.5s | API returns data | { total_pending: 2 } |
| T+6s | Bell badge updated | Shows "2" in red |
| T+6s | Modal initialized | Bootstrap ready |
| T+6.5s | Modal shown | Notification popup visible |
| T+7s | **Safi sees modal** | **Ready to take action** |

---

## Result

✅ **Seamless User Experience**
- No entity selection delay
- Immediate notification visibility
- Clear pending actions
- One-click access to contributions
