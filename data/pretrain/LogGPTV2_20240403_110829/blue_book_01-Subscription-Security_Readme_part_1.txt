## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
# AzSK Subscription Security Package
![Subscription_Security](../Images/Subscription_Security.png)
### Contents:
### [AzSK: Subscription Health Scan](Readme.md#azsk-subscription-health-scan-1)
- [Overview](Readme.md#overview)
- [Scan the security health of your subscription](Readme.md#scan-the-security-health-of-your-subscription)
- [Subscription Health Scan - What is covered?](Readme.md#subscription-health-scan---what-is-covered)
- [Subscription Health Scan - How to fix findings?](Readme.md#subscription-health-scan---how-to-fix-findings)
- [Target specific controls during a subscription health scan](Readme.md#target-specific-controls-during-a-subscription-health-scan)
- [FAQs](Readme.md#faqs)
### [AzSK: Subscription Security Provisioning](Readme.md#azsk-subscription-security-provisioning-1)
- [Overview](Readme.md#overview-1)
- [Provision security for your subscription](Readme.md#provision-security-for-your-subscription)
- [Remove previously provisioned security settings from your subscription](Readme.md#remove-azsk-subscription-security-provisioning-from-your-subscription)
- [FAQs](Readme.md#faqs-1)
### [AzSK: Subscription Access Control Provisioning](Readme.md#azsk-subscription-access-control-provisioning)
- [Overview](Readme.md#overview-2)
- [Setup pre-approved mandatory accounts](Readme.md#setup-pre-approved-mandatory-accounts)
- [Remove pre-approved mandatory accounts](Readme.md#remove-previously-provisioned-accounts)
### [AzSK: Subscription Activity Alerts](Readme.md#azsk-subscription-activity-alerts-1)
- [Overview](Readme.md#overview-3)
- [Configure alerts in your subscription](Readme.md#configure-alerts-for-your-subscription)
- [Remove previously configured alerts from your subscription](Readme.md#remove-previously-configured-alerts-from-your-subscription)
- [Configure alerts scoped to specific resource groups](Readme.md#configure-alerts-scoped-to-specific-resource-groups)
- [FAQs](Readme.md#faqs-2)
### [AzSK: Azure Security Center (ASC) configuration](Readme.md#azsk-azure-security-center-asc-configuration-1)
- [Setup Azure Security Center (ASC) on your subscription](Readme.md#setup-azure-security-center-asc-on-your-subscription)
### [AzSK: Subscription Security - ARM Policy](Readme.md#azsk-subscription-security---arm-policy-1)
- [Overview](Readme.md#overview-4)
- [Setup ARM policies for your subscription](Readme.md#setup-arm-policies-on-your-subscription)
- [Remove ARM policies from your subscription](Readme.md#remove-arm-policies-from-your-subscription)
- [FAQs](Readme.md#faqs-3)
### [AzSK: Update subscription security baseline configuration](Readme.md#azsk-update-subscription-security-baseline-configuration-1)
- [Update subscription security baseline configuration](Readme.md#update-subscription-security-baseline-configuration)
### [AzSK support for Azure Government and Azure China](Readme.md#azsk-support-for-azure-government-and-azure-china-1)
- [Spotcheck/Manual Scans](Readme.md#spotcheckmanual-scans)
- [CICD](Readme.md#cicd)
- [CA](Readme.md#ca)
- [Customizing AzSK for your organization](Readme.md#customizing-azsk-for-your-organization)
### [AzSK: Privileged Identity Management (PIM) helper cmdlets](Readme.md#azsk-privileged-identity-management-pim-helper-cmdlets-1)
- [Get-AzSKPIMConfiguration at Subscription scope](Readme.md#use-get-azskpimconfiguration-alias-getpim-for-querying-various-pim-settingsstatus-at-subscription-scope)
- [Set-AzSKPIMConfiguration at Subscription scope](Readme.md#use-set-azskpimconfiguration-alias-setpim-for-configuringchanging-pim-settings-at-subscription-scope)
- [Get-AzSKPIMConfiguration at Management Group scope](Readme.md#use-get-azskpimconfiguration-alias-getpim-for-querying-various-pim-settingsstatus-at-management-group-level)
- [Set-AzSKPIMConfiguration at Management Group scope](Readme.md#use-set-azskpimconfiguration-alias-setpim-for-configuringchanging-pim-settings-at-management-group-level)
----------------------------------------------------------
## AzSK: Subscription Health Scan
### Overview
The subscription health check script runs a set of automated scans to examine a subscription and flags 
off conditions that are indications that your subscription may be at a higher risk due to various security 
issues, misconfigurations or obsolete artifacts/settings. 
The following aspects of security are checked:
1. 	 Access control configuration - identity and access management related issues in the subscription
2. 	 Alert configuration - configuration of activity alerts for sensitive actions for the subscription and various cloud resources
3. 	 Azure Security Center configuration - configuration of ASC (security point of contact, various ASC policy settings, etc.)
4. 	 ARM Policy and Resource Locks configuration - presence of desired set of ARM policy rules and resource locks. 
[Back to top…](Readme.md#contents)
### Scan the security health of your subscription 
The subscription health check script can be run using the command below after replacing ` 
 with your subscriptionId
```PowerShell
Get-AzSKSubscriptionSecurityStatus -SubscriptionId 
```
The parameters used are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription 
You need to have at least **Reader** role at the subscription scope to run this command. 
If you also have access to read the Graph in your tenant, the RBAC information and checking will be richer.
> **Note**: The check for presence of Management Certificates cannot be performed just with "Reader" privilege. 
> This check only works if you are running as a Co-Administrator. This is in itself a bad practice. Hence, in most
> situations, the user running the subscription health check will likely not be a co-admin and, because we will not be
> able to actually perform the check, the outcome of this control will be listed as 'Manual'.
>
> In general, in any scenario where the runtime account used to run an AzSK cmdlet does not have enough access to evaluate
> a control, the evaluation status is marked as "Manual" in the report. Basically, for such controls, someone with the
> correct access needs to manually verify the control and record the information through the "Control Attestation" feature.
> A common situation for this is in respect to "Graph Access" which is not available by default to SPNs.
[Back to top…](Readme.md#contents)
### Subscription Health Scan - What is covered?  
The various security checks performed by the health check script are listed in the table [here](../02-Secure-Development/ControlCoverage/Feature/SubscriptionCore.md). 
The next section explains how to interpret output in the LOG file and how to address control failures.
[Back to top…](Readme.md#contents)
### Subscription Health Scan - How to fix findings?
All cmdlets in AzSK generate outputs which are organized as under: 
- summary information of the control evaluation (pass/fail) status in a CSV file, 
- detailed control evaluation log in a LOG file and
- a few other ancillary files for additional support
The overall layout and files in the output folder are also described in the README.txt file present in the root output folder.
To address findings, you should do the following:
1. See the summary of control evaluation first in the CSV file. (Open the CSV in XLS. Use "Format as Table", "Hide Columns", "Filter", etc.)
2. Review controls that are marked as "Failed", "Verify" or "Manual"
3. The 'Recommendation' column for each control in the XLS will tell you the command/steps needed to resolve the issue.
4. The LOG file contains details about *why* AzSK has flagged each control as "Failed" or "Verify".
5. Use the following approach based on control status:
    - For "Failed" controls, look at the LOG file and use the Recommendation field to address the issue. (e.g., If the 'external accounts (LiveId)' control
has failed, the list of such external accounts found is displayed in the LOG file. Remove these using
the cmdlet mentioned in the Recommendation field.)
    - For "Verify" controls, look at the LOG file to get the supporting information that should help you to decide whether to consider
the control as "Passed" or not. (e.g., For an RBAC control, you should look at the actual list of users and confirm that it is appropriate. 
Then use the "Control Attestation" feature to record your attestation.)
    - For "Manual" controls, follow the steps using the Recommendation field in the CSV. (There will not be anything in the LOG file for "Manual" controls.) 
For provisioning related failures (e.g., you don't have central accounts correctly configured), you should use the
corresponding provisioning cmdlet as described in respective sections below. (E.g., `Set-AzSKSubscriptionRBAC` for
provisioning mandatory accounts).
[Back to top…](Readme.md#contents)
### Target specific controls during a subscription health scan
The subscription health check supports multiple parameters as specified below:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription 
- FilterTags  - Comma-separated tags to filter the security controls. E.g., RBAC, SOX, AuthN, etc.
- ExcludeTags - Comma-separated tags to exclude the security controls. E.g., RBAC, SOX, AuthN, etc.
- ControlIds  - Comma-separated AzSK control id's to filter security controls. E.g., Azure_Subscription_AuthZ_Limit_Admin_Owner_Count, Azure_Subscription_Config_Azure_Security_Center, etc.
```PowerShell
Get-AzSKSubscriptionSecurityStatus -SubscriptionId  [-ControlIds ] [-FilterTags ] [-ExcludeTags ]
```
These different parameters would enable you to execute different 'flavors' of subscription health scan. 
For example, they will let you scan only SOX relevant controls or AuthZ related controls or 
exclude best practices or even execute one specific control. 
Here are some examples:
1. Execute only SOX related controls
```PowerShell
Get-AzSKSubscriptionSecurityStatus -SubscriptionId  -FilterTags "SOX"
``` 
2. Exclude *Best-Practice* while doing *AuthZ* related subscription health scan
```PowerShell
Get-AzSKSubscriptionSecurityStatus -SubscriptionId  -FilterTags "AuthZ" -ExcludeTags "Best Practice"
``` 
3. Execute ASC related security control of subscription health scan 
```PowerShell
Get-AzSKSubscriptionSecurityStatus -SubscriptionId  -ControlIds Azure_Subscription_Config_Azure_Security_Center
``` 
|List of Tags|Purpose|
|-------|-------|
|Access|Access activities|
|ACLS|Access control activities|
|AppService|Azure App Services|
|Audit|Audit activities|
|AuthN|Authentication activities|
|AuthZ|Authorization activities|
|Automated|Controls which are automated by AzSK|
|Availability|Availability|
|BCDR|Backup and disaster recovery|
|Best Practice|Controls which should be implemented to ensure your application security|
|Classic|Classic services|
|Config|Configurations|
|Deploy|Deployment activities|
|Diagnostics|Diagnostics activities|
|DP|Data protection|
|FunctionApp|Azure FunctionApp|
|Information|Controls which are default behaviour by Azure but additional check for notification|
|KeyRotation|Key rotation|
|KeySecretPermissions|Controls which can be attested only when the user has access permissions on the concerned keys and secrets|
|Linux|Linux virtual machine|
|Manual|Controls which are not automated and user need to verify it manually|
|NetSec|Network security|
|OwnerAccess|Controls which require owner/co-admin permission to get required output|
|RBAC|Role based access controls|
|SDL|Software development lifecycle |
|SecIntell|Security intellisense |
|SI|System integrity |
|SOX|Controls which are enforced by SOX|
|SqlDatabase|Azure SQL Database|
|TCP|Controls which must be implemented to ensure your application security|
|Windows|Windows virtual machine|
[Back to top…](Readme.md#contents)
-----------------------------------------------------------------------  
## AzSK: Subscription Security Provisioning
### Overview
The Subscription Security Provisioning script is a master script that, in turn, invokes multiple other 
scripts to setup up all of the following in the target subscription:
- A set of mandatory accounts that are required for central scanning/audit/compliance functions.
- A group of subscription and resource activity alerts for activities with significant security implications.
- A baseline set of ARM policies corresponding to certain actions that are considered insecure.
- Default enterprise policy settings for Azure Security Center (ASC).
- Security contact information in ASC.
[Back to top…](Readme.md#contents)
### Provision security for your subscription
The Subscription Security setup script can be run by providing the subscriptionID, security contact 
E-mails (comma separated values) and a contact phone number.
```PowerShell
Set-AzSKSubscriptionSecurity -SubscriptionId  -SecurityContactEmails  -SecurityPhoneNumber 
```
|Config Param Name	|Purpose	|
| --------------- | -------- |
|SecurityContactEmails 	|Comma-separated list of emails (e.g., 'PI:EMAIL, PI:EMAIL')	for contact preference|
|SecurityPhoneNumber 	|Single phone number (e.g., '425-882-8080' or '+91-98765-43210' or '+1-425-882-8080')	for contact preference|
> **Note**: 
>  - This command *overwrites* the contact emails and phone number previously configured in Azure Security Center.
>  - This command also helps you to recover if any of the base resources are accidentally deleted, like AzSK resource group, storage account, attestation container, continuous assurance log container etc.
While running command, you may see message that configuration in your subscription is already up to date. This indicates your subscription already have latest security configurations. If you still see any failures for controls in `Get-AzSKSubscriptionSecurityStatus` command, you can pass `-Force` parameter to the provisioning script and reconfigure AzSK artifacts (
Alerts, RBAC, ARM policies, etc.) in the subscription. 
[Back to top…](Readme.md#contents)
### Remove AzSK subscription security provisioning from your subscription
The subscription setup created by the provisioning command can be removed by running:
```PowerShell
Remove-AzSKSubscriptionSecurity -SubscriptionId  -Tags 
```
This command cleans up various security provisioning that was previously done using the Set-AzSKSubscriptionSecurity 
command such as alerts, access control (RBAC) settings, ARM policies, etc.
This command does not affect the Azure Security Center related settings (whether they were previously configured
by AzSK or directly by the user).
To remove access control related configuration, it is mandatory to use the `-Tags` parameter. If this
parameter is not specified, previously setup RBAC will not be deprovisioned will be done. 
Typically you would want to specify the tags which were used when setting up RBAC. If you did not specify 
any tags during provisioning then, by default, only the accounts marked as 'Mandatory' would get provisioned. Typically, you should not have
to remove those accounts but if you must you can do so using `-Tags "Mandatory"` in the command.
[Back to top…](Readme.md#contents)
### FAQs
#### Is it possible to setup an individual feature (e.g., just alerts or just ARM Policy)?
Yes, each of the components of the overall subscription provisioning setup can be individually 
run/controlled. 
You can run cmdlets in isolation for the following:
1. RBAC roles/permissions - Set-AzSKSubscriptionRBAC
2. Alerts - Set-AzSKAlerts
3. ARM Policy - Set-AzSKARMPolicies
4. Azure Security Center configuration - Set-AzSKAzureSecurityCenterPolicies
#### Set-AzSKSubscriptionSecurity  or Set-AzSKAzureSecurityCenterPolicies returns - InvalidOperation: The remote server returned an error: (500) Internal Server Error
Currently we are seeing an issue with an Azure Security Center API which is causing the error you are seeing. You can follow the steps below until the issue is resolved:
1. Login to your subscription.
2. Go to 'Security Center' > 'Security policy'.
3. Select your subscription and click on 'Edit settings'.
4. Select 'Email notifications'.
5. Update 'Security contact emails' and 'Phone number'.
6. Click on 'Save'.
You can try running the recommendation command again after doing the above change.
[Back to top…](Readme.md#contents)
------------------------------------------------------------
## AzSK: Subscription Access Control Provisioning
### Overview
The subscription access control provisioning script will setup certain permissions in the subscription 