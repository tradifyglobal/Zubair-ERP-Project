# Leave Balance System - Visual Flowcharts

## 1. Adding Leave Balance - Step by Step

```
┌─────────────────────────────────────┐
│  User navigates to HR Module        │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Clicks: Leave Management           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Selects: Leave Balances            │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Leave Balances      │
        │  List View           │
        │                      │
        │  [+Add Leave Balance] │◄──── Click here
        │                      │
        │ ┌──────────────────┐ │
        │ │ Employee │Type│Yr│ │
        │ ├──────────────────┤ │
        │ │ John │Annual│25│ │
        │ │ Alice│Sick │25│ │
        │ └──────────────────┘ │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Create Form         │
        │                      │
        │  Employee:    [▼]    │
        │  Leave Type:  [▼]    │
        │  Year:        [2025] │
        │  Opening:     [5]    │
        │  Allocated:   [20]   │
        │  Taken:       [0]    │
        │                      │
        │  Available: 25 days  │
        │  (auto-calculated)   │
        │                      │
        │    [Save] [Cancel]   │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  System Validates:   │
        │  ✓ Employee exists   │
        │  ✓ Leave type OK     │
        │  ✓ No duplicate      │
        │  ✓ Entity matches    │
        └──────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
         ✓ Valid      ✗ Invalid
            │             │
            ▼             ▼
        ┌────────┐    ┌────────┐
        │ Saved! │    │ Error! │
        └────────┘    └────────┘
            │             │
            ▼             ▼
        ┌─────────┐  ┌──────────┐
        │  Back   │  │  Fix &   │
        │   to    │  │  Retry   │
        │  List   │  └──────────┘
        └─────────┘
```

---

## 2. Leave Request Validation - Where Balance is Used

```
┌─────────────────────────────────────┐
│  Employee Submits Leave Request     │
│                                     │
│  Employee: John Smith               │
│  Leave Type: Annual Leave           │
│  From: 2025-01-20                   │
│  To: 2025-01-22                     │
│  Duration: 3 days                   │
│  Reason: Vacation                   │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ System Searches for: │
        │ LeaveBalance with:   │
        │ • employee = John    │
        │ • leave_type = Ann   │
        │ • year = 2025        │
        └──────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
       FOUND         NOT FOUND
            │             │
            ▼             ▼
    ┌────────────────┐ ┌──────────────┐
    │ Balance Exists │ │❌ Error      │
    │                │ │              │
    │ Opening: 5     │ │"Leave balance│
    │ Allocated: 20  │ │ not found    │
    │ Taken: 0       │ │ for this     │
    │ Available: 25  │ │ employee and │
    │                │ │ leave type.  │
    │ Check: 25 >= 3 │ │ Please       │
    └────────┬───────┘ │ contact HR"  │
             │         │              │
            ✓          │ User needs to:
            │          │ 1. Contact HR
            ▼          │ 2. Create balance
    ┌────────────────┐ │ 3. Retry request
    │ Approve        │ └──────────────┘
    │ Request        │
    │                │ Solution:
    │ Update taken:  │ → Go to HR
    │ 0 + 3 = 3      │ → Leave Balances
    │                │ → Add Balance
    │ Update avail:  │ → Fill form
    │ 25 - 3 = 22    │ → Save
    │                │ → Retry request
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │✓ Approved!     │
    │                │
    │Employee can    │
    │now use leave   │
    └────────────────┘
```

---

## 3. Balance Available Calculation

```
┌─────────────────────────────────────────┐
│  LEAVE BALANCE CALCULATION FORMULA      │
└─────────────────────────────────────────┘

    AVAILABLE = OPENING + ALLOCATED - TAKEN
       BALANCE    BALANCE    BALANCE   BALANCE

Example:
    AVAILABLE = 5 + 20 - 3
       (22 days)  (carryover) (annual) (used)

Scenario A: New Employee (No carryover)
    AVAILABLE = 0 + 20 - 0 = 20 days
    ├─ Opening: 0 (no previous year)
    ├─ Allocated: 20 (annual)
    └─ Taken: 0 (just hired)

Scenario B: Existing Employee (With carryover)
    AVAILABLE = 5 + 20 - 8 = 17 days
    ├─ Opening: 5 (from 2024)
    ├─ Allocated: 20 (2025 annual)
    └─ Taken: 8 (already used)

Scenario C: Over-allocated (Unusual)
    AVAILABLE = 2 + 15 - 20 = -3 days
    ├─ Opening: 2 (carryover)
    ├─ Allocated: 15 (annual)
    └─ Taken: 20 (overspent!)
    └─ ⚠️  Action: Review & correct

Real-Time Updates:
    Initial:     AVAILABLE = 5 + 20 - 0 = 25
    After 1st req:   AVAILABLE = 5 + 20 - 3 = 22
    After 2nd req:   AVAILABLE = 5 + 20 - 8 = 17
    After 3rd req:   AVAILABLE = 5 + 20 - 13 = 12
    ...
```

---

## 4. Complete System Flow - From Error to Resolution

```
┌───────────────────────────────────────────┐
│ SCENARIO: Employee Wants to Take Leave    │
└───────────────────────┬───────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
     ┌──────▼────────┐      ┌───────▼─────────┐
     │ First Time?   │      │ Existing User?  │
     │ YES           │      │ Balance exists  │
     └──────┬────────┘      └───────┬─────────┘
            │                       │
            ▼                       │
     ┌──────────────────┐           │
     │No Leave Balance  │           │
     │existing          │           │
     └──────┬───────────┘           │
            │                       │
            ▼                       ▼
     ┌──────────────────┐    ┌──────────────────┐
     │HR Admin creates  │    │System validates  │
     │leave balance:    │    │balance available │
     │1.Go to HR menu   │    │                  │
     │2.Leave Balances  │    │Check: avail >= ? │
     │3.Add button      │    │        requested │
     │4.Fill form:      │    └──────┬───────────┘
     │  -Employee       │           │
     │  -LeaveType      │    ┌──────┴──────┐
     │  -Year           │    │             │
     │  -Opening Bal    │  ✓ YES        ✗ NO
     │  -Allocated      │    │             │
     │  -Taken          │    ▼             ▼
     │5.Save            │ ┌───────┐   ┌────────┐
     └──────┬───────────┘ │✓Approv│   │❌Error │
            │             │ed!    │   │        │
            ▼             └───┬───┘   │Insuff. │
     ┌──────────────────┐    │       │Balance │
     │✓ Balance Created │    │       └────┬───┘
     └──────┬───────────┘    │            │
            │                │ Need more   │
            ▼                │ leave or    │
     ┌──────────────────┐    │ carryover   │
     │Employee retries  │    │            │
     │leave request     │    ▼            │
     └──────┬───────────┘ ┌───────────┐   │
            │             │Go on dates│   │
            │             │differently│   │
            │             │or defer   │   │
            │             └───┬───────┘   │
            │                 │           │
            └────────┬────────┴───────────┘
                     │
                     ▼
            ┌──────────────────┐
            │Employee has way  │
            │forward now!      │
            │✓ Can take leave  │
            └──────────────────┘
```

---

## 5. Data Relationships

```
                    ┌─────────────────┐
                    │    ENTITY       │
                    │ (Organization)  │
                    │                 │
                    │ Pristine Planet │
                    │ OR Tradify ERP  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌────────────┐ ┌────────────┐ ┌──────────┐
        │ EMPLOYEE   │ │ LEAVE TYPE │ │DEPARTMENT│
        │            │ │            │ │          │
        │John Smith  │ │Annual Leave│ │HR        │
        │HR-001      │ │20 days/yr  │ │or IT     │
        │john@co.com │ │            │ │          │
        │            │ │CODE: AL    │ │          │
        └─────┬──────┘ └─────┬──────┘ └──────────┘
              │              │
              └──────┬───────┘
                     │
                     ▼
            ┌────────────────────┐
            │  LEAVE BALANCE     │
            │                    │
            │ Unique Key:        │
            │ (Employee,         │
            │  LeaveType,        │
            │  Year)             │
            │                    │
            │ John + Annual + 25 │
            │                    │
            │ Opening:    5 days │
            │ Allocated: 20 days │
            │ Taken:      3 days │
            │ Available: 22 days │
            └──────┬─────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
    ┌─────────────┐    ┌──────────────┐
    │LEAVE REQUEST│    │PAYROLL RECORD│
    │             │    │              │
    │From:Jan 20  │    │Uses data for │
    │To: Jan 22   │    │calculations  │
    │Duration: 3  │    │              │
    │Status:Approv│    │              │
    │             │    │              │
    │Auto-updates │    │              │
    │Taken: 3→6   │    │              │
    └─────────────┘    └──────────────┘
```

---

## 6. UI Layout - Leave Balance Form

```
┌─────────────────────────────────────────────────┐
│  LEAVE BALANCE FORM                             │
├─────────────────────────────────────────────────┤
│                                                 │
│  LEFT COLUMN (2/3)        RIGHT COLUMN (1/3)   │
│  ─────────────────        ──────────────────   │
│                                                 │
│  ┌─────────────────────┐ ┌──────────────────┐ │
│  │ Employee:  [▼]      │ │ INFO PANEL       │ │
│  │ Leave Type:[▼]      │ │                  │ │
│  └─────────────────────┘ │ • Fields explain │ │
│                          │ • Example calc   │ │
│  ┌─────────────────────┐ │ • Tips & tricks  │ │
│  │ Year:      [2025]   │ │                  │ │
│  └─────────────────────┘ │ IMPORTANT:       │ │
│                          │ • 1 per emp/type │ │
│  ┌─────────────────────┐ │ • No duplicates  │ │
│  │ Opening:   [5  ]    │ │ • Contact HR if  │ │
│  │ Allocated: [20 ]    │ │   issues         │ │
│  │ Taken:     [3  ]    │ │                  │ │
│  └─────────────────────┘ └──────────────────┘ │
│                                                 │
│  ┌──────────────────────────────────────────┐ │
│  │ AVAILABLE BALANCE: 22 days               │ │
│  │ (Auto-calculated: 5 + 20 - 3 = 22)      │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
│            [SAVE] [CANCEL]                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 7. System Status Check

```
┌──────────────────────────────────────────┐
│  LEAVE BALANCE SYSTEM - QUICK CHECK      │
├──────────────────────────────────────────┤
│                                          │
│  ✓ Model exists: LeaveBalance          │
│  ✓ Form created: LeaveBalanceForm       │
│  ✓ Views added:                         │
│    ✓ CreateView                         │
│    ✓ UpdateView                         │
│    ✓ DetailView                         │
│    ✓ ListView (enhanced)                │
│  ✓ URLs configured:                     │
│    ✓ /leave-balances/                   │
│    ✓ /leave-balances/create/            │
│    ✓ /leave-balances/{id}/              │
│    ✓ /leave-balances/{id}/update/       │
│  ✓ Templates created:                   │
│    ✓ leavebalance_form.html             │
│    ✓ leavebalance_detail.html           │
│    ✓ leavebalance_list.html             │
│  ✓ Integration working:                 │
│    ✓ Linked to employees                │
│    ✓ Linked to leave types              │
│    ✓ Used by leave requests             │
│  ✓ Entity segregation:                  │
│    ✓ Filtering by session entity        │
│    ✓ Validates entity match             │
│  ✓ Documentation:                       │
│    ✓ LEAVE_BALANCE_GUIDE.md             │
│    ✓ LEAVE_BALANCE_QUICK_REFERENCE.md   │
│    ✓ LEAVE_BALANCE_IMPLEMENTATION.md    │
│                                          │
│  STATUS: ✓ READY TO USE                │
│                                          │
└──────────────────────────────────────────┘
```

---

## 8. Error Resolution Timeline

```
BEFORE (❌ Error):                 AFTER (✓ Working):
─────────────────                  ─────────────────

Day 1: Employee tries leave    →   Day 1: Employee tries leave
       ❌ "Balance not found"         ✓ System checks balance
       Can't submit                  
                                Day 2: Admin notices error
Day 2: Employee frustrated         ✓ Goes to HR → Leave Balances
       Contacts HR             
       HR tells: "See admin"    Day 3: Admin creates balance
                                  • Employee: John
Day 3: Admin confused            • Type: Annual
       Looks in admin           • Year: 2025
       ❌ No way to add         • Opens: 5, Allocated: 20
       No form                  • Saves (2 minutes)
       
Day 4: Back and forth           Day 4: Employee retries
       Delays mount           ✓ Leaf request works
       No resolution          ✓ Balance shows 22 available
                              
                                Day 5: All subsequent requests
                                ✓ Process smoothly
                                ✓ Balances auto-update
                                ✓ No more errors
```

---

## 9. Entity Segregation Verification

```
┌─────────────────────────────────────────┐
│  ENTITY 1: Pristine Planet ERP Corp     │
├─────────────────────────────────────────┤
│                                         │
│  Employees:          Leave Types:      │
│  • John Smith        • Annual Leave    │
│  • Alice Johnson     • Sick Leave      │
│  • Bob Williams      • Casual Leave    │
│                                         │
│  Leave Balances:                       │
│  • John + Annual + 2025 → OpenBal: 5   │
│  • Alice + Sick + 2025 → OpenBal: 2   │
│  • Bob + Casual + 2025 → OpenBal: 0   │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ENTITY 2: Tradify ERP Corporation      │
├─────────────────────────────────────────┤
│                                         │
│  Employees:          Leave Types:      │
│  • Carol Smith       • Annual Leave    │
│  • David Lee         • Sick Leave      │
│  • Emma Brown        • Marriage Leave  │
│                                         │
│  Leave Balances:                       │
│  • Carol + Annual + 2025 → OpenBal: 0  │
│  • David + Sick + 2025 → OpenBal: 3    │
│  • Emma + Marriage + 2025 → OpenBal: 0 │
│                                         │
└─────────────────────────────────────────┘

Data Segregation:
✓ Employees see only their entity's balances
✓ Admins see only selected entity's data
✓ Cross-entity lookups prevented
✓ Session-based entity selection enforced
```

---

## 10. Component Integration Map

```
┌────────────────────────────────────────────────┐
│           LEAVE BALANCE SYSTEM                  │
│       (Core HR Module Component)                │
└────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────────┐ ┌────────────┐
   │Database │  │Form Layer    │ │View Layer  │
   │         │  │              │ │            │
   │LeaveB.. │  │LeaveBalanceF │ │CreateView  │
   │         │  │orm           │ │UpdateView  │
   │• Open   │  │              │ │DetailView  │
   │• Alloc  │  │Validation    │ │ListView    │
   │• Taken  │  │Duplicate chk │ │            │
   │• Avail  │  │Entity filter │ │            │
   └────┬────┘  └──────┬───────┘ └──────┬─────┘
        │              │                │
        └──────────────┼────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌────────┐ ┌────────────┐ ┌───────────┐
    │Templates│ │URL Routes  │ │Integration│
    │         │ │            │ │           │
    │Form.htm │ │/list/      │ │Leave      │
    │Detail.. │ │/create/    │ │Request   │
    │List.htm │ │/{id}/      │ │Payroll    │
    │         │ │/{id}/upd..│ │Reporting │
    └────┬────┘ └────┬───────┘ └───────┬───┘
         │           │                │
         └───────────┼────────────────┘
                     │
                     ▼
            ┌────────────────────┐
            │  USER INTERFACE    │
            │                    │
            │  HR Menu           │
            │  └─ Leave Mgmt     │
            │    └─ Balances     │
            │      └─ [List/Add] │
            │                    │
            │  Employee sees:    │
            │  ✓ Their balance   │
            │  ✓ Available days  │
            │  ✓ Can take leave  │
            └────────────────────┘
```

---

**All flowcharts demonstrate the Leave Balance system is complete, integrated, and ready for use!**

