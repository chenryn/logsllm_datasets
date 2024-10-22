that enable central security and compliance teams to perform automated scans and manual review/assessment 
activities in the subscription. This basically involves addition of some common accounts (service principals 
or security groups) to one or more roles in the subscription. The script also supports provisioning of 
some optional accounts based on the scenarios that the subscription is used for. (The specific accounts
and the roles they are deployed into are configurable by the central security team in your organization.) 
[Back to top…](Readme.md#contents)
### Setup pre-approved mandatory accounts
The subscription access control provisioning script can be run using the following command (by specifying 
the subscriptionId for the subscription in which you want to provision the various roles):
```PowerShell
Set-AzSKSubscriptionRBAC -SubscriptionId  
```
The subscription access control provisioning script ensures that certain central accounts and roles are 
setup in your subscription.
[Back to top…](Readme.md#contents)
### Remove previously provisioned accounts
The Remove-AzSKSubscriptionRBAC command can be used to remove access control (RBAC) settings that were
previously provisioned using AzSK.
To remove access control related configuration, use the '-Tags' parameter. If this
parameter is not specified, only the deprecated accounts will be deleted from the subscription. Typically you would want to specify
the tags which were used when setting up RBAC. If you did not specify any tags during provisioning then,
by default, only the accounts marked as 'Mandatory' would get provisioned. Typically, you should not have
to remove those accounts but if you must you can do so using '-Tags "Mandatory"' in the command.
Run the below command with the subscriptionId which you want to remove RBAC accounts from:
```PowerShell
Remove-AzSKSubscriptionRBAC -SubscriptionId  [-Tags ]
```		
[Back to top…](Readme.md#contents)
----------------------------------------------------------
## AzSK: Subscription Activity Alerts
#### Subscription Activity Alerts (based on Azure Insights)
> **Note**: The alerts setup covered on this page uses the native 'Insights-based' alerts mechanism 
offered by the Azure PG. In the 'Alerting & Monitoring' section, we also cover support for Log Analytics-based 
alerts which enable similar scenarios (and more). We have found that both approaches are in use across 
LoB application teams.
### Overview
This module helps setup and manage subscription and resource activity-based alerts in your Azure subscription. These alerts can be configured against actions that get recorded in Azure Audit Logs. These activity logs are natively generated upon resource activity by various ARM-based log providers (which are typically correspond to the different resource types in Azure). 
It is important to understand the concept of 'control plane' and 'data plane' in order to follow exactly which type of activities get covered by these alerts. In the ARM-model for Azure, everything that you can create from a subscription (at the portal or from PS) is considered a 'resource'. Various activities performed on these resources that you can do using the ARM APIs generate activity logs. For e.g., you can change the replication type of a storage account or you can set the size of an availability set, etc. These activities are usually considered 'control plane' activities. However, there are a set of activities that can happen "inside" the resource. For e.g., if you have a VM, you could log in to it as an Admin and add someone as a Guest user. Or just create a new folder under "C:\windows". These actions are usually considered 'data plane'. Insights-based alerts don't directly support alerting on 'data plane' actions. As is evident, each type of resource (VM, SQL Server, ADLS, etc.) will have their own ways of generating 'data plane' activity so alerting from that layer is usually very specific to each resource type. (Events from the 'data plane' are sometimes called 'Diagnostic Logs' whereas events from the 'control plane' are called 'Activity Logs'.)
In the context of this script, we have triaged the 200 or so activities that generate activity log entries and distilled them down to a subset that can be of interest to security. That subset was further triaged into Critical, High, Medium and Low severity alerts.
The basic script flow configures these alerts after taking an email id as input. After the alerts are setup, whenever a particular activity happens (e.g., adding a new person in the "Owners" group or modifying user defined routes on a virtual network), the configured email ID receives an email notification.  
[Back to top…](Readme.md#contents)
### Configure alerts for your subscription
You can setup alerts for a subscription using the following command:
```PowerShell
Set-AzSKAlerts -SubscriptionId  -SecurityContactEmails  [-SecurityPhoneNumbers ]
```
As noted above, by default alerts are configured for activities that are deemed to be Critical or High in severity by AzSK.
|Config Param Name	|Purpose	|Comments|
| ----------------  | --------- | ------ |
|SubscriptionId 	|Subscription ID against which the alerts would be setup| |
|SecurityContactEmails	|Email address of Security Point of Contact, can be a mail enabled security group or a distribution list |PI:EMAIL, PI:EMAIL|
|SecurityPhoneNumbers	|Phone numbers of Security Point of Contact, provide contact no. with country code.|'+91-98765-43210' or '+1-425-882-8080'|
[Back to top…](Readme.md#contents)
### Remove previously configured alerts from your subscription
- Steps to remove all the alerts configured by AzSK:  
Run the below command:
```PowerShell
Remove-AzSKAlerts -SubscriptionId  -Tags 
```
|Config Param Name	|Purpose	|
| ----------------  | --------- | 
|SubscriptionID	|Subscription ID against which these alerts would be setup|
|Tags |Comma-separated alert tag names which needs to be removed, supported tag names "Optional","Mandatory","SMS"|
For e.g., to remove only optional alerts, run following command:
```PowerShell
Remove-AzSKAlerts -SubscriptionId  -Tags "Optional"
```
**Note**: This command cleans up all alerts in the resource group 'AzSKRG' with matched tag. This resource group is used internally as a container for AzSK objects. As a result, it is advisable to not add other alerts (or other types of resources) to this RG.
[Back to top…](Readme.md#contents)
### FAQs
#### Can I get the alert emails to go to a distribution group instead of an individual email id?
Yes it is possible. While setting up the alerts you are asked to provide the SecurityContactEmails. It supports individual point of contact or mail enabled security group or a distribution list.  
#### How can I find out more once I receive an alert email?
You should visit portal with the details data provided in the Alert Email. For example, you could visit the resource id and look for the action that has been called out in the email, or to get more details about the alert, visit the Activity Log in the portal and look for this resource type, you should find more details on the action performed.  
**Note:** 
These alerts template and the generation is completely controlled through Azure Application Insights framework. 
#### Is there a record maintained of the alerts that have fired?
You could run the below command to check the alerts raised on the subscription.
```PowerShell
Get-AzLog | where {$_.OperationName -eq "Microsoft.Insights/AlertRules/Activated/Action"}
```  
#### Troubleshooting
|Error Description	|Comments|
| --------------  | ------- |
|Error: Please enter valid subscription id!|	Provided subscription id is incorrect|
|Error Occurred! Try running the command with -Debug option for more details. |Failed to setup the policy. Share the details of the errors to PI:EMAIL|
[Back to top…](Readme.md#contents)
----------------------------------------------------------
## AzSK: Azure Security Center (ASC) configuration
### Setup Azure Security Center (ASC) on your subscription
The Set-AzSKAzureSecurityCenterPolicies provisions the following for Azure Security Center (ASC) configuration:
1. Configure Azure Security Center by enabling all the required policies and rules.
2. Configure email address and phone number for contact preferences.
3. Enable automatic provisioning for the subscription.
**Prerequisites:**
1. You need to be owner on the subscription which you want to onboard on to ASC.
2. Ensure you have the latest AzSK modules installed.
**Steps to onboard onto ASC:**
1. Open PowerShell under non admin mode.
2. Login into your Azure Account using Connect-AzAccount.
3. Run the below command with the subscriptionId on which you want to configure Azure Security Center.
```PowerShell
Set-AzSKAzureSecurityCenterPolicies -SubscriptionId  `
        -SecurityContactEmails  `
        -SecurityPhoneNumber  `
        [-OptionalPolicies]
```
|Config Param Name	|Purpose	|
| --------------- | -------- |
|SubscriptionId 	|Subscription ID against which ASC would be setup	|
|SecurityContactEmails 	|Comma-separated list of emails (e.g., 'PI:EMAIL, PI:EMAIL')	for contact preference|
|SecurityPhoneNumber 	|Single phone number (e.g., '425-882-8080' or '+91-98765-43210' or '+1-425-882-8080')	for contact preference|
|OptionalPolicies       |Switch to enable policies which are marked as optional|
This command will *overwrite* the contact emails and contact phone previously set in Azure Security Center. Here is the [list](../01-Subscription-Security/ASCPoliciesCoverage.md) of all the policies (both mandatory & optional) that are enabled via this command.
>**Note:** The Get-AzSKSubscriptionSecurityStatus cmdlet can be used to check Azure Security Center settings (amongst other things). That script checks for the following w.r.t. Azure Security Center: 
>1.  All ASC policies are configured per expectation.
>2. There are no pending ASC tasks.
>3. There are no pending ASC recommendations.  
(Presence of either of Tasks/Recommendations indicates that there are some security issues that need attention.)  
[Back to top…](Readme.md#contents)  
----------------------------------------------------------
## AzSK: Subscription Security - ARM Policy
### Overview
The native ARM Policy feature in Azure can be used control access to resources by explicitly auditing or denying access to certain operations on them. The ARM Policy setup script in the AzSK uses this feature to define and deploy some broadly applicable security policies in the subscription. By using the setup script (either standalone or through the overall Provisioning script), you can be assured that the subscription is compliant with respect to the core set of policies expected to be in place by AzSK.
[Back to top…](Readme.md#contents)
### Setup ARM policies on your subscription
You can install the ARM policies via the Set-AzSKARMPolicies cmdlet as below:
1. Login to your Azure Subscription using below command
```PowerShell
Connect-AzAccount
```
2. Once you have installed the AzSK, you should be able to run the below command
```PowerShell
Set-AzSKARMPolicies -SubscriptionId 
```
|Config Param Name	|Purpose	|
| --------------- | -------- |
|SubscriptionId 	|Subscription ID against which these alerts would be setup	|
[Back to top…](Readme.md#contents)
### Remove ARM policies from your subscription
Use the following command to remove the ARM policies setup via the AzSK 
```PowerShell
Remove-AzSKARMPolicies -subscriptionId  -Tags 
```
You can also use native Azure PS commands to do the same. Refer to this MSDN [article](https://msdn.microsoft.com/en-us/library/mt652489.aspx) for more details.
[Back to top…](Readme.md#contents)
### FAQs
#### What happens if an action in the subscription violates the policy?
Currently "effect" parameter of all the AzSK policies is configured as "audit". So, in the event of policy violation, it would generate an audit log entry. You should watch for these policy violation audit events in the Azure audit log.
#### Which ARM policies are installed by the setup script?
The ARM policy configuration script currently enables the policies (Refer the list [here](../02-Secure-Development/ControlCoverage/Feature/ARMPolicyList.md)) in the subscription. Note that the policy level is currently set to 'Audit'.  
>Policy definitions exist in the JSON file at this location: 
 C:\Users\SampleUser\Documents\WindowsPowerShell\Modules\AzSK\\\\Framework\Configurations\SubscriptionSecurity\Subscription.ARMPolicies.json
#### How can I check for policy violations? 
You could run the below command to check for the policy violations on the subscription. By default this shows the violations for the last one hour. Other intervals can be specified.
```PowerShell
Get-AzLog | where {$_.OperationName -eq "Microsoft.Authorization/policies/audit/action"} 
```
Refer to this [MSDN article](https://azure.microsoft.com/en-in/documentation/articles/resource-manager-policy/#policy-audit-events) for more details
#### Are there more policies available for use?
We have covered for the below resource types so far:
- Azure SQL DB
- Azure Storage
- Scheduler Service
- Usage of classic (v1/non-ARM) resources
 More policies will be added in upcoming releases.
#### Troubleshooting
|Error Description	|Comments|
| ----------------- |--------|
|Error: Please enter valid subscription id! |Provided subscription id is incorrect|
|Error Occurred! Try running the command with -Debug option for more details.	|Failed to setup the policy. Share the details of the errors to PI:EMAIL |
Reach out to PI:EMAIL for any further help  
[Back to top…](Readme.md#contents)
## AzSK: Update subscription security baseline configuration 
### Update subscription security baseline configuration
AzSK team is constantly improving subscription security capabilities so it is possible that newer AzSK version has enhanced baselines for ASC, Alerts, ARM policies, CA runbook etc. This is where below command can help you to update your baseline configuration for different features (ARM Policies, Alerts, ASC, Access control, Continuous Assurance runbook).  
```PowerShell
Update-AzSKSubscriptionSecurity -SubscriptionId 
```
|Config Param Name	|Purpose	|
| --------------- | -------- |
|SubscriptionId 	|Subscription for which AzSK subscription security baseline would be upgraded	|
> **Note**: 
>  - This command is useful only for updating AzSK subscription security baseline. If you have never setup baseline, then you can set it up using Set-AzSKSubscriptionSecurity command.
>  - This command also helps you to recover if any of the base resources are accidentally deleted, like AzSK resource group, storage account, attestation container, continuous assurance log container etc.
[Back to top…](Readme.md#contents)
## AzSK support for Azure Government and Azure China
>**Pre-requisites**:
> - AzSK version 3.8.0 or above.
From release 3.8.0, AzSK has started supporting a few core scenarios for Azure Government and Azure China environments. Please follow the steps as under to use AzSK in those environments.
### Spotcheck/Manual Scans:
Follow the steps below to successfully run the local AzSK scans (GRS, GSS and other commands):
1. Follow instructions in our [installation guide](../00a-Setup#installation-guide) to download the latest version of AzSK (3.9.0 or above).
2. Configure AzSK for your Azure environment using the following command:
```PowerShell
Set-AzSKPolicySettings -AzureEnvironment ''
```   
```PowerShell
E.g., Set-AzSKPolicySettings -AzureEnvironment AzureUSGovernment 
```   
Once you have run through the steps above, any AzSK commands you run will start targeting the configured Azure cloud environment. 
Notes:
  * When no specific environment is configured (as in Step-2 above), AzSK assume AzureCloud as the default environment.
  * If you have access to multiple Azure environments and need to switch from one to the other (e.g., AzurePublic to AzureChina) then you can use the  Clear-AzSKSessionState command after running Step-2. This will cause AzSK to reload the newly configured environment.
### CICD:
To use the CICD extension, no special steps are required beyond those outlined in the AzSK CICD extensions [doc](../03-Security-In-CICD#contents).
### CA:
Once you have run through the steps outlined in the 'Spotcheck/Manual' section, You can easily use AzSK Continuous Assurance. Click [here](/04-Continous-Assurance#continuous-assurance-ca) for more details on Continuous Assurance.
Please refer [this](../04-Continous-Assurance/Readme.md#setting-up-continuous-assurance---step-by-step) set up CA. As Azure Government and Azure China are limited to particular location, provide 'AutomationAccountLocation' parameter because the default value is EastUS2.
```PowerShell
E.g., Install-AzSKContinuousAssurance -SubscriptionId  `
		    -AutomationAccountLocation "USGov Virginia" `                    (for Azure Government)
	        -ResourceGroupNames  `
	        -LAWSId  `
	        -LAWSSharedKey  
```
### Customizing AzSK for your organization: