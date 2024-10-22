# Awesome Incident Response [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome) [![Check URLs](https://github.com/meirwah/awesome-incident-response/actions/workflows/check_urls.yml/badge.svg)](https://github.com/meirwah/awesome-incident-response/actions/workflows/check_urls.yml)
> A curated list of tools and resources for security incident response, aimed to help security analysts and [DFIR](http://www.acronymfinder.com/Digital-Forensics%2c-Incident-Response-%28DFIR%29.html) teams.
Digital Forensics and Incident Response (DFIR) teams are groups of people in an organization responsible for managing the response to a security incident, including gathering evidence of the incident, remediating its effects, and implementing controls to prevent the incident from recurring in the future.
## Contents
- [Adversary Emulation](#adversary-emulation)
- [All-In-One Tools](#all-in-one-tools)
- [Books](#books)
- [Communities](#communities)
- [Disk Image Creation Tools](#disk-image-creation-tools)
- [Evidence Collection](#evidence-collection)
- [Incident Management](#incident-management)
- [Knowledge Bases](#knowledge-bases)
- [Linux Distributions](#linux-distributions)
- [Linux Evidence Collection](#linux-evidence-collection)
- [Log Analysis Tools](#log-analysis-tools)
- [Memory Analysis Tools](#memory-analysis-tools)
- [Memory Imaging Tools](#memory-imaging-tools)
- [OSX Evidence Collection](#osx-evidence-collection)
- [Other Lists](#other-lists)
- [Other Tools](#other-tools)
- [Playbooks](#playbooks)
- [Process Dump Tools](#process-dump-tools)
- [Sandboxing/Reversing Tools](#sandboxingreversing-tools)
- [Scanner Tools](#scanner-tools)
- [Timeline Tools](#timeline-tools)
- [Videos](#videos)
- [Windows Evidence Collection](#windows-evidence-collection)
## IR Tools Collection
### Adversary Emulation
* [APTSimulator](https://github.com/NextronSystems/APTSimulator) - Windows Batch script that uses a set of tools and output files to make a system look as if it was compromised.
* [Atomic Red Team (ART)](https://github.com/redcanaryco/atomic-red-team) - Small and highly portable detection tests mapped to the MITRE ATT&CK Framework.
* [AutoTTP](https://github.com/jymcheong/AutoTTP) - Automated Tactics Techniques & Procedures. Re-running complex sequences manually for regression tests, product evaluations, generate data for researchers.
* [Caldera](https://github.com/mitre/caldera) - Automated adversary emulation system that performs post-compromise adversarial behavior within Windows Enterprise networks. It generates plans during operation using a planning system and a pre-configured adversary model based on the Adversarial Tactics, Techniques & Common Knowledge (ATT&CK™) project.
* [DumpsterFire](https://github.com/TryCatchHCF/DumpsterFire) - Modular, menu-driven, cross-platform tool for building repeatable, time-delayed, distributed security events. Easily create custom event chains for Blue Team drills and sensor /   alert mapping. Red Teams can create decoy incidents, distractions, and lures to support and scale their operations.
* [Metta](https://github.com/uber-common/metta) - Information security preparedness tool to do adversarial simulation.
* [Network Flight Simulator](https://github.com/alphasoc/flightsim) - Lightweight utility used to generate malicious network traffic and help security teams to evaluate security controls and network visibility.
* [Red Team Automation (RTA)](https://github.com/endgameinc/RTA) - RTA provides a framework of scripts designed to allow blue teams to test their detection capabilities against malicious tradecraft, modeled after MITRE ATT&CK.
* [RedHunt-OS](https://github.com/redhuntlabs/RedHunt-OS) - Virtual machine for adversary emulation and threat hunting.
### All-In-One Tools
* [Belkasoft Evidence Center](https://belkasoft.com/ec) -  The toolkit will quickly extract digital evidence from multiple sources by analyzing hard drives, drive images, memory dumps, iOS, Blackberry and Android backups, UFED, JTAG and chip-off dumps.
* [CimSweep](https://github.com/PowerShellMafia/CimSweep) - Suite of CIM/WMI-based tools that enable the ability to perform incident response and hunting operations remotely across all versions of Windows.
* [CIRTkit](https://github.com/byt3smith/CIRTKit) - CIRTKit is not just a collection of tools, but also a framework to aid in the ongoing unification of Incident Response and Forensics investigation processes.
* [Cyber Triage](http://www.cybertriage.com) - Cyber Triage collects and analyzes host data to determine if it is compromised. It's scoring system and recommendation engine allow you to quickly focus on the important artifacts. It can import data from its collection tool, disk images, and other collectors (such as KAPE). It can run on an examiner's desktop or in a server model. Developed by Sleuth Kit Labs, which also makes Autopsy. 
* [Dissect](https://github.com/fox-it/dissect) - Dissect is a digital forensics & incident response framework and toolset that allows you to quickly access and analyse forensic artefacts from various disk and file formats, developed by Fox-IT (part of NCC Group).
* [Doorman](https://github.com/mwielgoszewski/doorman) - osquery fleet manager that allows remote management of osquery configurations retrieved by nodes. It takes advantage of osquery's TLS configuration, logger, and distributed read/write endpoints, to give administrators visibility across a fleet of devices with minimal overhead and intrusiveness.
* [Falcon Orchestrator](https://github.com/CrowdStrike/falcon-orchestrator) - Extendable Windows-based application that provides workflow automation, case management and security response functionality.
* [Flare](https://github.com/fireeye/flare-vm) - A fully customizable, Windows-based security distribution for malware analysis, incident response, penetration testing.
* [Fleetdm](https://github.com/fleetdm/fleet) - State of the art host monitoring platform tailored for security experts. Leveraging Facebook's battle-tested osquery project, Fleetdm delivers continuous updates, features and fast answers to big questions.
* [GRR Rapid Response](https://github.com/google/grr) - Incident response framework focused on remote live forensics. It consists of a python agent (client) that is installed on target systems, and a python server infrastructure that can manage and talk to the agent. Besides the included Python API client, [PowerGRR](https://github.com/swisscom/PowerGRR) provides an API client library in PowerShell working on Windows, Linux and macOS for GRR automation and scripting.
* [IRIS](https://github.com/dfir-iris/iris-web) - IRIS is a web collaborative platform for incident response analysts allowing to share investigations at a technical level.
* [Kuiper](https://github.com/DFIRKuiper/Kuiper) - Digital Forensics Investigation Platform
* [Limacharlie](https://www.limacharlie.io/) - Endpoint security platform composed of a collection of small projects all working together that gives you a cross-platform (Windows, OSX, Linux, Android and iOS) low-level environment for managing and pushing additional modules into memory to extend its functionality.
* [Matano](https://github.com/matanolabs/matano): Open source serverless security lake platform on AWS that lets you ingest, store, and analyze petabytes of security data into an Apache Iceberg data lake and run realtime Python detections as code.
* [MozDef](https://github.com/mozilla/MozDef) - Automates the security incident handling process and facilitate the real-time activities of incident handlers.
* [MutableSecurity](https://github.com/MutableSecurity/mutablesecurity) - CLI program for automating the setup, configuration, and use of cybersecurity solutions.
* [nightHawk](https://github.com/biggiesmallsAG/nightHawkResponse) - Application built for asynchronous forensic data presentation using ElasticSearch as the backend. It's designed to ingest Redline collections.
* [Open Computer Forensics Architecture](http://sourceforge.net/projects/ocfa/) - Another popular distributed open-source computer forensics framework. This framework was built on Linux platform and uses postgreSQL database for storing data.
* [osquery](https://osquery.io/) - Easily ask questions about your Linux and macOS infrastructure using a SQL-like query language; the provided *incident-response pack* helps you detect and respond to breaches.
* [Redline](https://www.fireeye.com/services/freeware/redline.html) - Provides host investigative capabilities to users to find signs of malicious activity through memory and file analysis, and the development of a threat assessment profile.
* [SOC Multi-tool](https://github.com/zdhenard42/SOC-Multitool) - A powerful and user-friendly browser extension that streamlines investigations for security professionals.
* [The Sleuth Kit & Autopsy](http://www.sleuthkit.org) - Unix and Windows based tool which helps in forensic analysis of computers. It comes with various tools which helps in digital forensics. These tools help in analyzing disk images, performing in-depth analysis of file systems, and various other things.
* [TheHive](https://thehive-project.org/) - Scalable 3-in-1 open source and free solution designed to make life easier for SOCs, CSIRTs, CERTs and any information security practitioner dealing with security incidents that need to be investigated and acted upon swiftly.
* [Velociraptor](https://github.com/Velocidex/velociraptor) - Endpoint visibility and collection tool
* [X-Ways Forensics](http://www.x-ways.net/forensics/) - Forensics tool for Disk cloning and imaging. It can be used to find deleted files and disk analysis.
* [Zentral](https://github.com/zentralopensource/zentral) - Combines osquery's powerful endpoint inventory features with a flexible notification and action framework. This enables one to identify and react to changes on OS X and Linux clients.
### Books
* [Applied Incident Response](https://www.amazon.com/Applied-Incident-Response-Steve-Anson/dp/1119560268/) - Steve Anson's book on Incident Response.
* [Art of Memory Forensics](https://www.amazon.com/Art-Memory-Forensics-Detecting-Malware/dp/1118825098/) - Detecting Malware and Threats in Windows, Linux, and Mac Memory.
* [Crafting the InfoSec Playbook: Security Monitoring and Incident Response Master Plan](https://www.amazon.com/Crafting-InfoSec-Playbook-Security-Monitoring/dp/1491949406) - by Jeff Bollinger, Brandon Enright and Matthew Valites.
* [Digital Forensics and Incident Response: Incident response techniques and procedures to respond to modern cyber threats](https://www.amazon.com/Digital-Forensics-Incident-Response-techniques/dp/183864900X) - by Gerard Johansen.
* [Introduction to DFIR](https://medium.com/@sroberts/introduction-to-dfir-d35d5de4c180/) - By Scott J. Roberts.
* [Incident Response & Computer Forensics, Third Edition](https://www.amazon.com/Incident-Response-Computer-Forensics-Third/dp/0071798684/) - The definitive guide to incident response.
* [Incident Response Techniques for Ransomware Attacks](https://www.amazon.com/Incident-Response-Techniques-Ransomware-Attacks/dp/180324044X) - A great guide to build an incident response strategy for ransomware attacks. By Oleg Skulkin.
* [Incident Response with Threat Intelligence](https://www.amazon.com/Incident-response-Threat-Intelligence-intelligence-based/dp/1801072957) - Great reference to build an incident response plan based also on Threat Intelligence. By Roberto Martinez.
* [Intelligence-Driven Incident Response](https://www.amazon.com/Intelligence-Driven-Incident-Response-Outwitting-Adversary-ebook-dp-B074ZRN5T7/dp/B074ZRN5T7) - By Scott J. Roberts, Rebekah Brown.
* [Operator Handbook: Red Team + OSINT + Blue Team Reference](https://www.amazon.com/Operator-Handbook-Team-OSINT-Reference/dp/B085RR67H5/) - Great reference for incident responders.
* [Practical Memory Forensics](https://www.amazon.com/Practical-Memory-Forensics-Jumpstart-effective/dp/1801070334) - The definitive guide to practice memory forensics. By Svetlana Ostrovskaya and Oleg Skulkin.
* [The Practice of Network Security Monitoring: Understanding Incident Detection and Response](http://www.amazon.com/gp/product/1593275099) - Richard Bejtlich's book on IR.
### Communities
* [Digital Forensics Discord Server](https://discordapp.com/invite/JUqe9Ek) - Community of 8,000+ working professionals from Law Enforcement, Private Sector, and Forensic Vendors. Additionally, plenty of students and hobbyists! Guide [here](https://aboutdfir.com/a-beginners-guide-to-the-digital-forensics-discord-server/).
* [Slack DFIR channel](https://dfircommunity.slack.com) - Slack DFIR Communitiy channel - [Signup here](https://start.paloaltonetworks.com/join-our-slack-community).
### Disk Image Creation Tools
* [AccessData FTK Imager](http://accessdata.com/product-download/?/support/adownloads#FTKImager) - Forensics tool whose main purpose is to preview recoverable data from a disk of any kind. FTK Imager can also acquire live memory and paging file on 32bit and 64bit systems.
* [Bitscout](https://github.com/vitaly-kamluk/bitscout) - Bitscout by Vitaly Kamluk helps you build your fully-trusted customizable LiveCD/LiveUSB image to be used for remote digital forensics (or perhaps any other task of your choice). It is meant to be transparent and monitorable by the owner of the system, forensically sound, customizable and compact.
* [GetData Forensic Imager](http://www.forensicimager.com/) - Windows based program that will acquire, convert, or verify a forensic image in one of the following common forensic file formats.
* [Guymager](http://guymager.sourceforge.net) - Free forensic imager for media acquisition on Linux.
* [Magnet ACQUIRE](https://www.magnetforensics.com/magnet-acquire/) - ACQUIRE by Magnet Forensics allows various types of disk acquisitions to be performed on Windows, Linux, and OS X as well as mobile operating systems.
### Evidence Collection
* [Acquire](https://github.com/fox-it/acquire) - Acquire is a tool to quickly gather forensic artifacts from disk images or a live system into a lightweight container. This makes Acquire an excellent tool to, among others, speedup the process of digital forensic triage. It uses [Dissect](https://github.com/fox-it/dissect) to gather that information from the raw disk, if possible.
* [artifactcollector](https://github.com/forensicanalysis/artifactcollector) - The artifactcollector project provides a software that collects forensic artifacts on systems.