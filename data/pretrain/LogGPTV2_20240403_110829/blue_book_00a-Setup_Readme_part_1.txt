## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
------------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
# Installation Guide
> IMPORTANT: If you are from CSE, please install the AzSK via instructions at https://aka.ms/devopskit/onboarding so that CSE-specific policies are configured for your installation. Do not use the installation instructions on this page.
  AzSK 3.0.x ** -->
>**Pre-requisites**:
> - PowerShell 5.0 or higher. 
> - Windows OS
1. First verify that prerequisites are already installed:  
    Ensure that you are using Windows OS and have PowerShell version 5.0 or higher by typing **$PSVersionTable** in the PowerShell ISE console window and looking at the PSVersion in the output as shown below.) 
 If the PSVersion is older than 5.0, update PowerShell from [here](https://www.microsoft.com/en-us/download/details.aspx?id=54616).  
   ![PowerShell Version](../Images/00_PS_Version.PNG)   
2. Install the Secure DevOps Kit for Azure (AzSK) PS module:  
```PowerShell
  Install-Module AzSK -Scope CurrentUser
```
Note: 
You may need to use `-AllowClobber` and `-Force` options with the Install-Module command 
above if you have a different version of Az modules installed on your machine. 
AzSK depends on specific version of different Az service modules and installs that during the installation above.
Run command 'Find-Module AzSK -includedependencies' to see all dependencies. 
In version 3.6.x, if you are facing issue during scan, you may have to register "Microsoft.Security" and "Microsoft.PolicyInsights" providers on subscriptions. Refer [link](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-supported-services#portal) for provider registration.
------------------------------------------------
### Backward compatibility
As Azure features evolve and add more security controls, "Secure DevOps Kit for Azure" also evolves every month respecting the latest security features.
It is always recommended to run on the latest DevOps kit module to scan your subscription with the latest rules. 
Users who are still using older modules of DevOps kit continue to work only until N-2 version w.r.t production version e.g. If the current production version is 3.11.x, 
then teams can continue to use 3.9.x and 3.10.x. As the version 3.12.x becomes available, automatically 3.9.x would stop working. 
More details on how it impacts each stage of DevOps kit are shared below:
**Adhoc Scans:**
Users running the DevOps kit scan using N-3 version from their local machine, will start getting an error asking to upgrade as shown below:
![Install_OlderVersionWarning](../Images/00_Install_OlderVersionWarning.PNG) 
> **Note:** This restriction has been put in place from AzSDK version 2.8.x and applicable for all future releases.
**Continuous Assurance(CA) Scans:**
No impact to CA as it would automatically upgrade to latest version. 
Before every scan it checks whether there has been a latest release of the DevOps kit and upgrade itself.
All the further scans would happen using the latest version.
**AzSK CICD Extension:**
No impact to default behavior of CICD. It always runs the scan with the latest version available in the PS Gallery. 
If teams have overridden the default behavior by specifying a version number during the build, then the same restriction of N-2 applies here as well.
### Auto Update
It is always recommended to scan your subscription with the latest DevOps kit module, thus ensuring to evaluate latest security controls that are available through the module.
"Secure DevOps Kit for Azure" module provides different auto update capabilities w.r.t different stages of devops. More details are below:
**Adhoc Scans:**
Users running the older version of AzSK scan from their local machine will get a warning as shown in the image below.
It would also provide the user with required instructions to upgrade the module.
![Install_Autoupdate](../Images/00_Install_Autoupdate.PNG) 
In a scenario where an organization has setup its own instance of "Secure DevOps Kit for Azure", the users can leverage 
the auto update feature which has been introduced from the AzSDK version 2.8.x.
As shown in the image above, user can either sign up for Autoupdate or go with manual update by running the command below:
```PowerShell
  Set-AzSKPolicySettings -AutoUpdate On|Off
```
User needs to close and reopen a fresh session once the command is run.
Going forward, if the latest version of DevOps kit is released, then during execution of any DevOps kit command it would start the auto update workflow automatically 
as shown in the image below:
![Install_Autoupdate_Workflow](../Images/00_Install_Autoupdate_Workflow.PNG)
Step 1: It would take user consent before it starts the auto update workflow. (1 in the image above) 
Step 2: Users need to close all the displayed PS sessions. Typically open PS sessions would lock the module and fail the installation. (2 in the image above) 
Step 3: Even the current session must be closed. It would again take the user consent before it starts the auto update flow to avoid the loss of any unsaved work. (3 in the image above) 
**Continuous Assurance(CA) Scans:**
The DevOps kit module running the scans through CA, auto updates itself. Every scan would initially check if any new version has been released and auto-upgrade the installed module to the latest version.
No action is required from the user.
Users can also run the command below to confirm the same:
```PowerShell
  Get-AzSKContinuousAssurance -SubscriptionId ''
```
**AzSK CICD Extension**
AzSK CICD extension will always run the scan using latest module of AzSK from the gallery. This is the default behavior in the case of both hosted and non-hosted agents. 
You could find more details about CICD [here](../03-Security-In-CICD/Readme.md).
------------------------------------------------
### FAQs
#### Getting exception: Package 'Az.Accounts' failed to be installed because End of Central Directory record could not be found.
Recently we have seen some users are facing issue during installation of latest AzSK module from PSGallery. AzSK is mainly dependant on Az module versions and its failing to install specific versions. We are investigating more on issue. You can use below method to install module from AzSK repository.
```PowerShell
$AzSKModuleRepoPath = "https://azsdkossep.azureedge.net/3.7.0/AzSK.zip"
#Copy module zip to temp location
$CopyFolderPath = $env:temp + "\AzSKTemp\"
if(-not (Test-Path -Path $CopyFolderPath))
{
  mkdir -Path $CopyFolderPath -Force | Out-Null
}
$ModuleFilePath = $CopyFolderPath + "AzSK.zip"           
Invoke-WebRequest -Uri $AzSKModuleRepoPath -OutFile $ModuleFilePath
#Extract zip file to module location
Expand-Archive -Path $ModuleFilePath -DestinationPath "$Env:USERPROFILE\documents\WindowsPowerShell\modules" -Force