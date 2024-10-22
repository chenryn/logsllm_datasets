## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
# Secure Development
![Secure_Development](../Images/Secure_Development.png)
### Contents
### [Security Verification Tests (SVT)](Readme.md#security-verification-tests-svt-1)
- [Overview](Readme.md#overview)
- [Execute SVTs for all controls in all resources in a given subscription](Readme.md#execute-svts-for-all-controls-of-all-resources-in-a-given-subscription)
- [Execute SVTs for specific resource groups (or tagged resources)](Readme.md#execute-svts-for-specific-resource-groups-or-tagged-resources)
- [Execute SVTs for a specific resource](Readme.md#execute-svts-for-a-specific-resource)
- [Execute SVTs for a specific resource type](Readme.md#execute-svts-for-a-specific-resource-type)
- [Execute SVTs in Baseline mode](Readme.md#execute-svts-in-baseline-mode) 
- [Execute SVTs using "-UsePartialCommits" switch](Readme.md#execute-svts-using--usepartialcommits-switch)
- [Execute SVT excluding some resource groups](Readme.md#execute-svts-excluding-some-resource-groups)
- [Execute SVT excluding some resources](Readme.md#execute-svts-excluding-some-resources)
- [Execute SVT excluding a resource type](Readme.md#execute-svts-excluding-a-resource-type)
- [Execute SVT excluding some controls from scan](Readme.md#execute-svts-excluding-some-controls-from-scan)
- [Generate FixScripts for controls that support AutoFix while executing SVTs](Readme.md#generate-fixscripts-for-controls-that-support-autofix-while-executing-svts)
- [Prevent the output folder from opening automatically at the end of SVTs](Readme.md#prevent-the-output-folder-from-opening-automatically-at-the-end-of-svts)
- [Understand the scan reports](Readme.md#understand-the-scan-reports)
- [Generate output report in PDF format](Readme.md#generate-output-report-in-pdf-format)
- [FAQs](Readme.md#faqs)
### [Express Route-connected Virtual Networks (ER-vNet)](Readme.md#express-route-connected-virtual-networks-er-vnet-1)
### [Security IntelliSense (Dev-SecIntel)](Readme.md#security-intellisense-dev-secintel-1)
#### [Basics](Readme.md#basics-1)
- [What is Security IntelliSense?](Readme.md#what-is-security-intellisense)
- [How do I enable Security IntelliSense on my dev box?](Readme.md#how-do-i-enable-security-intellisense-on-my-dev-box)
- [Is there a sample I can use to see how it works?](Readme.md#is-there-a-sample-i-can-use-to-see-how-it-works)
#### [Rules](Readme.md#rules)
- [What 'secure coding' rules are currently covered?](Readme.md#what-secure-coding-rules-are-currently-covered)
- [How are the rules updated? Do I need to refresh the plugin periodically?](Readme.md#how-are-the-rules-updated-do-i-need-to-refresh-the-plugin-periodically)
- [Can I add my own rules over and above the default set?](Readme.md#can-i-add-my-own-rules-over-and-above-the-default-set)
- [Can I 'mask' a particular rule or rules?](Readme.md#can-i-mask-a-particular-rule-or-rules)
- [Can I change the 'recommended' code for a rule?](Readme.md#can-i-change-the-recommended-code-for-a-rule-eg-i-want-to-recommend-gcm-instead-of-cbc-mode)
#### [Actions](Readme.md#actions-1)
- [What should I do to remove the extension?](Readme.md#what-should-i-do-to-remove-the-extension)
- [What default compiler actions are configured?](Readme.md#what-default-compiler-actions-are-configured)
- [Can I customize actions for my dev box / team? (E.g. change Error -> Warnings etc.)](Readme.md#can-i-customize-actions-for-my-dev-box--team-eg-change-error---warnings-etc)
-----------------------------------------------------------------
## Security Verification Tests (SVT)
>  **Prerequisites:**
> For all commands in this feature it is assumed that you have:
> 1. Logged in to your Azure account using Connect-AzAccount from a PowerShell ISE.
> 2. Selected a subscription using Set-AzContext.
### Overview
Security Verifications Tests (or SVTs) represent the core of security testing functionality of the 
AzSK. For all the prominent features in Azure (e.g., Web Apps, Storage, SQL DB, Key Vault, etc.), 
the AzSK can perform automated security checks against Azure resources of those types. 
These checks are based on security standards and best practices as applicable for sensitive corporate 
data at Microsoft. In general, these are likely to be applicable for most scenarios that involve 
processing sensitive data in other environments.
An SVT for a particular resource type basically examines a resource of that type within a specified 
resource group and runs a set of security control checks pertinent to that resource type. 
The outcome of the analysis is printed on the console during SVT execution and a CSV and a LOG file are 
also generated for subsequent use.
The CSV file and LOG file are generated under a subscription-specific sub-folder in the folder  
*%LOCALAPPDATA%\Microsoft\AzSKLogs\Sub_[yourSubscriptionName]*  
E.g.  
C:\Users\UserName\AppData\Local\Microsoft\AzSKLogs\Sub_[yourSubscriptionName]\20170331_142819
There are multiple ways that SVTs can be executed:
1. Scan all resources in a subscription. This is the simplest approach and simply enumerates 
all resources in a specific subscription and runs security checks against all the known resource 
types found.
2. Scan all resources in specific resource group(s). In this option, you can target resources
within one or more resource group. The AzSK simply enumerates all resources in the resource group(s) 
and runs security checks..
3. Scan a specific resource. In this approach, you can target a specific (individual) resource.
4. Scan a specific resource type. In this approach, you can target a specific resource type (e.g., Storage)
by specifying the 'resource type' value.
These options are described with examples below.  
[Back to top…](Readme.md#contents)
### Execute SVTs for all controls of all resources in a given subscription
The cmdlet below checks security control state and generates a status report of all Azure resources 
in a given subscription:  
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription.  
>**Note** Although this command is simple, it may take time proportionate to the number of 
>resources in your subscription and may not be ideal for 'shared' subscriptions. Typically, 
>you would want to scan a specific application (organized under one or more resource groups or 
>using tags). The subsequent options provide ability to narrow down the scope of the scan.
[Back to top…](Readme.md#contents)  
### Execute SVTs for specific resource groups (or tagged resources) 
The cmdlet below scans all Azure resources in the specified resource groups within a subscription and 
generates a status report:
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceGroupNames 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- ResourceGroupNames – Comma separated list of resource groups that hold related resources for an Azure subscription.
The cmdlet below scans all resources with specific tag names/values under a given subscription:  
1. Single Tag
```PowerShell
    Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -TagName  -TagValue 
```
2. Multiple Tags
```PowerShell
    Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -Tag 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- TagName – Key to identify the resources.
- TagValue – Value to identify the resources.
- Tag – The tag filter for Azure resource. The expected format is @{tagName1=$null} or @{tagName = 'tagValue'; tagName2='value1'}.  
[Back to top…](Readme.md#contents)
### Execute SVTs for a specific resource
The cmdlet below scans a single Azure resource within a specific resource group in a subscription and generates a status report:
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceGroupNames  -ResourceName 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- ResourceGroupNames – Name of the resource group that holds the individual resource to be scanned.
- ResourceName – Name of the resource. 
> **Note**: In the command above, 'ResourceName' should be the short name as used in Azure 
> and shown in the portal (as opposed to the fully qualified domain name (FQDN) which may 
> apply to some resource types such as storage blobs or SQL DB).  
[Back to top…](Readme.md#contents)
### Execute SVTs for a specific resource type
The cmdlet below scans all resources for a specific Azure resource type in a subscription (and a resource group [optional]):
1. 	Using Azure resource type
```PowerShell
 Get-AzSKAzureServicesSecurityStatus -SubscriptionId  [-ResourceGroupNames ] -ResourceType 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- [Optional] ResourceGroupNames  – Name of the container that holds related resource under an Azure subscription. Comma separated values are allowed.
- ResourceType – Resource type as defined by Azure. E.g.: Microsoft.KeyVault/vaults. Run command 'Get-AzSKSupportedResourceTypes' to get the list of supported types.
2. Using a user-friendly resource type name
```PowerShell
 Get-AzSKAzureServicesSecurityStatus -SubscriptionId  [-ResourceGroupNames ] -ResourceTypeName 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- [Optional] ResourceGroupNames – Name of the container that holds related resource under an Azure subscription. Comma separated values are allowed.
- ResourceTypeName – Friendly name of resource type. E.g.: KeyVault. Run command 'Get-AzSKSupportedResourceTypes' to get the list of supported values.  
[Back to top…](Readme.md#contents)
### Execute SVTs for specific control severity
```PowerShell
 Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -Severity "High, Medium"
```
The above command execution will result in scanning of 'High' and 'Medium' controls for Azure resources in your subscription
> **Note**: If you have mapped the AzSK control severity in your custom org policy settings 
> (refer: [Control severity mapping for your org](https://github.com/azsk/DevOpsKit-docs/tree/master/07-Customizing-AzSK-for-your-Org#testing-3) to know about mapping), then the final severities mapped should be passed as parameter values to -Severity parameter.  
[Back to top…](Readme.md#contents)
### Execute SVTs in Baseline mode 
In 'baseline mode' a centrally defined 'control baseline' is used as the target control set for scanning.
The cmdlet below scans azure resources in a subscription in Baseline mode and generates a status report:
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -UseBaselineControls
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -UsePreviewBaselineControls
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -UseBaselineControls -UsePreviewBaselineControls
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription. 
- UseBaselineControls – UseBaselineControls is the flag used to enable scanning of resources in Baseline mode.
- UsePreviewBaselineControls – UsePreviewBaselineControls is the flag used to enable scanning of resources in Preview Baseline mode.