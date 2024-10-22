## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
# Customizing AzSK for your organization
### [Overview](Readme.md#Overview-1)
 - [When and why should I set up org policy?](Readme.md#when-and-why-should-i-setup-org-policy)
 - [How does AzSK use online policy?](Readme.md#how-does-azsk-use-online-policy)
### [Setting up org policy](Readme.md#setting-up-org-policy-1)
 - [What happens during org policy setup?](Readme.md#what-happens-during-org-policy-setup)
 - [The org policy setup command: Install-AzSKOrganizationPolicy](Readme.md#the-org-policy-setup-command-install-azskorganizationpolicy)
 - [First-time policy setup - an example](Readme.md#first-time-policy-setup---an-example)
### [Consuming custom org policy](Readme.md#consuming-custom-org-policy-1)
 - [Running scan in local machine with org policy](Readme.md#1-running-scan-in-local-machine-with-custom-org-policy)
 - [Setup Continuous Assurance](Readme.md#2-setup-continuous-assurance)
 - [Using CICD Extension with org-policy](Readme.md#3-using-cicd-extension-with-custom-org-policy)
### [Modifying and customizing org policy](Readme.md#modifying-and-customizing-org-policy-1)
 - [Getting Started](Readme.md#getting-started)
 - [Basic scenarios for org policy customization](Readme.md#basic-scenarios-for-org-policy-customization) 
      - [Changing the default 'Running AzSK using…' message](Readme.md#a-changing-the-default-running-azsk-using-message)
      - [Changing control setting](Readme.md#b-changing-a-control-setting-for-specific-controls)
      - [Customizing specific controls for a service SVT](Readme.md#c-customizing-specific-controls-for-a-service)
      - [Setting up and updating baselines for your org](Readme.md#d-creating-a-custom-control-baseline-for-your-org)
      - [Customizing severity labels](Readme.md#e-customizing-severity-labels)
### [Managing policy/advanced policy usage ](Readme.md#managing-policyadvanced-policy-usage)
- [Downloading and examining policy folder](Readme.md#downloading-and-examining-policy-folder)
- [Working with ‘local’ mode (policy dev-test-debug)](Readme.md#working-with-local-mode-policy-dev-test-debug)
- [How to upgrade org version to latest AzSK version](Readme.md#how-to-upgrade-org-azsk-version-to-the-latest-azsk-version)
   - [Upgrade scenarios in different scan sources(SDL/CA/CICD)](Readme.md#upgrade-scenarios-in-different-scan-sources)
- [Maintaining policy in source-control](Readme.md#maintaining-policy-in-source-control)
- [Policy deployment using CICD pipeline](Readme.md#policy-deployment-using-cicd-pipeline)
### [Create compliance and monitoring solutions](Readme.md#create-security-compliance-monitoring-solutions)
- [Create cloud security compliance report for your org in PowerBI](Readme.md#create-cloud-security-compliance-report-for-your-org-using-powerbi)
- [AzSK org health monitoring dashboard](Readme.md#azsk-org-health-monitoring-dashboard)
- [Detail resource inventory dashboard](Readme.md#detail-resource-inventory-dashboard)
### [Compliance notifications](Readme.md#compliance-notifications-1)
- [Create compliance notification to subscription owners](Readme.md#compliance-notification-to-subscription-owners)
### [Advanced scenarios for org policy customization/extending AzSK](Readme.md#advanced-usage-of-org-policy-extending-azsk) 
- [SVT customization](Readme.md#customizing-the-svts)
   - [Update/extend existing control by augmenting logic](./Extending%20AzSK%20Module/Readme.md#steps-to-override-the-logic-of-existing-svt)
   - [Add new control for existing GSS/GRS SVT](./Extending%20AzSK%20Module/Readme.md#steps-to-extend-the-control-svt)
   - [Add new SVT altogether (non-existing SVT)](./Extending%20AzSK%20Module/Readme.md#steps-to-add-a-new-svt-to-the-azsk-module)
- [Subscription security provisioning](Readme.md#customizing-subscription-security)
   - [ARM policy](Readme.md#arm-policy)
   - [Alert set](Readme.md#alert-set)
   - [Security center configurations](Readme.md#security-center-configurations)
   - [Mandatory/deprecated RBAC list](Readme.md#rbac-mandatorydeprecated-lists)
- [ARM checker policy customization](Readme.md#arm-checker-policy-customization)
- [Scenarios for modifying scanagent](Readme.md#scenarios-for-modifying-scanagent)
   - [Scanning only baseline controls using continuous assurance setup](Readme.md#scanning-only-baseline-controls-using-continuous-assurance-setup)
   - [Scanning admin and graph access controls using CA](Readme.md#scanning-owner-and-graph-access-controls-using-ca)
   - [Reporting critical alerts](#reporting-critical-alerts)
- [Change default resource group name (AzSKRG) and location (EastUS2) created for AzSK components](Readme.md#change-default-resource-group-name-(AzSKRG)-and-location-(EastUS2)-created-for-AzSK-components)
### [Org policy usage statistics and monitoring using telemetry](Readme.md#org-policy-usage-statistics-and-monitoring-using-telemetry-1)
### [Troubleshooting common issues](Readme.md#testing-and-troubleshooting-org-policy-1)
### [Frequently Asked Questions](Readme.md#frequently-asked-questions)
----------------------------------------------------------------
## Overview
#### When and why should I setup org policy
When you run any scan command from the AzSK, it relies on JSON-based policy files to determine various 
parameters that effect the behavior of the command it is about to run. These policy files are downloaded 'on the fly' from a policy 
server. When you run the public version of the toolkit, the policy files are accessed from a CDN endpoint 
that is managed by the AzSK team. Thus, whenever you run a scan from a vanilla installation, 
AzSK accesses the CDN endpoint to get the latest policy configuration and runs the scan using 
it. 
The JSON inside the policy files dictate the behavior of the security scan. 
This includes things such as:
 - Which set of controls to evaluate?
 - What control set to use as a baseline?
 - What settings/values to use for individual controls? 
 - What messages to display for recommendations? Etc.
Note that the policy files needed for security scans are downloaded into each PS session for **all** 
AzSK scenarios. That is, apart from manually-run scans from your desktop, this same behavior happens 
if you include the AzSK SVTs Release Task in your CICD pipeline or if you setup Continuous Assurance. 
Also, the AzSK policy files on the CDN are based on what we use internally in Core Services Engineering and Operations
(CSEO) at Microsoft. We also keep them up to date from one release to next.
 While the out-of-box files on CDN may be good for limited use, in many contexts you may want to "customize" 
the behavior of the security scans for your environment. You may want to do things such as: (a) enable/disable 
some controls, (b) change control settings to better match specific security policies within your org, 
(c) change various messages, (d) add additional filter criteria for certain regulatory requirements that teams 
in your org can leverage, etc. When faced with such a need, you need a way to create and manage 
a dedicated policy endpoint customized to the needs of your environment. The organization policy setup feature 
helps you do that in an automated fashion. 
In this document, we will look at how to setup an organization-specific policy endpoint, how to make changes 
to and manage the policy files and how to accomplish various common org-specific policy/behavior customizations 
for the AzSK.
#### How does AzSK use online policy?
Let us look at how policy files are leveraged in a little more detail. 
When you install AzSK, it downloads the latest AzSK module from the PS Gallery. Along with this module there
is an *offline* set of policy files that go in a sub-folder under the %userprofile%\documents\WindowsPowerShell\Modules\AzSK\ folder. 
It also places (or updates) an AzSKSettings.JSON file in your %LocalAppData%\Microsoft\AzSK folder that contains the policy endpoint (or policy server) URL that is used by all local commands. 
Whenever any command is run, AzSK uses the policy server URL to access the policy endpoint. It first downloads 
a 'metadata' file that contains information about what other files are available on the policy server. After 
that, whenever AzSK needs a specific policy file to actually perform a scan, it loads the local copy of 
the policy file into memory and 'overlays' any settings *if* the corresponding file was also found on the 
server-side. 
It then accesses the policy to download a 'metadata' file that helps it determine the actual policy files list 
that is present on the server. Thereafter, the scan runs by overlaying the settings obtained from the server with 
the ones that are available in the local installation module folder. This means that if there hasn't been anything 
overridden for a specific feature (e.g., Storage), then it won't find a policy file for that listed in the server
 metadata file and the local policy file for that feature will get used. 
The image below shows this flow with inline explanations: 
## Setting up org policy
#### What happens during org policy setup?
At a high level, the org policy setup support for AzSK does the following:
 - Sets up a storage account to hold various policy artifacts in the subscription you want to use for hosting 
your policy endpoint. (This should be a secure, limited-access subscription to be used only for managing your 
org's AzSK policy.)
 - Uploads the minimum set of policy files required to bootstrap your policy server.
 - Sets up an Application Insights telemetry account in the subscription so as to facilitate visibility of control 
scan/telemetry events in your central subscription. (This is where control 'pass/fail' events will get sent when other 
people in the org start using the version of AzSK customized for your org.)
 - Creates a special folder (or uses one specified by you) for storing a local copy of all customizations made to policy.
 - Creates an org-specific (customized) installer that others in your org will use to install and configure the AzSK 
per your org's policy.
Let us now look at the command that will help with the above and a few examples…
#### The org policy setup command (`Install-AzSKOrganizationPolicy`)
This command helps the central security team of an organization to customize the behavior of various functions
and security controls checked by AzSK.  
As discussed in previous sections, AzSK runtime behavior is mainly controlled through JSON-based policy files 
which have a predefined schema. The command helps in creating a policy store and other required components to
host and maintain a custom set of policy files that override the default AzSK behavior. 
| Parameter| Description | Required? | Default Value | Comments |
| ---- | ---- | ---- |----|---- |
| SubscriptionId | Subscription ID of the Azure subscription in which organization policy store will be created. | Yes | None | 
|OrgName | The name of your organization. The value will be used to generate names of Azure resources being created as part of policy setup. This should be alphanumeric. | Yes | None |
| DepartmentName | The name of a department in your organization. If provided, this value is concatenated to the org name parameter. This should be alphanumeric. | No | None |
| PolicyFolderPath | The local folder in which the policy files capturing org-specific changes will be stored for reference. This location can be used to manage policy files. | No | User Desktop |
| ResourceGroupLocation | The location in which the Azure resources for hosting the policy will be created. | No | EastUS2 | To obtain valid locations, use Get-AzLocation cmdlet |
| ResourceGroupName | Resource Group name where policy resources will be created. | No | AzSK-\-\-RG | Custom resource group name for storing policy resources. **Note:** ResourceGroupName, StorageAccountName and AppInsightName must be passed together to create custom resources. The same parameters must be used to update org policy. |
| StorageAccountName | Name for policy storage account | No | azsk-\-\-sa | |
| AppInsightName | Name for application insight resource where telemetry data will be pushed | No | AzSK-\--AppInsight |   |
| AppInsightLocation | The location in which the AppInsightLocation resource will be created. | No | EastUS |  |
#### First-time policy setup - an example
The following example will set up policies for IT department of Contoso organization.  
You must be an 'Owner' or 'Contributor' for the subscription in which you want to host your org's policy artifacts.
Also, make sure that that the org name and dept name are purely alphanumeric and their combined length is less than 19 characters. The policy setup command is fairly lightweight - both in terms of effort/time and in terms of costs incurred.
```PowerShell
Install-AzSKOrganizationPolicy -SubscriptionId  `
           -OrgName "Contoso" `
           -DepartmentName "IT" `
           -PolicyFolderPath "D:\ContosoPolicies"
```
> **Note:** For Azure environments other than Azure Cloud (like Azure Gov, China etc.), don't forget to provide ResourceGroupLocation as the default value won't work in those environments.
The execution of command will create following resources in the subscription (if they don't already exist): 
1. Resource Group (AzSK-Contoso-IT-RG) - AzSK-\-\-RG. 
2. Storage Account (azskcontosoitsa) - azsk\\sa.
3. Application Insight (AzSK-Contoso-IT-AppInsight) - AzSK-\-\-AppInsight.
4. Monitoring dashboard (DevOpsKitMonitoring (DevOps Kit Monitoring Dashboard [Contoso-IT])) 
> **Note:** You must not have any other resources than created by setup command in org policy resource group.
It will also create a very basic 'customized' policy involving below files uploaded to the policy storage account.
##### Basic files setup during Policy Setup 
| File | Container | Description  
| ---- | ---- | ---- |
| AzSK-EasyInstaller.ps1 | installer | Org-specific installation script. This installer will ensure that anyone who installs AzSK using your 'iwr' command not only gets the core AzSK module but their local installation of AzSK is also configured to use org-specific policy settings (e.g., policy server URL, telemetry key, etc.) **IMPORTANT:** Make sure anyone in your org who needs to scan according to your policies uses the above 'iwr' command to install AzSK. (They should not use 'install-module AzSK' directly. Anyone using an incorrect setup will not get your custom policy when they run any AzSK cmdlet. |
| AzSK.Pre.json | policies  | This file contains a setting that controls/defines the AzSK version that is 'in effect' at an organization. An org can use this file to specify the specific version of AzSK that will get used in SDL/CICD/CA scenarios at the org for people who have used the org-specific 'iwr' to install and configure AzSK.   **Note:** During first time policy setup, this value is set with AzSK version available on the client machine that was used for policy creation. Whenever a new AzSK version is released, the org policy owner should update the AzSK version in this file with the latest released version after performing any compatibility tests in a test setup. You can get notified of new releases by following the AzSK module in PowerShell Gallery or release notes section [here](https://azsk.azurewebsites.net/ReleaseNotes/LatestReleaseNotes.html).  
| RunbookCoreSetup.ps1 | policies  | Used in Continuous Assurance to setup AzSK module
| RunbookScanAgent.ps1 | policies  | Used in Continuous Assurance to run daily scan 
| AzSk.json | policies | Includes org-specific message, telemetry key, InstallationCommand, CASetupRunbookURL etc.
| ServerConfigMetadata.json | policies | Index file with list of policy files.  
Output of command looks like below 
If you note section 3 of the command output , an 'iwr' command line is printed to the console. This command leverages the org-specific
 installation script from the storage account for installing AzSK. You can run this IWR followed by some scan commands (GSS/GRS) to see org policy in effect in your dev box.
```PowerShell
#IWR to install org specific configurations
iwr 'https://azskcontosoitsa.blob.core.windows.net/installer/AzSK-EasyInstaller.ps1' -UseBasicParsing | iex
#Subscription Scan with org policy
Get-AzSKSubscriptionSecurityStatus -SubscriptionId 
```
 Output:
## Next Steps:
Once your org policy is setup, all scenarios/use cases of AzSK should work seamlessly with your org policy server
as the policy endpoint for your org (instead of the default CDN endpoint). Basically, you should be able to do one 
or more of the following using AzSK:
 - People will be able to install AzSK using your special org-specific installer (the 'iwr' install command)
 - Developers will be able to run manual scans for security of their subscriptions and resources (GRS, GSS commands)
 - Teams will be able to configure the AzSK SVT release task in their CICD pipelines
 - Subscription owners will be able to setup Continuous Assurance (CA) from their local machines (**after** they've installed
 AzSK using your org-specific 'iwr' installer locally)
 - Monitoring teams will be able to setup AzSK Log Analytics view and see scan results from CA (and also manual scans and CICD if configured) 
 - You will be able to do central governance for your org by leveraging telemetry events that will collect in the master subscription
 from all the AzSK activity across your org. 
## Consuming custom org policy
Running scan with custom org policy is supported from all three avenues of AzSK viz. local scan (SDL), continuous assurance setup and CICD SVT task. Follow the steps below for the same:
### 1. Running scan in local machine with custom org policy
 To run scan with custom org policy from any machine, get IWR cmdlet from org policy owner. This IWR is generated at the time of policy setup (IOP) or policy update (UOP) in the following format
```PowerShell
#Sample IWR to install org specific configurations
iwr 'https://azskcontosoitsa.blob.core.windows.net/installer/AzSK-EasyInstaller.ps1' -UseBasicParsing | iex
#Run subscription scan cmdlet and validate if it is running with org policy
Get-AzSKSubscriptionSecurityStatus -SubscriptionId 
```
This step is pre-requisite for the other two scan methods.
### 2. Setup Continuous Assurance
Setting up CA with org policy is pretty simple. Once you have followed the first step i.e. running iwr in local machine, you can run CA setup with the help of doc [here](https://github.com/azsk/DevOpsKit-docs/blob/master/04-Continous-Assurance/Readme.md#setting-up-continuous-assurance---step-by-step). 
CA setup command will refer policy setting from your local machine and configure it in automation runbook.
For existing CA, you just need to run *Update-AzSKContinuousAssurance* in your local.
You can validate if CA is running with custom org policy, via the options below:
   Option 1:
   Go to central CA resource group --> automation account --> Jobs --> Open one of the completed jobs --> It prints initials of PolicyStoreURL (Policy Store URL is nothing but org policy storage account blob url)
   ![AzSK org policy check using runbook ](../Images/07_OrgPolicy_CA_PolicyCheck-0.PNG)
   Option 2:
   i) Download latest AzSK Scan logs stored in storage account (inside AzSKRG) 
   ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-1.PNG)
   ii) Open PowerShellOutput.log file under etc folder and validate policy name
   ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-2.PNG)
   Option 3:
   Go to Log Analytics workspace which was configured during CA setup and execute below query
   ```AI Query
   AzSK_CL | where Source_s == "CA" |  summarize arg_max(TimeGenerated,*) by SubscriptionId  | project SubscriptionId,PolicyOrgName_s | render table
   ```
   It will show the subscriptions running with org policy in a table as depicted below:
   ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-3.PNG)
### 3. Using CICD Extension with custom org policy
To set up CICD when using custom org policy, please follow below steps: