# homeassistant-cozylife

> Generated from repository-local OKF records. The Markdown/YAML bundle remains canonical.

Source: `homeassistant-cozylife`

The report separates the connected repository map from detailed component and key-concept views so large bundles remain reviewable.

## Connected-area overview

```mermaid
flowchart LR
    a0["docs · 25 concepts"]
    a1["repository root · 6 concepts"]
    a2["tasks · 1 concepts"]
    a0 -->|links| a1
    a0 -->|links| a2
    a1 -->|links| a0
    a2 -->|links| a0
    classDef default fill:#eef2ff,stroke:#4f46e5,color:#1e1b4b
```

## Connected component 1

### docs

```mermaid
flowchart LR
    n0["Architecture"]:::boundary
    n1["CozyLife Codebase Map"]:::boundary
    n2["CI"]:::knowledge
    n3["Core Beliefs"]:::knowledge
    n4["DIY Support Principles"]:::knowledge
    n5["Entity Surface Principles"]:::knowledge
    n6["Local-First Device Control"]:::knowledge
    n7["Design"]:::knowledge
    n8["DIY Support Plan"]:::knowledge
    n9["Documentation Harness Plan"]:::knowledge
    n10["Implementation Readiness"]:::knowledge
    n11["Completed Plan: Codebase Mapping"]:::knowledge
    n12["Tech Debt Tracker"]:::knowledge
    n13["Frontend"]:::knowledge
    n14["homeassistant-cozylife complete Markdown inventory"]:::knowledge
    n15["homeassistant-cozylife documentation map"]:::knowledge
    n16["homeassistant-cozylife repository OKF visualization"]:::knowledge
    n17["Plans"]:::knowledge
    n18["DIY Support"]:::knowledge
    n19["Entity Surface"]:::knowledge
    n20["Light Device Behaviour"]:::knowledge
    n21["New User Onboarding"]:::knowledge
    n22["Product Sense"]:::knowledge
    n23["Readiness Rubric"]:::knowledge
    n24["Reliability"]:::knowledge
    n25["Security"]:::knowledge
    n26["Support"]:::knowledge
    n27["Glossary"]:::boundary
    n28["Info"]:::boundary
    n29["CozyLife For Home Assistant"]:::boundary
    n30["Adopt RKE OKF knowledge format · done"]:::boundary
    n31["CozyLife Verification Audit"]:::boundary
    n0 -->|links| n15
    n1 -->|links| n15
    n2 -->|links| n15
    n3 -->|links| n15
    n4 -->|links| n15
    n5 -->|links| n15
    n6 -->|links| n15
    n7 -->|links| n15
    n8 -->|links| n15
    n9 -->|links| n15
    n10 -->|links| n15
    n11 -->|links| n15
    n12 -->|links| n15
    n13 -->|links| n15
    n14 -->|links| n0
    n14 -->|links| n1
    n14 -->|links| n2
    n14 -->|links| n3
    n14 -->|links| n4
    n14 -->|links| n5
    n14 -->|links| n6
    n14 -->|links| n7
    n14 -->|links| n8
    n14 -->|links| n9
    n14 -->|links| n10
    n14 -->|links| n11
    n14 -->|links| n12
    n14 -->|links| n13
    n14 -->|links| n15
    n14 -->|links| n16
    n14 -->|links| n17
    n14 -->|links| n18
    n14 -->|links| n19
    n14 -->|links| n20
    n14 -->|links| n21
    n14 -->|links| n22
    n14 -->|links| n23
    n14 -->|links| n24
    n14 -->|links| n25
    n14 -->|links| n26
    n14 -->|links| n27
    n14 -->|links| n28
    n14 -->|links| n29
    n14 -->|links| n30
    n14 -->|links| n31
    n15 -->|links| n29
    n15 -->|links| n14
    n15 -->|links| n0
    n15 -->|links| n1
    n15 -->|links| n8
    n15 -->|links| n9
    n15 -->|links| n10
    n15 -->|links| n11
    n15 -->|links| n12
    n15 -->|links| n17
    n15 -->|links| n23
    n15 -->|links| n3
    n15 -->|links| n4
    n15 -->|links| n5
    n15 -->|links| n6
    n15 -->|links| n7
    n15 -->|links| n13
    n15 -->|links| n27
    n15 -->|links| n18
    n15 -->|links| n19
    n15 -->|links| n20
    n15 -->|links| n21
    n15 -->|links| n24
    n15 -->|links| n2
    n15 -->|links| n22
    n15 -->|links| n28
    n15 -->|links| n25
    n15 -->|links| n26
    n15 -->|links| n31
    n15 -->|links| n30
    n15 -->|links| n16
    n16 -->|links| n15
    n16 -->|links| n14
    n16 -->|links| n30
    n17 -->|links| n15
    n18 -->|links| n15
    n19 -->|links| n15
    n20 -->|links| n15
    n21 -->|links| n15
    n22 -->|links| n15
    n23 -->|links| n15
    n24 -->|links| n15
    n25 -->|links| n15
    n26 -->|links| n15
    n27 -->|links| n15
    n28 -->|links| n15
    n29 -->|links| n26
    n29 -->|links| n0
    n29 -->|links| n24
    n29 -->|links| n15
    n30 -->|links| n15
    n30 -->|links| n16
    n31 -->|links| n15
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### repository root

```mermaid
flowchart LR
    n0["Architecture"]:::knowledge
    n1["CozyLife Codebase Map"]:::knowledge
    n2["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n3["homeassistant-cozylife documentation map"]:::boundary
    n4["Reliability"]:::boundary
    n5["Support"]:::boundary
    n6["Glossary"]:::knowledge
    n7["Info"]:::knowledge
    n8["CozyLife For Home Assistant"]:::knowledge
    n9["CozyLife Verification Audit"]:::knowledge
    n0 -->|links| n3
    n1 -->|links| n3
    n2 -->|links| n0
    n2 -->|links| n1
    n2 -->|links| n3
    n2 -->|links| n4
    n2 -->|links| n5
    n2 -->|links| n6
    n2 -->|links| n7
    n2 -->|links| n8
    n2 -->|links| n9
    n3 -->|links| n8
    n3 -->|links| n2
    n3 -->|links| n0
    n3 -->|links| n1
    n3 -->|links| n6
    n3 -->|links| n4
    n3 -->|links| n7
    n3 -->|links| n5
    n3 -->|links| n9
    n4 -->|links| n3
    n5 -->|links| n3
    n6 -->|links| n3
    n7 -->|links| n3
    n8 -->|links| n5
    n8 -->|links| n0
    n8 -->|links| n4
    n8 -->|links| n3
    n9 -->|links| n3
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### tasks

```mermaid
flowchart LR
    n0["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n1["homeassistant-cozylife documentation map"]:::boundary
    n2["homeassistant-cozylife repository OKF visualization"]:::boundary
    n3["Adopt RKE OKF knowledge format · done"]:::task
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n3 -->|links| n1
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

## Key concept neighbourhoods

### homeassistant-cozylife documentation map

```mermaid
flowchart LR
    n0["Architecture"]:::boundary
    n1["CozyLife Codebase Map"]:::boundary
    n2["CI"]:::boundary
    n3["Core Beliefs"]:::boundary
    n4["DIY Support Principles"]:::boundary
    n5["Entity Surface Principles"]:::boundary
    n6["Local-First Device Control"]:::boundary
    n7["Design"]:::boundary
    n8["DIY Support Plan"]:::boundary
    n9["Documentation Harness Plan"]:::boundary
    n10["Implementation Readiness"]:::boundary
    n11["Completed Plan: Codebase Mapping"]:::boundary
    n12["Tech Debt Tracker"]:::boundary
    n13["Frontend"]:::boundary
    n14["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n15["homeassistant-cozylife documentation map"]:::knowledge
    n16["homeassistant-cozylife repository OKF visualization"]:::boundary
    n17["Plans"]:::boundary
    n18["DIY Support"]:::boundary
    n19["Entity Surface"]:::boundary
    n20["Light Device Behaviour"]:::boundary
    n21["New User Onboarding"]:::boundary
    n22["Product Sense"]:::boundary
    n23["Readiness Rubric"]:::boundary
    n24["Reliability"]:::boundary
    n25["Security"]:::boundary
    n26["Support"]:::boundary
    n27["Glossary"]:::boundary
    n28["Info"]:::boundary
    n29["CozyLife For Home Assistant"]:::boundary
    n30["Adopt RKE OKF knowledge format · done"]:::boundary
    n31["CozyLife Verification Audit"]:::boundary
    n0 -->|links| n15
    n1 -->|links| n15
    n2 -->|links| n15
    n3 -->|links| n15
    n4 -->|links| n15
    n5 -->|links| n15
    n6 -->|links| n15
    n7 -->|links| n15
    n8 -->|links| n15
    n9 -->|links| n15
    n10 -->|links| n15
    n11 -->|links| n15
    n12 -->|links| n15
    n13 -->|links| n15
    n14 -->|links| n0
    n14 -->|links| n1
    n14 -->|links| n2
    n14 -->|links| n3
    n14 -->|links| n4
    n14 -->|links| n5
    n14 -->|links| n6
    n14 -->|links| n7
    n14 -->|links| n8
    n14 -->|links| n9
    n14 -->|links| n10
    n14 -->|links| n11
    n14 -->|links| n12
    n14 -->|links| n13
    n14 -->|links| n15
    n14 -->|links| n16
    n14 -->|links| n17
    n14 -->|links| n18
    n14 -->|links| n19
    n14 -->|links| n20
    n14 -->|links| n21
    n14 -->|links| n22
    n14 -->|links| n23
    n14 -->|links| n24
    n14 -->|links| n25
    n14 -->|links| n26
    n14 -->|links| n27
    n14 -->|links| n28
    n14 -->|links| n29
    n14 -->|links| n30
    n14 -->|links| n31
    n15 -->|links| n29
    n15 -->|links| n14
    n15 -->|links| n0
    n15 -->|links| n1
    n15 -->|links| n8
    n15 -->|links| n9
    n15 -->|links| n10
    n15 -->|links| n11
    n15 -->|links| n12
    n15 -->|links| n17
    n15 -->|links| n23
    n15 -->|links| n3
    n15 -->|links| n4
    n15 -->|links| n5
    n15 -->|links| n6
    n15 -->|links| n7
    n15 -->|links| n13
    n15 -->|links| n27
    n15 -->|links| n18
    n15 -->|links| n19
    n15 -->|links| n20
    n15 -->|links| n21
    n15 -->|links| n24
    n15 -->|links| n2
    n15 -->|links| n22
    n15 -->|links| n28
    n15 -->|links| n25
    n15 -->|links| n26
    n15 -->|links| n31
    n15 -->|links| n30
    n15 -->|links| n16
    n16 -->|links| n15
    n16 -->|links| n14
    n16 -->|links| n30
    n17 -->|links| n15
    n18 -->|links| n15
    n19 -->|links| n15
    n20 -->|links| n15
    n21 -->|links| n15
    n22 -->|links| n15
    n23 -->|links| n15
    n24 -->|links| n15
    n25 -->|links| n15
    n26 -->|links| n15
    n27 -->|links| n15
    n28 -->|links| n15
    n29 -->|links| n26
    n29 -->|links| n0
    n29 -->|links| n24
    n29 -->|links| n15
    n30 -->|links| n15
    n30 -->|links| n16
    n31 -->|links| n15
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### homeassistant-cozylife complete Markdown inventory

```mermaid
flowchart LR
    n0["Architecture"]:::boundary
    n1["CozyLife Codebase Map"]:::boundary
    n2["CI"]:::boundary
    n3["Core Beliefs"]:::boundary
    n4["DIY Support Principles"]:::boundary
    n5["Entity Surface Principles"]:::boundary
    n6["Local-First Device Control"]:::boundary
    n7["Design"]:::boundary
    n8["DIY Support Plan"]:::boundary
    n9["Documentation Harness Plan"]:::boundary
    n10["Implementation Readiness"]:::boundary
    n11["Completed Plan: Codebase Mapping"]:::boundary
    n12["Tech Debt Tracker"]:::boundary
    n13["Frontend"]:::boundary
    n14["homeassistant-cozylife complete Markdown inventory"]:::knowledge
    n15["homeassistant-cozylife documentation map"]:::boundary
    n16["homeassistant-cozylife repository OKF visualization"]:::boundary
    n17["Plans"]:::boundary
    n18["DIY Support"]:::boundary
    n19["Entity Surface"]:::boundary
    n20["Light Device Behaviour"]:::boundary
    n21["New User Onboarding"]:::boundary
    n22["Product Sense"]:::boundary
    n23["Readiness Rubric"]:::boundary
    n24["Reliability"]:::boundary
    n25["Security"]:::boundary
    n26["Support"]:::boundary
    n27["Glossary"]:::boundary
    n28["Info"]:::boundary
    n29["CozyLife For Home Assistant"]:::boundary
    n30["Adopt RKE OKF knowledge format · done"]:::boundary
    n31["CozyLife Verification Audit"]:::boundary
    n0 -->|links| n15
    n1 -->|links| n15
    n2 -->|links| n15
    n3 -->|links| n15
    n4 -->|links| n15
    n5 -->|links| n15
    n6 -->|links| n15
    n7 -->|links| n15
    n8 -->|links| n15
    n9 -->|links| n15
    n10 -->|links| n15
    n11 -->|links| n15
    n12 -->|links| n15
    n13 -->|links| n15
    n14 -->|links| n0
    n14 -->|links| n1
    n14 -->|links| n2
    n14 -->|links| n3
    n14 -->|links| n4
    n14 -->|links| n5
    n14 -->|links| n6
    n14 -->|links| n7
    n14 -->|links| n8
    n14 -->|links| n9
    n14 -->|links| n10
    n14 -->|links| n11
    n14 -->|links| n12
    n14 -->|links| n13
    n14 -->|links| n15
    n14 -->|links| n16
    n14 -->|links| n17
    n14 -->|links| n18
    n14 -->|links| n19
    n14 -->|links| n20
    n14 -->|links| n21
    n14 -->|links| n22
    n14 -->|links| n23
    n14 -->|links| n24
    n14 -->|links| n25
    n14 -->|links| n26
    n14 -->|links| n27
    n14 -->|links| n28
    n14 -->|links| n29
    n14 -->|links| n30
    n14 -->|links| n31
    n15 -->|links| n29
    n15 -->|links| n14
    n15 -->|links| n0
    n15 -->|links| n1
    n15 -->|links| n8
    n15 -->|links| n9
    n15 -->|links| n10
    n15 -->|links| n11
    n15 -->|links| n12
    n15 -->|links| n17
    n15 -->|links| n23
    n15 -->|links| n3
    n15 -->|links| n4
    n15 -->|links| n5
    n15 -->|links| n6
    n15 -->|links| n7
    n15 -->|links| n13
    n15 -->|links| n27
    n15 -->|links| n18
    n15 -->|links| n19
    n15 -->|links| n20
    n15 -->|links| n21
    n15 -->|links| n24
    n15 -->|links| n2
    n15 -->|links| n22
    n15 -->|links| n28
    n15 -->|links| n25
    n15 -->|links| n26
    n15 -->|links| n31
    n15 -->|links| n30
    n15 -->|links| n16
    n16 -->|links| n15
    n16 -->|links| n14
    n16 -->|links| n30
    n17 -->|links| n15
    n18 -->|links| n15
    n19 -->|links| n15
    n20 -->|links| n15
    n21 -->|links| n15
    n22 -->|links| n15
    n23 -->|links| n15
    n24 -->|links| n15
    n25 -->|links| n15
    n26 -->|links| n15
    n27 -->|links| n15
    n28 -->|links| n15
    n29 -->|links| n26
    n29 -->|links| n0
    n29 -->|links| n24
    n29 -->|links| n15
    n30 -->|links| n15
    n30 -->|links| n16
    n31 -->|links| n15
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### CozyLife For Home Assistant

```mermaid
flowchart LR
    n0["Architecture"]:::boundary
    n1["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n2["homeassistant-cozylife documentation map"]:::boundary
    n3["Reliability"]:::boundary
    n4["Support"]:::boundary
    n5["CozyLife For Home Assistant"]:::knowledge
    n0 -->|links| n2
    n1 -->|links| n0
    n1 -->|links| n2
    n1 -->|links| n3
    n1 -->|links| n4
    n1 -->|links| n5
    n2 -->|links| n5
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n2 -->|links| n4
    n3 -->|links| n2
    n4 -->|links| n2
    n5 -->|links| n4
    n5 -->|links| n0
    n5 -->|links| n3
    n5 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### homeassistant-cozylife repository OKF visualization

```mermaid
flowchart LR
    n0["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n1["homeassistant-cozylife documentation map"]:::boundary
    n2["homeassistant-cozylife repository OKF visualization"]:::knowledge
    n3["Adopt RKE OKF knowledge format · done"]:::boundary
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n3 -->|links| n1
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### Adopt RKE OKF knowledge format

```mermaid
flowchart LR
    n0["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n1["homeassistant-cozylife documentation map"]:::boundary
    n2["homeassistant-cozylife repository OKF visualization"]:::boundary
    n3["Adopt RKE OKF knowledge format · done"]:::task
    n0 -->|links| n1
    n0 -->|links| n2
    n0 -->|links| n3
    n1 -->|links| n0
    n1 -->|links| n3
    n1 -->|links| n2
    n2 -->|links| n1
    n2 -->|links| n0
    n2 -->|links| n3
    n3 -->|links| n1
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

### Architecture

```mermaid
flowchart LR
    n0["Architecture"]:::knowledge
    n1["homeassistant-cozylife complete Markdown inventory"]:::boundary
    n2["homeassistant-cozylife documentation map"]:::boundary
    n3["CozyLife For Home Assistant"]:::boundary
    n0 -->|links| n2
    n1 -->|links| n0
    n1 -->|links| n2
    n1 -->|links| n3
    n2 -->|links| n3
    n2 -->|links| n1
    n2 -->|links| n0
    n3 -->|links| n0
    n3 -->|links| n2
    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065
    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407
    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16
    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3
```

## Legend

- Blue: task
- Purple: workstream
- Orange: tracker profile
- Green: durable knowledge
- Dashed neutral nodes: neighbouring context repeated from another area or key-concept view
- Time references: edges to addressable `Task.time[]` fragments
- Arrows: structured relationships or repository-local Markdown links
