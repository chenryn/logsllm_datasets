## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
# Getting started with the Secure DevOps Kit for Azure!
If you have just installed the Secure DevOps Kit for Azure (a.k.a. AzSK) and are not familiar with 
its functionality, then you can get started with the 2 most basic use cases of AzSK by going through 
the following getting started guides:
- [Scan the security of your subscription](GettingStarted_SubscriptionSecurity.md)
- [Scan the security of your cloud application](GettingStarted_AzureServiceSecurity.md)  
Thereafter, you can explore individual features further using the table of contents below which has 
pointers to full help on individual features by feature area.
> **Note:** If you have not installed the DevOps Kit yet, follow the instructions in the [installation guide](../00a-Setup/Readme.md) and then come back here.
> **PowerShell Tips for AzSK:** 
> If you are new to PowerShell, then you will find several useful tips in our [PowerShell tips for new AzSK Users](GettingStarted_PowerShellTipsAzSK.md) guide 
> handy to accelerate your initial learning curve for PowerShell competencies needed to use AzSK effectively.
The overall set of features in the Secure DevOps Kit for Azure are organized by the 6 areas as shown 
in the table below:  
|Feature Area | Secure DevOps Kit Feature|
|-------------|--------------------------|
[Subscription Security](../01-Subscription-Security/Readme.md) | Subscription Security Health Check Subscription Provisioning Alerts Configuration   ARM Policy Configuration Azure Security Center (ASC) ConfigurationAccess control (RBAC) Hygiene   
[Secure Development](../02-Secure-Development/Readme.md) | Security Verification Tests (SVTs) Security IntelliSense VS Editor Extension 
[Security in CICD](../03-Security-In-CICD/Readme.md) | AzSK-SVTs VSTS extension for injecting security tests in a CICD pipeline 
[Continuous Assurance](../04-Continous-Assurance/Readme.md) | Security scanning of Azure subscription and applications via automation runbooks
[Alerting & Monitoring](../05-Alerting-and-Monitoring/Readme.md) | Leveraging Log Analytics towards:Single pane view of security across dev ops stagesSecurity alerts based on various search conditions.
[Cloud Risk Governance](../06-Security-Telemetry/Readme.md) | Support for control state attestation and security governance dashboards.  
## Complete list of AzSK commands
> **Note**: Most of the AzSK cmdlets support 3 letter acronyms (e.g., GRS, ICA, UCA, etc.). You can invoke cmdlets using these *after* AzSK has been imported in the session. So, to use any of these aliases, make sure you run 'ipmo AzSK' as the first thing in a new PS/ISE console window ('ipmo' itself is an alias for 'import-module'). Apart from cmdlets, parameters also have associated aliases. Those are documented in the individual cmdlet documentation. 
> For a quick reference on aliases, you can run 'get-alias | findstr -i AzSk' within a PS/ISE console after running 'ipmo AzSK'.
| Command (alias) | What it does |	Required Permission |
|----|----|-----|
|Clear-AzSKSessionState (CSS)|Command to clear AzSK session object|NA|
|Get-AzSKAzureServicesSecurityStatus (GRS)|Scans a set of RGs (or the entire subscription)|Reader on subscription or respective RGs|
|Get-AzSKContinuousAssurance (GCA)|Validates the status of Continuous Assurance automation account including the condition of various artifacts such as storage account, schedules, runbooks, SPN/connection, required modules, etc.|Reader on subscription.|
|Get-AzSKControlsStatus (GACS)|Single cmdlet that combines Get-AzSKSubscriptionSecurityStatus, Get-AzSKAzureServicesSecurityStatus|Union of permissions.|
|Get-AzSKExpressRouteNetworkSecurityStatus (GES)|Validate secure configuration of ER-connected vNets. Also validates custom/supporting protections |Reader on ERNetwork, Reader on sub.|
|Get-AzSKSubscriptionSecurityStatus (GSS)|Scans an Azure subscription for security best practices and configuration baselines for things such as alerts, ARM policy, RBAC, ASC, etc.|Reader on subscription|
|Get-AzSKSupportedResourceTypes (GSRT)|Lists the currently supported Azure service types in AzSK. Basically, all resources in this list have SVTs available and these SVTs will be invoked whenever Get-AzSKAzureServicesSecurityStatus is run.|NA.|
|Get-AzSKInfo (GAI)|This command would help users to get details of various components of AzSK. |Reader on subscription, Contributor on AzSKRG|
|Install-AzSKContinuousAssurance (ICA)|Sets up continuous assurance for a subscription. This creates various artifacts such as resource group, storage account and automation account| Owner on subscription.|
|Install-AzSKMonitoringSolution (IMS)|Creates and deploys a Log Analytics view in a subscription that has a Log Analytics workspace. The Log Analytics view provides visibility to application state across dev ops stages. It also creates alerts, common search queries, etc.	|Reader on subscription.|
|Remove-AzSKAlerts (RAL)|Removes the alerts configured by AzSK.|Owner on subscription.|
|Remove-AzSKARMPolicies (RAP)|Removes the ARM policy configured by AzSK.|Owner on subscription.|
|Remove-AzSKContinuousAssurance (RCA)|Removes the AzSK CA setup (including, optionally, the container being used for storing reports).|Reader on subscription.|
|Remove-AzSKSubscriptionRBAC (RRB)|Removes the RBAC setup by AzSK. By default "mandatory" central accounts are not removed and "deprecated" accounts are always removed.|Owner on subscription.|
|Remove-AzSKSubscriptionSecurity (RSS)|Removes the configuration done via Set-AzSKSubscriptionSecurity. It invokes the individual remove commands for RBAC, ARM policy, Alerts and ASC.|Owner on subscription.|
|Repair-AzSKAzureServicesSecurity (RRS)|Fixes the security controls for various Azure resources using the automated fixing scripts generated by running the AzSK scan command "Get-AzSKAzureServicesSecurityStatus" with the '-GenerateFixScript' flag.|Contributor on subscription or respective RGs |
|Repair-AzSKSubscriptionSecurity (RASS)|Fixes the subscription security related controls using the automated fixing scripts generated by running the AzSK scan command "Get-AzSKSubscriptionSecurityStatus" with the '-GenerateFixScript' flag.|Contributor on subscription|
|Set-AzSKAlerts (SAA)|Sets up activity alerts for the subscription. Includes alerts for subscription and resource specific activities. Alerts can be scopes to subscription or RGs.This is internally called by Set-AzSKSubscriptionSecurity.|Owner on subscription.
|Set-AzSKARMPolicies (SAP)|Sets up a core set of ARM policies in a subscription.This is internally called by Set-AzSKSubscriptionSecurity.|Owner on subscription.|
|Set-AzSKAzureSecurityCenterPolicies (SSC)|Sets up ASC policies and security points of contact. This is internally called by Set-AzSKSubscriptionSecurity.|Reader on subscription.|
|Set-AzSKEventHubSettings (SEHS)|Configures AzSK to send scan results to the provided EventHub. Currently available only in 'ad hoc' or 'SDL' mode.|NA|	
|Set-AzSKMonitoringSettings (SMS)|Configures AzSK to send scan results to the provided Log Analytics workspace. Events can be sent to Log Analytics from 'ad hoc'/SDL mode (via this configuration) or from CICD by specifying Log Analytics settings in a variable or from CA by specifying Log Analytics settings in the CA installation command.|Reader on subscription.|
|Set-AzSKPolicySettings (SPS)|Configures the server URL that is used by AzSK to download controls and config JSON. If this is not called, AzSK runs in an 'org-neutral' mode using a generic policy. Once this command is called, AzSK gets provisioned with the URL of a server/CDN where it can download control/config JSON from.|Reader on subscription.|
|Set-AzSKSubscriptionRBAC (SRB)|Sets up RBAC for a subscription. Configures "mandatory" accounts by default and function/scenario specific accounts if additional "tags" are provided.|Owner on subscription.|
|Set-AzSKSubscriptionSecurity (SSS)|Master command that takes combined inputs and invokes the individual setup commands for RBAC, ARM policy, Alerts and ASC.|Owner on subscription.|
|Set-AzSKUsageTelemetryLevel (SUTL)|Command to switch the default TM level for AzSK. The generic version of AzSK comes with 'Anonymous' level telemetry. The other levels supported is 'None'. |NA|	
|Set-AzSKLocalAIOrgTelemetrySettings (SLOTS)|Command to set local control telemetry settings. |NA|	
|Set-AzSKWebhookSettings (SWHS)|Configures AzSK to send scan results to the provided webhook. Currently available only in 'ad hoc' or 'SDL' mode.This capability can be used to receive AzSK scan results in arbitrary downstream systems. (E.g., Splunk)|NA|
|Set-AzSKUserPreference  (SUP)|This command is useful to set user preferences for AzSK commands. E.g. 1. Run 'Set-AzSKUserPreference -OutputFolderPath ' to override default path 2. Rn 'Set-AzSKUserPreference -DoNotOpenOutputFolder' to not open output folder by default.|NA|
|Install-AzSKOrganizationPolicy (IOP)|This command is intended to be used by central Organization team to setup Organization specific policies. |Contributor on subscription|
|Update-AzSKContinuousAssurance (UCA)|Updates various parameters that were used when CA was originally setup. This command can be used to change things like target resource groups that were scanned, Log Analytics workspaceID and sharedKey, run as account used by CA for scanning, update/renew certificate credential as run as account. | Owner on subscription.|
|Update-AzSKSubscriptionSecurity (USS)|This command can be used to update various security baseline elements and bring your subscription up to speed from a baseline policy compliance of subscription security controls. It updates one or more of the following elements after checking the ones that are out of date - alerts, Security Center, ARM policy, RBAC (mandatory accounts and deprecated accounts), continuous assurance runbook, etc.|Owner on subscription.|
|Update-AzSKOrganizationPolicy (UOP)|This command is intended to be used by central Organization team to update Organization specific policies. |Contributor on subscription|
## List of commonly used parameters
| Parameter (alias) |
|-------------------|
|SubscriptionId (s,sid)|
|ResourceGroupNames (rgns)|
|ResourceType (rt)|
|ResourceTypeName (rtn)|
|ResourceNames (rns)|
|ControlIds (cids)|
|ControlsToAttest (cta)|
|UseBaselineControls (ubc)|
## Some commonly used commands
```PowerShell 
grs -s  -rgns  -rns  -ubc 
```
```PowerShell  
gss -s  
```
```PowerShell  
ica -hsid  -rgns  -owid  -okey  
```
```PowerShell  
uca -hsid  
```
```PowerShell  
gacs -s  -rgns  -rns  -cids  
```
```PowerShell  
uss -s  -f -dnof 
```