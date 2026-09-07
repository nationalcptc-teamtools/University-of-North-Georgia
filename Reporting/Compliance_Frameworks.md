# Red Team Compliance Framework Summary

## Purpose

The goal of compliance during CPTC is not to memorize frameworks.

The goal is to understand how to connect:

**Technical Finding → Failed Security Control → Business Risk → Recommendation**

Different frameworks serve different purposes, so they should not all be treated the same way.

---

# 1. NIST Cybersecurity Framework 2.0

## What It Is

NIST CSF 2.0 is a cybersecurity **risk-management framework**.

It gives organizations a way to describe what cybersecurity outcomes they should achieve without prescribing every technical configuration.

It is especially useful for explaining cybersecurity findings to leadership.

## Six Functions

### Govern

Focuses on how cybersecurity is managed across the organization.

Includes:

* Organizational context
* Risk-management strategy
* Roles and responsibilities
* Security policies
* Oversight
* Supply-chain risk

### Identify

Focuses on understanding what systems, assets, and risks exist.

Includes:

* Asset inventory
* Risk assessment
* Identifying vulnerabilities
* Identifying areas for improvement

Example:

> An organization has an unsupported server that nobody knew was still connected to the network.

This is both a technical issue and an **asset-management failure**.

### Protect

Focuses on safeguards designed to prevent compromise.

Includes:

* Authentication
* Access control
* Awareness training
* Data protection
* Platform security
* Infrastructure resilience

Common Red Team mappings:

* Weak passwords → Protect
* No MFA → Protect
* Excessive privileges → Protect
* Sensitive data exposed → Protect
* Poor system configuration → Protect
* Unpatched systems → Protect

### Detect

Focuses on identifying malicious or abnormal activity.

Includes:

* Continuous monitoring
* Logging
* Alerting
* Security-event analysis

Example:

> Red Team successfully performs multiple failed logins followed by privileged access without generating an alert.

This demonstrates a weakness in the organization's **Detect capability**.

### Respond

Focuses on what the organization does after detecting an incident.

Includes:

* Incident management
* Incident analysis
* Communication
* Containment
* Mitigation

### Recover

Focuses on restoring systems and operations after an incident.

Includes:

* Recovery planning
* Backups
* Restoration
* Business continuity
* Recovery communication

---

## Current vs. Target Profiles

### Current Profile

Describes the organization's current cybersecurity posture.

### Target Profile

Describes where the organization wants its cybersecurity posture to be.

The difference between the two represents a **security gap**.

---

## NIST CSF Tiers

### Tier 1 – Partial

Security is mostly informal or reactive.

### Tier 2 – Risk Informed

Cybersecurity risks are understood, but processes may not be consistently implemented.

### Tier 3 – Repeatable

Security processes are formally documented and consistently followed.

### Tier 4 – Adaptive

The organization continuously improves based on threats, incidents, and lessons learned.

---

## CPTC Use

NIST CSF is best for:

* Executive summaries
* Overall security posture
* Business risk
* Recommendations
* Security strategy
* C-Suite presentations

**Think of NIST CSF as the big-picture framework.**

---

# 2. NIST SP 800-53 Rev. 5

## What It Is

NIST SP 800-53 is a detailed catalog of cybersecurity and privacy controls.

NIST CSF describes **what an organization should accomplish**.

NIST 800-53 provides controls that can help accomplish those goals.

---

## Major Control Families

There are 20 control families.

The most important ones for Red Team activities are below.

### AC – Access Control

Focuses on who can access systems and what privileges they receive.

Common findings:

* Excessive privileges
* Poor role separation
* Insecure remote access
* Unrestricted access

Important concept:

**Least Privilege**

Users should only have the permissions required to perform their job.

---

### IA – Identification and Authentication

Focuses on verifying user identities.

Common findings:

* Weak passwords
* Default credentials
* No MFA
* Shared accounts
* Poor privileged-account authentication

---

### CM – Configuration Management

Focuses on securely configuring systems.

Common findings:

* Default configurations
* Unnecessary services
* Insecure system settings
* Unauthorized software
* Poor security baselines

---

### RA – Risk Assessment

Focuses on identifying and evaluating cybersecurity risks.

Important area:

**Vulnerability Monitoring and Scanning**

Common findings:

* Known vulnerabilities
* Unsupported systems
* Missing vulnerability management
* Poor patch-management practices

---

### AU – Audit and Accountability

Focuses on logging and monitoring activity.

Common findings:

* Missing logs
* Insufficient log retention
* Logs not reviewed
* Security events not detected

---

### SI – System and Information Integrity

Focuses on protecting systems from malicious activity and maintaining integrity.

Common findings:

* Missing patches
* Malware defenses disabled
* Security alerts ignored
* Integrity-monitoring issues

---

### SC – System and Communications Protection

Focuses on network and communication security.

Common findings:

* Poor segmentation
* Exposed services
* Weak firewall rules
* Insecure network protocols
* Poor boundary protection

---

### IR – Incident Response

Focuses on handling security incidents.

Includes:

* Preparation
* Detection
* Analysis
* Containment
* Eradication
* Reporting

---

### CP – Contingency Planning

Focuses on maintaining operations after incidents.

Includes:

* Backups
* Disaster recovery
* Business continuity
* Restoration

---

## NIST 800-53B

800-53B provides security-control baselines.

Organizations can select controls based on system impact.

Common baselines include:

* Low Impact
* Moderate Impact
* High Impact

Organizations then tailor those baselines to their environment.

---

## NIST 800-53A

800-53A explains how organizations should **assess whether controls actually work**.

This is very relevant to penetration testing.

A control may exist on paper but still fail during testing.

---

## CPTC Use

NIST 800-53 is best for mapping findings to specific security-control families.

Example:

**Weak Administrator Password**

* NIST CSF → Protect
* NIST 800-53 → IA / AC
* Business Impact → Unauthorized privileged access

**Think of NIST 800-53 as the detailed control library.**

---

# 3. CIS Critical Security Controls v8.1

## What It Is

CIS Controls are a prioritized set of cybersecurity practices designed to defend against common attacks.

CIS is generally easier to map directly to technical findings than NIST 800-53.

There are:

* 18 Controls
* 153 Safeguards

---

## The 18 CIS Controls

1. Inventory and Control of Enterprise Assets
2. Inventory and Control of Software Assets
3. Data Protection
4. Secure Configuration of Enterprise Assets and Software
5. Account Management
6. Access Control Management
7. Continuous Vulnerability Management
8. Audit Log Management
9. Email and Web Browser Protections
10. Malware Defenses
11. Data Recovery
12. Network Infrastructure Management
13. Network Monitoring and Defense
14. Security Awareness and Skills Training
15. Service Provider Management
16. Application Software Security
17. Incident Response Management
18. Penetration Testing

---

## CIS Implementation Groups

### IG1

Basic cybersecurity protections.

Often described as **essential cyber hygiene**.

### IG2

Designed for organizations with more complex environments and dedicated IT/security resources.

### IG3

Designed for organizations with high-value systems, major regulatory requirements, or advanced threats.

---

## Common Red Team Mappings

### Unknown System

* Control 1
* Control 2

### Default Credentials

* Control 5

### Excessive Privileges

* Control 5
* Control 6

### Missing Patches

* Control 7

### Missing Logging

* Control 8

### Flat Network

* Control 12
* Control 13

### No Malware Protection

* Control 10

### Poor Backups

* Control 11

### Unrestricted Vendor Access

* Control 15

### SQL Injection

* Control 16

### Missing Incident Response Plan

* Control 17

---

## CPTC Use

CIS is one of the best frameworks for operators to use while documenting findings.

It is:

* Easy to understand
* Easy to map
* Highly technical
* Directly related to common penetration-testing findings

**Think of CIS as the practical security checklist.**

---

# 4. PCI DSS 4.0.1

## What It Is

PCI DSS is a security standard focused on protecting **payment-card information**.

It applies to environments that:

* Store cardholder data
* Process cardholder data
* Transmit cardholder data
* Affect the security of the Cardholder Data Environment

---

## 12 PCI DSS Requirements

1. Install and Maintain Network Security Controls
2. Apply Secure Configurations
3. Protect Stored Account Data
4. Protect Cardholder Data During Transmission
5. Protect Against Malicious Software
6. Develop and Maintain Secure Systems and Software
7. Restrict Access Based on Business Need
8. Identify Users and Authenticate Access
9. Restrict Physical Access
10. Log and Monitor Access
11. Test Security Regularly
12. Maintain Security Policies and Programs

---

## Cardholder Data Environment

The **Cardholder Data Environment**, or CDE, includes systems that store, process, or transmit cardholder data.

Systems that can affect the security of the CDE may also fall into scope.

This makes network segmentation extremely important.

Example:

Guest Wi-Fi
↓
Corporate Network
↓
Point-of-Sale Network

If poor segmentation allows an attacker to reach payment systems, the PCI impact becomes much more significant.

---

## Common Red Team Mappings

### Flat Network

Requirement 1

### Insecure Default Configuration

Requirement 2

### Exposed Card Information

Requirement 3

### Unencrypted Card Data

Requirement 4

### Missing Malware Protection

Requirement 5

### Vulnerable Web Application

Requirement 6

### Excessive Permissions

Requirement 7

### Weak Authentication

Requirement 8

### Poor Physical Security

Requirement 9

### Missing Logs

Requirement 10

### Missing Security Testing

Requirement 11

### Missing Security Policies

Requirement 12

---

## Theme Park Relevance

PCI DSS could be very relevant to:

* Ticket sales
* Online reservations
* Gift shops
* Restaurants
* Hotels
* Payment kiosks
* Point-of-sale systems

---

## CPTC Use

If payment systems are discovered, determine:

* Where payment information is stored
* Where it is processed
* Where it is transmitted
* Which systems can access the CDE
* Whether segmentation exists
* Whether compromised systems can affect payment security

**Think of PCI DSS as the payment-security standard.**

---

# 5. CISA Cybersecurity Performance Goals

## What They Are

CISA's Cross-Sector Cybersecurity Performance Goals are voluntary cybersecurity practices.

They are designed to prioritize high-impact protections that reduce common cybersecurity risks.

They are especially useful for **critical infrastructure and operational environments**.

---

## Major Areas

CISA guidance emphasizes areas such as:

* Asset inventories
* Eliminating default passwords
* Strong passwords
* Unique credentials
* Separate administrator accounts
* MFA
* Network segmentation
* Security training
* Encryption
* Data protection
* Secure system configurations
* Network diagrams
* Logging
* Backups
* Incident response

---

## IT and OT

CISA guidance is especially useful when Information Technology and Operational Technology interact.

### IT

Traditional systems such as:

* Workstations
* Servers
* Email
* Websites
* Corporate networks

### OT

Systems that interact with physical operations.

Examples in a theme park could include:

* Ride-control systems
* Maintenance systems
* Building controls
* Physical access systems
* Industrial equipment

---

## Theme Park Example

Guest Wi-Fi
↓
Corporate Network
↓
Maintenance Workstation
↓
Ride Network

Finding:

> Poor network segmentation allows compromise of a standard IT environment to create a potential path toward operational technology.

This becomes more serious because the impact could move beyond confidentiality and include:

* Operational outages
* Physical safety
* Business continuity
* Customer safety

---

## CPTC Use

CISA is especially helpful for discussing:

* IT/OT separation
* Critical systems
* Operational resilience
* Security priorities
* Network segmentation
* High-impact remediation

**Think of CISA CPGs as practical guidance for reducing real-world infrastructure risk.**

---

# 6. HIPAA Security Rule

## What It Is

HIPAA is a federal law and regulation.

It is **not simply a cybersecurity framework**.

The HIPAA Security Rule protects **Electronic Protected Health Information**, or ePHI.

---

## Three Types of Safeguards

### Administrative Safeguards

Include:

* Risk analysis
* Security management
* Employee security responsibilities
* Security training
* Incident response
* Contingency planning

### Physical Safeguards

Include:

* Facility access
* Workstation security
* Device protection
* Media controls

### Technical Safeguards

Include:

* Access control
* Audit controls
* Integrity
* Authentication
* Transmission security

---

## Important Limitation

Finding medical information does **not automatically mean HIPAA applies**.

The organization or system must fall under HIPAA requirements.

Do not automatically write:

> The client violated HIPAA.

Better wording:

> If this system processes ePHI on behalf of a HIPAA-regulated entity, the observed access-control weakness may have implications under HIPAA Security Rule requirements.

---

## CPTC Use

HIPAA becomes relevant when the scenario clearly establishes:

* Healthcare operations
* Medical records
* Health information
* A HIPAA-covered entity
* A business associate handling ePHI

**Think of HIPAA as regulated protection of health information.**

---

# 7. FERPA

## What It Is

FERPA is a federal privacy law covering education records.

It is **not a cybersecurity control framework**.

FERPA provides students and parents certain rights concerning education records and limits inappropriate disclosure of those records.

---

## Main FERPA Concepts

* Right to inspect records
* Right to request corrections
* Consent before certain disclosures
* Restrictions on releasing personally identifiable information
* Legitimate educational interest
* Annual notification of FERPA rights

---

## FERPA and Cybersecurity

FERPA does not prescribe a detailed cybersecurity framework.

However, schools need reasonable methods to protect education records.

A cybersecurity incident could therefore create FERPA concerns if education records are improperly accessed or disclosed.

Example:

> All employees can access student records regardless of job role.

This could create a FERPA issue because access is not restricted based on legitimate educational interest.

---

## Important Limitation

A technical vulnerability does not automatically equal a FERPA violation.

Example:

> Missing Windows patch

does not automatically mean:

> FERPA violation.

The issue needs to affect the confidentiality or disclosure of protected education records.

---

## CPTC Use

FERPA becomes relevant when systems contain:

* Student information
* Academic records
* Educational records
* Personally identifiable student information

**Think of FERPA as privacy protection for education records.**

---

# Framework Comparison

| Framework      | Main Purpose                               |
| -------------- | ------------------------------------------ |
| NIST CSF 2.0   | Overall cybersecurity risk management      |
| NIST SP 800-53 | Detailed cybersecurity controls            |
| CIS Controls   | Practical prioritized defenses             |
| PCI DSS        | Payment-card security                      |
| CISA CPGs      | High-impact IT/OT cybersecurity practices  |
| HIPAA          | Protection of regulated health information |
| FERPA          | Protection of education records            |

---

# Recommended CPTC Priority

For general CPTC reporting:

## Highest Priority

### NIST CSF 2.0

Best for:

* Business risk
* Executive reporting
* Overall cybersecurity posture

### CIS Controls

Best for:

* Technical findings
* Direct control mapping
* Operator documentation

### NIST SP 800-53

Best for:

* Detailed security-control references
* More formal reports
* Security requirements

---

## Situational Frameworks

### PCI DSS

Use when payment systems or cardholder data are involved.

### CISA

Use when operational systems, critical infrastructure, or IT/OT relationships are involved.

### HIPAA

Use when HIPAA-regulated health information is clearly involved.

### FERPA

Use when education records are involved.

---

# Finding Mapping Process

For every major finding, ask:

## 1. What Did We Exploit?

Example:

Weak administrator password.

## 2. What Security Control Failed?

Authentication and access control.

## 3. CIS Mapping

Potentially:

* Control 5 – Account Management
* Control 6 – Access Control Management

## 4. NIST CSF Mapping

Potentially:

**PR.AA – Identity Management, Authentication, and Access Control**

## 5. NIST 800-53 Mapping

Potentially:

* IA – Identification and Authentication
* AC – Access Control

## 6. Does a Specialized Requirement Apply?

Examples:

* PCI DSS if payment systems are affected
* HIPAA if regulated ePHI is affected
* FERPA if education records are affected

## 7. What Is the Business Impact?

Example:

> Weak privileged credentials could allow an attacker to gain administrative access and move laterally into critical systems.

## 8. What Should Be Done?

Example:

* Require strong unique passwords
* Implement MFA
* Separate administrative accounts
* Apply least privilege
* Monitor privileged authentication

## 9. Why Should Leadership Care?

Example:

> A single compromised credential could become a full-network compromise and lead to operational disruption, data exposure, or loss of critical services.

---

# Key Red Team Principle

Do not report compliance findings as:

> This violates NIST.

NIST is generally not a law.

Instead write:

> This condition is inconsistent with NIST CSF access-control practices.

or:

> The observed weakness demonstrates a gap in the organization's Protect capability.

or:

> This finding maps to CIS Control 6 – Access Control Management.

Compliance should help explain **why the technical vulnerability matters**, not just add another acronym to the report.
