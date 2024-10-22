## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
>NOTE:  
>The OMS* parameter/variable names will soon be deprecated. Please ensure that you have made the necessary changes to CA, CICD and AzSK Monitoring Solution as per below:  
>	1. Updated CA setups with new names ([details here](../04-Continous-Assurance#updating-an-existing-continuous-assurance-setup)). (Not required for CSEO subscriptions!)  
>	2. Switched to new names in CICD extension ([details here](../03-Security-In-CICD#advanced-cicd-scanning-capabilities)). (Required for all subscriptions)  
>	3. Start using the new parameters for [CA](../04-Continous-Assurance#setting-up-continuous-assurance---step-by-step) and [AzSK Monitoring Solution](../05-Alerting-and-Monitoring#1-c).
# Continuous Assurance (CA)
![Continous_Assurance](../Images/Continous_Assurance.png)
## Baseline Continuous Assurance
### Contents
- [Overview](Readme.md#overview)
- [Setting up Continuous Assurance - Step by Step](Readme.md#setting-up-continuous-assurance---step-by-step)
- [Continuous Assurance - how it works (under the covers)](Readme.md#continuous-assurance---how-it-works-under-the-covers)
- [Updating an existing Continuous Assurance setup](Readme.md#updating-an-existing-continuous-assurance-setup)
- [Removing a Continuous Assurance setup](Readme.md#removing-a-continuous-assurance-setup)
- [Getting details about a Continuous Assurance setup](Readme.md#getting-details-about-a-continuous-assurance-setup)
- [Continuous Assurance (CA) - 'Central Scan' mode](Readme.md#continuous-assurance-ca---central-scan-mode)
- [Continuous Assurance (CA) - Trigger scan on resource deployment (Preview)](Readme.md#continuous-assurance-ca---scanondeployment-mode)
- [Scan Databricks using custom AzSK Job](Readme.md#scan-databricks-using-custom-azsk-job)
- [FAQ](Readme.md#faq)
-----------------------------------------------------------------
## Overview 
The basic idea behind Continuous Assurance (CA) is to setup the ability to check for "drift" from what is 
considered a secure snapshot of a system. Support for Continuous Assurance lets us treat security truly as 
a 'state' as opposed to a 'point in time' achievement. This is particularly important in today's context 
when 'continuous change' has become a norm.
There can be two types of drift:        
1. Drift involving 'baseline' configuration:
This involves settings that have a fixed number of possible states (often pre-defined/statically determined 
ones). For instance, a SQL DB can have TDE encryption turned ON or OFF…or a Storage Account may have 
auditing turned ON however the log retention period may be less than 365 days. 	 
2. Drift involving 'stateful' configuration: There are settings which cannot be constrained within a finite 
set of well-known states. For instance, the IP addresses configured to have access to a SQL DB can be any (arbitrary) set of IP addresses. In such scenarios, usually human judgment is initially required to determine whether a particular configuration should be considered 'secure' or not. However, once that is done, it is important to ensure that there is no "stateful drift" from the attested configuration. (E.g., if, in a troubleshooting session, someone adds the IP address of a developer machine to the list, the Continuous Assurance feature should be able to identify the drift and generate notifications/alerts or even trigger 'auto-remediation' depending on the severity of the change). 
Besides 'drift tracking' there are also two other aspects of "staying secure" in operations. First of them 
is the simple concept that if new, more secure options become available for a feature, it should be possible to detect that 
a particular application or solution can benefit from them and notify/alert the owners concerned. In a way this can be thought 
of as facilitating "positive" security drift. The other aspect is about supporting "operational hygiene". In this area, 
we will add the ability to remind an app team about the security hygiene tasks that they need to periodically 
perform (key rotation, access reviews,  removing inactive/dormant power users, etc.). These two capabilities are on our backlog for H1-FY18.
>**Note:** If you have already installed Continuous Assurance using a version prior to 2.2.0, 
you should run 'Install-AzSKContinuousAssurance' command again by following the steps in the next section.
[Back to top…](Readme.md#contents)
## Setting up Continuous Assurance - Step by Step
In this section, we will walk through the steps of setting up a subscription and application(s) for Continuous Assurance coverage. 
To get started, we need the following:
1. The user setting up Continuous Assurance needs to have 'Owner' access to the subscription. (This is necessary because during setup, 
AzSK adds the service principal runtime account as a 'Reader' to the subscription.) 
>**Note:**  Starting AzSK v3.15.0, users having 'Contributor' permissions can set up AzSK Continuous Assurance (CA) for the subscription. The part of the setup where 'Owner' access is required will not abort if the user does not have that permission any more... instead, it will print a warning and ask the user to ensure that the required permissions are granted by someone (else) with 'Owner' access for the CA SPN (that does is used for the runtime scanning). Note that the CA SPN requires 'Reader' permission on the subscription and 'Contributor' permission on the DevOps Kit resource group in the subscription. CA will work seamlessly so long as these permissions are assigned (soon after the install cmdlet) by the owner.
2. Target Log Analytics WorkspaceID* and SharedKey. (The Log Analytics workspace can be in a different subscription, see note below)
**Prerequisite:**
**1.** We currently support following OS options: 	
- Windows 10
- Windows Server 2016
> **\*Note** CA leverages Azure Monitor repository for aggregating security scan results, you must determine which Log Analytics workspace 
you will use to view the security state of your subscription and applications (If you don't have a Log Analytics workspace please 
follow the steps in [Setting up the AzSK Monitoring Solution](../05-Alerting-and-Monitoring/Readme.md#setting-up-the-azsk-monitoring-solution-step-by-step). 
This can be a single workspace that is shared by multiple applications which may themselves be in different subscriptions. 
Alternately, you can have a Log Analytics workspace that is dedicated to monitoring a single application as well. 
(Ideally, you should use the same workspace that is being used to monitor other aspects like availability, performance, etc. 
for your application.)
**Step-1: Setup**  
0. Setup the latest version of the AzSK following the installation instructions for your organization. (For CSE use https://aka.ms/devopskit/onboarding).
1. Open the PowerShell ISE and login to your Azure account (using **Connect-AzAccount**).  
2. Run the '**Install-AzSKContinuousAssurance**' command with required parameters given in below table. 
```PowerShell
	Install-AzSKContinuousAssurance -SubscriptionId  `
		[-AutomationAccountLocation ] `
		[-AutomationAccountRGName ] `
		[-AutomationAccountName ] `
	        -ResourceGroupNames  `
	        -LAWSId  `
	        -LAWSSharedKey  `
	        [-AltLAWSId ] `
	        [-AltLAWSSharedKey ] `
	        [-WebhookUrl ] `
	        [-WebhookAuthZHeaderName ] `
	        [-WebhookAuthZHeaderValue ] `
	        [-ScanIntervalInHours ] `
	        [-AzureADAppName ]
```
Here is one basic example of continuous assurnace setup command:
```PowerShell
	Install-AzSKContinuousAssurance -SubscriptionId  `
	        -ResourceGroupNames ‘rgName1, rgName2,…etc.’ ` # You can also use “*” to specify all RGs
	        -LAWSId  `
	        -LAWSSharedKey  
```
Note:
For Azure environments other than Azure Cloud, don't forget to provide AutomationAccountLocation as the default value won't work in those environments.
|Param Name|Purpose|Required?|Default value|Comments|
|----|----|----|----|----|
|SubscriptionId|Subscription ID of the Azure subscription in which an Automation Account for Continuous Assurance will be created |TRUE|None||
|AutomationAccountLocation|(Optional) The location in which this cmdlet creates the Automation Account|FALSE|EastUS2|To obtain valid locations, use the Get-AzLocation cmdlet|
|AutomationAccountRGName|(Optional) Name of ResourceGroup where Automation Account will be installed|FALSE|AzSKRG|Don't pass default value explicitly for this param|
|AutomationAccountName|(Optional) Name of AutomationAccount|FALSE|AzSKContinuousAssurance|Don't pass default value explicitly for this param|
|ResourceGroupNames|Comma-separated list of resource group names which cover the application resources that need to be scanned. |TRUE|None|Use **"*"** to cover all resource groups in the subscription.|
|LAWSId|Workspace ID of Log Analytics workspace which is used to monitor security scan results|TRUE|None||
|LAWSSharedKey|Shared key of Log Analytics workspace which is used to monitor security scan results|TRUE|None||
|AltLAWSId|(Optional) Workspace ID of alternate Log Analytics workspace to monitor security scan results|FALSE|None||
|AltLAWSSharedKey|(Optional) Shared key of alternate Log Analytics workspace which is used to monitor security scan results|FALSE|None||
|WebhookUrl|(Optional) All the scan results shall be posted to this configured webhook |FALSE|None||
|WebhookAuthZHeaderName|(Optional) Name of the AuthZ header (typically 'Authorization')|FALSE|None||
|WebhookAuthZHeaderValue|(Optional) Value of the AuthZ header |FALSE|None||
|ScanIntervalInHours|(Optional) Overrides the default scan interval (24hrs) with the custom provided value |FALSE|None||
|AzureADAppName|(Optional) Name for the Azure Active Directory(AD) Application that will be created in the subscription for running the runbooks. |FALSE|None||
|ScanOnDeployment|(Optional) CA scan can be auto-triggered upon resource deployment.Installing CA with this flag will make sure that the Resource Group in which resource is deployed will be scanned. |FALSE|None||
|UsageTelemetryLevel|(Optional) CA scan evets get captured at AzSK side using anonymous telemetry.Installing CA with this flag with value as None will disable scan telemetry being captured at AzSk side. |FALSE|Anonymous||
> NOTE:  
> You can use **"*"** to cover all resource groups in the subscription. If **"*"** is specified, CA will automatically cover new resource groups that are added. Thus **"*"** might be a preferred option in enterprise-wide compliance/visibility initiatives based on CA.
**More about the 'AzureADAppName' parameter:**
The AzureADAppName parameter is optional. This represents the runtime account that will be used by the
CA runbook to scan the subscription/resources. 
- If the user does not specify a parameter, then CA will: 
    - Find if there is an existing AAD app (from a previous attempt to setup CA) in the subscription that can be reused.
    - Else, create a fresh Azure AD app on behalf of the user (in this case the user must have permission to create apps in the tenant).
- If the user specifies an AzureADAppName, then CA will try to find the AAD application corresponding to that 
name and attempt to use it (in this case the user must have 'Owner' permission on the specified app name). 
Here's a quick summary of the permissions required for the user who sets up CA:
- "Owner" access on the subscription
- Ability to create an AAD app in the tenant (This permissions is only required if app does not exist in tenant)
- "Owner" access to the AAD app if the user specifies one (or CA internally finds a previously created one)
**Note-1**: Completion of this one-time setup activity can take up to 2 hours. (This is because one of the things that setup does 
is download and add PowerShell modules for Azure PS library and for AzSK. This is a slow and sometimes flaky process and, 
as a result, the setup internally retries failed downloads. The Azure Automation product team is aware of this challenge and are working on a resolution.)
**Note-2**: Due to the complexity of various dependent activities involved, there are multiple places where CA setup can run into issues. 
It is important to verify that everything has worked without hiccups. Please review and ascertain each of the "Verifying" steps below carefully.
**Note-3**: If the person who had set up CA leaves organization/team then it's strongly advised to remove the service principal (configured in runtime account) access from subscription/AzSKRG to prevent any misuse.
**Step-2: Verifying that CA Setup is complete**  
**1:** In the Azure portal, select the application subscription that was used above and search for resources of type Automation Account. You should see an Automation Account created by the name 'AzSKContinuousAssurance'. Clicking on it will display the contents of the Automation Account (something that looks like the below, the counts shown may vary a little):
 ![04_CA_Overview_Screen](../Images/04_CA_Overview_Screen.PNG)
**2:** Click on 'Runbooks' tile. It should show the following runbook: 
 ![04_CA_RunBooks](../Images/04_CA_RunBooks.PNG)
**3:** Click on 'Schedules' tile. It should show the scheduling details of runbook. You can change the schedule timings according to your need. Default schedule is created as below. First job will run ten minutes after the installation: 
 ![04_CA_Schedule](../Images/04_CA_Schedule.PNG)
**4:** Click on 'Run As Accounts' tile. It should show the following account:
 ![04_CA_Run_as_Account](../Images/04_CA_Run_as_Account.PNG)
**Step-3: Verifying that all required modules are downloaded successfully (after about two hours of starting the installation)**
**1**: Click on the 'Modules' tile for the Automation Account. 'AzSK' module should be listed there. 'Status' column value for all modules should be 'Available' as below.
 ![04_CA_Downloaded_Modules](../Images/04_CA_Downloaded_Modules.PNG)
**Step-4: Verifying CA Runbook execution and Log Analytics connectivity**  
Once CA setup and modules download are completed successfully, the runbooks will automatically execute periodically (once a day) and scan the subscription and the specified resource groups for the application(s) for security issues. The outcomes of these scans will get stored in a storage account created by the installation (format : azsk\ e.g. azsk20170505181008) and follows a similar structure as followed by standalone SVT execution (CSV file, LOG file, etc.).    
The results of the control evaluation are also routed to the Log Analytics for viewing via a security dashboard.  
Let us verify that the runbook output is generated as expected and that the Log Analytics connectivity is setup and working correctly.
**1:** Verify that CSV file and LOG file are getting generated as expected.  
1. Go to Storage Explorer and look for a storage account with a name in azsk format in your subscription in 'AzSKRG' resource group.
2. Find a blob container called 'ca-scan-logs' in this storage account.
3. There should be a ZIP file named using a timestamp based on the date time for the manual execution in this container (most likely the ZIP file with the most recent creation date). 
4. Download the ZIP file and extract its contents locally. The folder structure will be similar to how SVTs/Subscription Health scan generate when run locally. 
5. In a single zip file you will find two folders (name format: Timestamp). One folder contains reports of Subscription Health scan and another folder contains reports of application(s) resource groups security scan.
 ![04_CA_Storage_Container](../Images/04_CA_Storage_Container.PNG)
**2:** Verify that data is being sent to the target Log Analytics workspace   
1. Go to the Log Analytics workspace that we used to setup CA above.
2. Navigate to 'Logs' window, and enter Type=AzSK_CL Source_s=CA. (Source_s used to be 'CC' in the past.)
3. You should see results similar to the below:
 ![04_CA_Log_Analytics](../Images/04_CA_Log_Analytics.png)
Once CA is setup in the subscription, an app team can start leveraging the Monitoring Solution from AzSK as a one-stop dashboard 
for visibility of security state. Please follow the steps to setup the Monitoring solution [here](../05-Alerting-and-Monitoring#setting-up-the-azsk-monitoring-solution-step-by-step) to enable that part.
[Back to top…](Readme.md#contents)
## Continuous Assurance - how it works (under the covers)
The CA feature is about tracking configuration drift. This is achieved by enabling support for running AzSK 
SVTs/SS-Health via automation runbook. 
The CA installation script that sets up CA creates the following resources in your subscription:
- Resource group (Name : AzSKRG) :- 