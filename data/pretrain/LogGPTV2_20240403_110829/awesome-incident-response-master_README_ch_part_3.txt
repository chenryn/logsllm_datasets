* [Crits](https://crits.github.io/) - 一个将分析引擎与网络威胁数据库相结合且带有 Web 界面的工具
* [Diffy](https://github.com/Netflix-Skunkworks/diffy) - Netflix de  SIRT 开发的 DFIR 工具，允许调查人员快速地跨越云主机（AWS 的 Linux 实例）并通过审查基线的的差异来有效地审查这些实例以便进行后续操作
* [domfind](https://github.com/diogo-fernan/domfind) - *domfind* 一个用 Python 编写的 DNS 爬虫，它可以找到在不同顶级域名下面的相同域名.
* [Fileintel](https://github.com/keithjjones/fileintel) - 为每个文件哈希值提供情报
* [HELK](https://github.com/Cyb3rWard0g/HELK) - 威胁捕捉
* [Hindsight](https://github.com/obsidianforensics/hindsight) - 针对 Google Chrome/Chromium 中浏览历史的数字取证
* [Hostintel](https://github.com/keithjjones/hostintel) - 为每个主机提供情报
* [imagemounter](https://github.com/ralphje/imagemounter) - 命令行工具及 Python 包，可以简单地 mount/unmount 数字取证的硬盘镜像
* [Kansa](https://github.com/davehull/Kansa/) - Kansa 是一个 PowerShell 的模块化应急响应框架
* [MFT Browser](https://github.com/kacos2000/MFT_Browser) - MFT 目录树重建并记录信息
* [Munin](https://github.com/Neo23x0/munin) - 通过 VirusTotal 等其他在线服务检查文件哈希
* [PowerSponse](https://github.com/swisscom/PowerSponse) - PowerSponse 是专注于安全事件响应过程中遏制与补救的 PowerShell 模块
* [PyaraScanner](https://github.com/nogoodconfig/pyarascanner) - PyaraScanner 是一个非常简单的多线程、多规则、多文件的 YARA 扫描脚本
* [rastrea2r](https://github.com/rastrea2r/rastrea2r) - 使用 YARA 在 Windows、Linux 与 OS X 上扫描硬盘或内存
* [RaQet](https://raqet.github.io/) - RaQet 是一个非常规的远程采集与分类工具，允许对那些为取证构建的操作系统进行远端计算机的遴选
* [Raccine](https://github.com/Neo23x0/Raccine) - 简单的勒索软件保护工具
* [Stalk](https://www.percona.com/doc/percona-toolkit/2.2/pt-stalk.html) - 收集关于 MySQL 的取证数据
* [Scout2](https://nccgroup.github.io/Scout2/) - 帮助 Amazon Web 服务管理员评估其安全态势的工具
* [Stenographer](https://github.com/google/stenographer) - Stenographer 是一个数据包捕获解决方案，旨在快速将全部数据包转储到磁盘中，然后提供对这些数据包的快速访问。它存储尽可能多的历史记录并且管理磁盘的使用情况，在大小达到设定的上限时删除记录，非常适合在事件发生前与发生中捕获流量，而不是显式存储所有流量。
* [sqhunter](https://github.com/0x4d31/sqhunter) - 一个基于 osquery 和 Salt Open (SaltStack) 的威胁捕捉工具，它无需 osquery 的 tls 插件就能发出临时的或者分布式的查询。 sqhunter 也可以查询开放的 sockets，并将它们与威胁情报进行比对。
* [sysmon-config](https://github.com/SwiftOnSecurity/sysmon-config) - 默认高质量事件跟踪的 Sysmon 配置文件模板
* [sysmon-modular](https://github.com/olafhartong/sysmon-modular) - sysmon 配置模块的存储库
* [traceroute-circl](https://github.com/CIRCL/traceroute-circl) - 由 Computer Emergency Response Center Luxembourg 开发的 traceroute-circl 是一个增强型的 traceroute 来帮助 CSIRT\CERT 的工作人员，通常 CSIRT 团队必须根据收到的 IP 地址处理事件
* [X-Ray 2.0](https://www.raymond.cc/blog/xray/) - 一个用来向反病毒厂商提供样本的 Windows 实用工具(几乎不再维护)
### Playbooks
* [AWS Incident Response Runbook Samples](https://github.com/aws-samples/aws-incident-response-runbooks/tree/0d9a1c0f7ad68fb2c1b2d86be8914f2069492e21) - AWS IR Runbook Samples 旨在针对三个案例（DoS 或 DDoS 攻击、凭据泄漏、意外访问 Amazon S3 存储桶）进行定制。
* [Counteractive Playbooks](https://github.com/counteractive/incident-response-plan-template/tree/master/playbooks) - Counteractive PLaybooks 集合
* [GuardSIght Playbook Battle Cards](https://github.com/guardsight/gsvsoc_cirt-playbook-battle-cards) - 网络事件响应手册集合
* [IRM](https://github.com/certsocietegenerale/IRM) - CERT Societe Generale 开发的事件响应方法论
* [PagerDuty Incident Response Documentation](https://response.pagerduty.com/) - 描述 PagerDuty 应急响应过程的文档，不仅提供了关于事件准备的信息，还提供了在此前与之后要做什么工作，源在 [GitHub](https://github.com/PagerDuty/incident-response-docs) 上。
* [Phantom Community Playbooks](https://github.com/phantomcyber/playbooks) - Splunk 的 Phantom 社区手册
* [ThreatHunter-Playbook](https://github.com/OTRF/ThreatHunter-Playbook) - 帮助开展威胁狩猎的手册
### 进程 Dump 工具
* [Microsoft ProcDump](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump) - 用户模式下的进程 dump 工具，可以 dump 任意正在运行的 Win32 进程内存映像
* [PMDump](http://www.ntsecurity.nu/toolbox/pmdump/) - PMDump 是一个可以在不停止进程的情况下将进程的内存内容 dump 到文件中的工具
### 沙盒／逆向工具
* [Any Run](https://app.any.run/) - 交互式恶意软件分析服务，对大多数类型的威胁进行静态与动态分析
* [CAPEv2](https://github.com/kevoreilly/CAPEv2) - 恶意软件配置与 Payload 提取
* [Cuckoo](https://github.com/cuckoosandbox/cuckoo) - 开源沙盒工具，高度可定制化
* [Cuckoo-modified](https://github.com/spender-sandbox/cuckoo-modified) - 社区基于 Cuckoo 的大修版
* [Cuckoo-modified-api](https://github.com/keithjjones/cuckoo-modified-api) - 一个用来控制 Cuckoo 沙盒设置的 Python 库
* [Cutter](https://github.com/rizinorg/cutter) - 由 驱动的逆向工程框架
* [Ghidra](https://github.com/NationalSecurityAgency/ghidra) - 软件逆向工程框架
* [Hybrid-Analysis](https://www.hybrid-analysis.com/) - Hybrid-Analysis 是一个由 Payload Security 提供的免费在线沙盒
* [Intezer](https://analyze.intezer.com/#/) - 深入分析 Windows 二进制文件，检测与已知威胁的 micro-code 相似性，以便提供准确且易于理解的结果
* [Joe Sandbox (Community)](https://www.joesandbox.com/) - Joe Sandbox 沙盒分析检测 Windows、Android、Mac OS、Linux 和 iOS 中的恶意软件与 URL，查找可疑文件并提供全面、详细的分析报告
* [Mastiff](https://github.com/KoreLogicSecurity/mastiff) - MASTIFF 是一个静态分析框架，可以自动化的从多种文件格式中提取关键特征。
* [Metadefender Cloud](https://www.metadefender.com) - Metadefender 是一个免费的威胁情报平台，提供多点扫描、数据清理以及对文件的脆弱性分析
* [Radare2](https://github.com/radareorg/radare2) - 逆向工程框架与命令行工具集
* [Reverse.IT](https://www.reverse.it/) - 由 CrowdStrike 提供支持的分析工具
* [StringSifter](https://github.com/fireeye/stringsifter) - 利用机器学习根据字符串与恶意软件分析的相关性对其进行排名
* [Valkyrie Comodo](https://valkyrie.comodo.com) - Valkyrie 使用运行时行为与文件的数百个特征进行分析
* [Viper](https://github.com/viper-framework/viper) - Viper 是一个基于 Python 的二进制程序分析及管理框架，支持 Cuckoo 与 YARA
* [Virustotal](https://www.virustotal.com) - Virustotal, Google 的子公司，一个免费在线分析文件/URL的厂商，可以分析病毒\蠕虫\木马以及其他类型被反病毒引擎或网站扫描器识别的恶意内容
* [Visualize_Logs](https://github.com/keithjjones/visualize_logs) - Cuckoo、Procmon等日志的开源可视化库
* [Yomi](https://yomi.yoroi.company) - Yoroi 托管的免费多沙盒服务。
### 扫描工具
* [Fenrir](https://github.com/Neo23x0/Fenrir) - Fenrir 是一个简单的 IOC 扫描器，可以在纯 bash 中扫描任意 Linux/Unix/OSX 系统，由 THOR 与 LOKI 的开发者编写
* [LOKI](https://github.com/Neo23x0/Loki) -  Loki 是一个使用 YARA 与其他 IOC 对终端进行扫描的免费 IR 扫描器
* [Spyre](https://github.com/spyre-project/spyre) - 使用 Go 编写的基于 YARA 的 IOC 扫描工具
### 时间线工具
* [Aurora Incident Response](https://github.com/cyb3rfox/Aurora-Incident-Response) - 构建事件的详细时间表的平台
* [Highlighter](https://www.fireeye.com/services/freeware/highlighter.html) - Fire/Mandiant 开发的免费工具，来分析日志/文本文件，可以对某些关键字或短语进行高亮显示，有助于时间线的整理
* [Morgue](https://github.com/etsy/morgue) - 一个 Etsy 开发的 PHP Web 应用，可用于管理事后处理
* [Plaso](https://github.com/log2timeline/plaso) -  一个基于 Python 用于 log2timeline 的后端引擎
* [Timesketch](https://github.com/google/timesketch) - 用于协作取证时间线分析的开源工具
### 视频
* [The Future of Incident Response](https://www.youtube.com/watch?v=bDcx4UNpKNc) - Bruce Schneier 在 OWASP AppSecUSA 2015 上的分享
### Windows 证据收集
* [AChoir](https://github.com/OMENScan/AChoir) - Achoir 是一个将对 Windows 的实时采集工具脚本化变得更标准与简单的框架
* [Crowd Response](http://www.crowdstrike.com/community-tools/) - 由 CrowdStrike 开发的 Crowd Response 是一个轻量级 Windows 终端应用,旨在收集用于应急响应与安全操作的系统信息，其包含许多模块与输出格式。
* [DFIR ORC](https://dfir-orc.github.io/) - DFIR ORC 是专门用于证据收集的关键组件，提供了 Windows 计算机的取证快照，代码在 [GitHub](https://github.com/DFIR-ORC/dfir-orc) 上找到
* [FastIR Collector](https://github.com/SekoiaLab/Fastir_Collector) - FastIR Collector 在 Windows 系统中实时收集各种信息并将结果记录在 CSV 文件中，通过对这些信息的分析，我们可以发现早期的入侵痕迹
* [Fibratus](https://github.com/rabbitstack/fibratus) - 探索与跟踪 Windows 内核的工具
* [Hoarder](https://github.com/muteb/Hoarder) - 为数字取证或事件响应调查收集有价值数据的工具
* [IREC](https://binalyze.com/products/irec-free/) - 免费、高效、易用的集成 IR 证据收集工具，可收集内存映像、$MFT、事件日志、WMI 脚本、注册表，系统还原点等
* [Invoke-LiveResponse](https://github.com/mgreen27/Invoke-LiveResponse) - Invoke-LiveResponse 是用于证据收集的实时响应工具
* [IOC Finder](https://www.fireeye.com/services/freeware/ioc-finder.html) - IOC Finder 是由 Mandiant 开发的免费工具，用来收集主机数据并报告存在危险的 IOC，仅支持 Windows。不再维护，仅支持 Windows 7/Windows Server 2008 R2
* [IRTriage](https://github.com/AJMartel/IRTriage) - 用于数字取证的 Windows 证据收集工具
* [KAPE](https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape) - Kroll Artifact Parser and Extractor (KAPE) 解析工具
* [LOKI](https://github.com/Neo23x0/Loki) - Loki 是一个使用 YARA 与其他 IOC 对终端进行扫描的免费 IR 扫描器
* [MEERKAT](https://github.com/TonyPhipps/Meerkat) - 适用于 Windows 的、基于 PowerShell 的分类和威胁狩猎工具
* [Panorama](https://github.com/AlmCo/Panorama) - Windows 系统运行时的快速事件概览
* [PowerForensics](https://github.com/Invoke-IR/PowerForensics) - PowerShell 开发的实时硬盘取证框架
* [PSRecon](https://github.com/gfoss/PSRecon/) - PSRecon 使用 PowerShell 在远程 Windows 主机上提取/整理数据，并将数据发送到安全团队，数据可以通过邮件来传送数据或者在本地留存
* [RegRipper](https://github.com/keydet89/RegRipper3.0) - Regripper 是用 Perl 编写的开源工具，可以从注册表中提取/解析数据(键\值\数据)提供分析