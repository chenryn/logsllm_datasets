# 应急响应大合集 [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)
用于安全事件响应的工具与资源的列表，旨在帮助安全分析师与 [DFIR](http://www.acronymfinder.com/Digital-Forensics%2c-Incident-Response-(DFIR).html) 团队。
DFIR 团队是组织中负责安全事件响应（包括事件证据、影响修复等）的人员组织，以防止组织将来再次发生该事件。
## 目录
 - [对抗模拟](#对抗模拟)
 - [多合一工具集](#多合一工具集)
 - [书籍](#书籍)
 - [社区](#社区)
 - [磁盘镜像创建工具](#磁盘镜像创建工具)
 - [证据收集](#证据收集)
 - [事件管理](#事件管理)
 - [知识库](#知识库)
 - [Linux 发行版](#linux-发行版)
 - [Linux 证据收集](#linux-证据收集)
 - [日志分析工具](#日志分析工具)
 - [内存分析工具](#内存分析工具)
 - [内存镜像工具](#内存镜像工具)
 - [OSX 证据收集](#osx-证据收集)
 - [其它清单](#其它清单)
 - [其他工具](#其他工具)
 - [Playbooks](#playbooks)
 - [进程 Dump 工具](#进程-dump-工具)
 - [沙盒／逆向工具](#沙盒／逆向工具)
 - [扫描工具](#扫描工具)
 - [时间线工具](#时间线工具)
 - [视频](#视频)
 - [Windows 证据收集](#windows-证据收集)
## IR 工具收集
### 对抗模拟
* [APTSimulator](https://github.com/NextronSystems/APTSimulator) - 使用一组工具与输出文件处理操作系统的 Windows 批处理脚本，使得系统看上去像被攻陷了。
* [Atomic Red Team (ART)](https://github.com/redcanaryco/atomic-red-team) - 与 MITRE ATT＆CK 框架匹配的便携测试工具。
* [AutoTTP](https://github.com/jymcheong/AutoTTP) - 自动策略技术与程序。手动重复运行复杂序列进行回归测试，产品评估，为研究人员生成数据。
* [Caldera](https://github.com/mitre/caldera) - 在 Windows Enterprise 网络中攻陷系统后执行敌对行为的自动对手仿真系统。运行时的行为由计划系统和基于 ATT＆CK™ 项目预先配置的对手模型生成。
* [DumpsterFire](https://github.com/TryCatchHCF/DumpsterFire) - DumpsterFire 工具集是一个模块化、菜单驱动的跨平台工具，用于构建可重复的分布式安全事件。创建 Blue Team 演戏与传感器报警映射关系的自定义事件链。Red Team 可以制造诱饵事件，分散防守方的注意力以支持和扩大战果。
* [Metta](https://github.com/uber-common/metta) - 用于进行敌对模拟的信息安全防御工具。
* [Network Flight Simulator](https://github.com/alphasoc/flightsim) - 用于生成恶意网络流量并帮助安全团队评估安全控制和网络可见性的轻量级程序。
* [Red Team Automation (RTA)](https://github.com/endgameinc/RTA) - RTA 提供了一个旨在让 Blue Team 在经历过 MITRE ATT&CK 模型为指导的攻击行为后的检测能力的脚本框架。
* [RedHunt-OS](https://github.com/redhuntlabs/RedHunt-OS) - 用于模拟对手与威胁狩猎的虚拟机。
### 多合一工具集
* [Belkasoft Evidence Center](https://belkasoft.com/ec) -  该工具包可以快速从多个数据源提取电子证据，包括硬盘、硬盘镜像、内存转储、iOS、黑莓与安卓系统备份、UFED、JTAG 与 chip-off 转储。
* [CimSweep](https://github.com/PowerShellMafia/CimSweep) - CimSweep 是一套基于 CIM/WMI 的工具，提供在所有版本的 Windows 上执行远程事件响应和追踪。
* [CIRTkit](https://github.com/byt3smith/CIRTKit) - CIRTKit 不仅是一个工具集合，更是一个框架，统筹事件响应与取证调查的进程。
* [Cyber Triage](http://www.cybertriage.com) - Cyber Triage 远程收集分析终端数据，以帮助确定计算机是否被入侵。其专注易用性与自动化，采用无代理的部署方法使公司在没有重大基础设施及取证专家团队的情况下做出响应。其分析结果用于决定该终端是否应该被擦除或者进行进一步调查。
* [Doorman](https://github.com/mwielgoszewski/doorman) - Doorman 是一个 osquery 的管理平台，可以远程管理节点的 osquery 配置。它利用 osquery 的 TLS 配置\记录器\分布式读写等优势仅以最小开销和侵入性为管理员提供一组设备的管理可见性。
* [Falcon Orchestrator](https://github.com/CrowdStrike/falcon-orchestrator) - Falcon Orchestrator 是由 CrowdStrike 提供的一个基于 Windows 可扩展的应用程序，提供工作流自动化、案例管理与安全应急响应等功能。
* [Flare](https://github.com/fireeye/flare-vm) - 为分析人员量身定制的、用于恶意软件分析/事件响应和渗透测试的 Windows 虚拟机。
* [Fleetdm](https://github.com/fleetdm/fleet) - 为安全专家量身定制的主机监控平台，利用 Facebook 久经考验的 osquery 支撑 Fleetdm 实现持续更新。
* [GRR Rapid Response](https://github.com/google/grr) - GRR Rapid Response 是一个用来远程现场实时取证的应急响应框架，其带有一个 Python 客户端安装在目标系统以及一个可以管理客户端的 Python 编写的服务器。除了 Python API 客户端外，[PowerGRR](https://github.com/swisscom/PowerGRR) 在 PowerShell 上也提供了 API 客户端库，该库可在 Windows、Linux 和 macOS 上运行，以实现 GRR 自动化和脚本化。
* [IRIS](https://github.com/dfir-iris/iris-web) - IRIS 是供事件响应人员使用的、可以共享调查进度的协作平台。
* [Kuiper](https://github.com/DFIRKuiper/Kuiper) - Kuiper 是数字取证调查平台。
* [Limacharlie](https://www.limacharlie.io/) - 一个终端安全平台，它本身是一个小项目的集合，并提供了一个跨操作系统的低级环境，你可以管理并推送附加功能进入内存给程序扩展功能。
* [MozDef](https://github.com/mozilla/MozDef) - Mozilla Defense Platform (MozDef) 旨在帮助安全事件处理自动化，并促进事件的实时处理。
* [nightHawk](https://github.com/biggiesmallsAG/nightHawkResponse) - nightHawk Response Platform 是一个以 ElasticSearch 为后台的异步取证数据呈现的应用程序，设计与 Redline 配合调查。
* [Open Computer Forensics Architecture](http://sourceforge.net/projects/ocfa/) - Open Computer Forensics Architecture (OCFA) 是另一个分布式开源计算机取证框架，这个框架建立在 Linux 平台上，并使用 postgreSQL 数据库来存储数据。
* [Osquery](https://osquery.io/) - osquery 可以找到 Linux 与 OSX 基础设施的问题,无论你是要入侵检测、基础架构可靠性检查或者合规性检查，osquery 都能够帮助你提高公司内部的安全组织能力, *incident-response pack* 可以帮助你进行检测\响应活动。
* [Redline](https://www.fireeye.com/services/freeware/redline.html) - 为用户提供主机调查工具，通过内存与文件分析来找到恶意行为的活动迹象，包括对威胁评估配置文件的开发
* [The Sleuth Kit & Autopsy](http://www.sleuthkit.org) - Sleuth Kit 是基于 Unix 和 Windows 的工具，可以帮助计算机取证分析，其中包含各种协助取证的工具，比如分析磁盘镜像、文件系统深度分析等
* [TheHive](https://thehive-project.org/) - TheHive 是一个可扩展的三合一开源解决方案，旨在让 SOC、CSIRT、CERT 或其他任何信息安全从业人员快速地进行安全事件调查。
* [Velociraptor](https://github.com/Velocidex/velociraptor) - 端点可见与相关信息收集工具。
* [X-Ways Forensics](http://www.x-ways.net/forensics/) - X-Ways 是一个用于磁盘克隆、镜像的工具，可以查找已经删除的文件并进行磁盘分析。
* [Zentral](https://github.com/zentralopensource/zentral) - 与 osquery 强大的端点清单保护能力相结合，通知与行动都灵活的框架，可以快速对 OS X 与 Linux 客户机上的更改做出识别与响应。
### 书籍
* [Applied Incident Response](https://www.amazon.com/Applied-Incident-Response-Steve-Anson/dp/1119560268/) - Steve Anson 编写的应急响应应用指南
* [Crafting the InfoSec Playbook: Security Monitoring and Incident Response Master Plan](https://www.amazon.com/Crafting-InfoSec-Playbook-Security-Monitoring/dp/1491949406) - 作者:Jeff Bollinger、Brandon Enright 和 Matthew Valites
* [Digital Forensics and Incident Response: Incident response techniques and procedures to respond to modern cyber threats](https://www.amazon.com/Digital-Forensics-Incident-Response-techniques/dp/183864900X) - 作者:Gerard Johansen
* [Dfir intro](https://medium.com/@sroberts/introduction-to-dfir-d35d5de4c180/)) - 作者:Scott J. Roberts
* [Incident Response & Computer Forensics, Third Edition](https://www.amazon.com/Incident-Response-Computer-Forensics-Third/dp/0071798684/) - 事件响应权威指南
* [Intelligence-Driven Incident Response](https://www.amazon.com/Intelligence-Driven-Incident-Response-Outwitting-Adversary-ebook-dp-B074ZRN5T7/dp/B074ZRN5T7) - 作者：Scott J. Roberts、Rebekah Brown
* [Operator Handbook: Red Team + OSINT + Blue Team Reference](https://www.amazon.com/Operator-Handbook-Team-OSINT-Reference/dp/B085RR67H5/) - 事件响应者的重要参考
* [The Practice of Network Security Monitoring: Understanding Incident Detection and Response](http://www.amazon.com/gp/product/1593275099) - 作者：Richard Bejtlich
### 社区
* [Digital Forensics Discord Server](https://discordapp.com/invite/JUqe9Ek) -来自执法部门、私营机构等地的 8000 多名在职专业人员组成的社区。[加入指南](https://aboutdfir.com/a-beginners-guide-to-the-digital-forensics-discord-server/)。
* [Slack DFIR channel](https://dfircommunity.slack.com) - Slack DFIR Communitiy channel - [Signup here](https://start.paloaltonetworks.com/join-our-slack-community)
### 磁盘镜像创建工具
* [AccessData FTK Imager](http://accessdata.com/product-download/?/support/adownloads#FTKImager) - AccessData FTK Imager 是一个从任何类型的磁盘中预览可恢复数据的取证工具，FTK Imager 可以在 32\64 位系统上实时采集内存与页面文件。
* [Bitscout](https://github.com/vitaly-kamluk/bitscout) - Vitaly Kamluk 开发的 Bitscout 可以帮助你定制一个完全可信的 LiveCD/LiveUSB 镜像以供远程数字取证使用（或者你需要的其它任务）。它对系统所有者透明且可被监控，同时可用于法庭质证、可定制且紧凑。 
* [GetData Forensic Imager](http://www.forensicimager.com/) - GetData Forensic Imager 是一个基于 Windows 程序，将常见的镜像文件格式进行获取\转换\验证取证
* [Guymager](http://guymager.sourceforge.net) - Guymager 是一个用于 Linux 上媒体采集的免费镜像取证器。
* [Magnet ACQUIRE](https://www.magnetforensics.com/magnet-acquire/) - Magnet Forensics 开发的 ACQUIRE 可以在不同类型的磁盘上执行取证,包括 Windows\Linux\OS X 与移动操作系统。
### 证据收集
* [artifactcollector](https://github.com/forensicanalysis/artifactcollector) - artifactcollector 提供了一个在系统上收集取证的工具。
* [bulk_extractor](https://github.com/simsong/bulk_extractor) - bulk_extractor 是一个计算机取证工具，可以扫描磁盘镜像、文件、文件目录，并在不解析文件系统或文件系统结构的情况下提取有用的信息，由于其忽略了文件系统结构，程序在速度和深入程度上都相比其它工具有了很大的提高。
* [Cold Disk Quick Response](https://github.com/rough007/CDQR) - 使用精简的解析器列表来快速分析取证镜像文件(dd, E01, .vmdk, etc)并输出报告。
* [CyLR](https://github.com/orlikoski/CyLR) - CyLR 可以快速、安全地从具有 NTFS 文件系统的主机收集取证镜像，并最大程度地减少对主机的影响。