>**Note** If just subscriptionId is passed, then it would check if the host sub is in central scanning mode, if so, user needs to pass CentralScanMode switch specifically. In these scenarios, it would remove the whole automation account from host sub.
#### 2. Central Scan mode CA using multiple Automation accounts
If you are trying to scan multiple target subscriptions, then scanning all of them using a single Automation account can be tedious and face scale/performance issues. Furthermore, with too many subscriptions to scan, you may not be able to scan each subscription with the desired scan interval.
In such scenarios, you can use the multiple accounts approach by grouping your subscriptions into batches and scanning these batches 
using multiple independent automation accounts with in the same host/central subscription.
In this scenario, all your logs, scanning configuration, attestation data is persisted under the default AzSKRG whereas each automation account will have its own dedicated RG for CA bookkeeping.
##### 2.1 Setting up Continuous Assurance (CA) in Central Scan mode (multiple Automation accounts option):
When you have more than about 40-50 subscriptions to scan, it is better to use multiple Automation accounts option of the Central Scan mode. You need to split the overall set of target subscriptions into multiple groups and then decide names to use for the Automation account and the resource groups that will host the CA for each group. Once this grouping and naming is done, you simply run the central scan mode CA setup command once for each group (with additional parameters identifying the Automation account name and the resource group that will serve as the host for scanning the respective group).
> **Note:** When using multi-Automation Account mode, be sure to provide a _unique_ Automation account name and a _unique_ resource group name for each CA setup. Basically, each such tuple represents a unique CA setup within the master/central subscription. You will need to carefully provide this tuple for subsequent Update-CA/Remove-CA calls as well...as it is this tuple that helps CA identify the subscription group being targeted. 
> Furthermore, make sure you do not use the default CA account name ("AzSKContinuousAssurance") or the default AzSK resource group name for the org (e.g., "AzSKRG") when using this mode. Those are reserved for the single CA account mode!
```PowerShell
$SubscriptionId = ''
$ResourceGroupNames = '*' #This should always be '*' for Central Scan mode CA
$LAWSId = ''
$LAWSSharedKey = '' 
$TargetSubscriptionIds = '' #Need to provide comma separated list of all subscriptionId that needs to be scanned.
#if you have text file containing subscription ids then run below script
#$FileContent = Get-Content -Path ""
#$TargetSubscriptionIds = ($FileContent| foreach {$_.Trim()}) -join "," 
#if you have PowerShell array object containing subscription ids e.g. $SubIdArray = @("subid1","subid2","subid3") then run below script
#$TargetSubscriptionIds = ($SubIdArray| foreach {$_.Trim()}) -join "," 
$AutomationAccountLocation = ''
$AutomationAccountRGName = '' # e.g. AzSK-Category-ScanRG01
$AutomationAccountName = '' # e.g. AzSKScanningAccount01
# **Note** You should use the unique names for AutomationAccountRG and AutomationAccountName to avoid any conflicts while setup
Install-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -TargetSubscriptionIds $TargetSubscriptionIds 
        -ResourceGroupNames $ResourceGroupNames -LAWSId $LAWSId -LAWSSharedKey $LAWSSharedKey 
        -AutomationAccountRGName $AutomationAccountRGName -AutomationAccountName $AutomationAccountName -AutomationAccountLocation $AutomationAccountLocation -CentralScanMode 
        [-LoggingOption ''] [-SkipTargetSubscriptionConfig]
```
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central subscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of subscriptionIds that needs to be scanned by the central subscription. Host subscription is always appended by default. No need to pass that value in this param| True | The user executing this command should be owner on these subscriptions. |
|ResourceGroupNames| Comma separated list of ResourceGroupNames| True | Since you are planning to run in the central mode, you should use * as its value. This is because you need not have the same RG across all the subscriptions|
|LAWSId| All the scanning events will be send to this Log Analytics workspace. This will act as central monitoring dashboard | True | |
|LAWSSharedKey| SharedKey for the central monitoring dashboard| True | |
|AutomationAccountLocation| (Optional) Location where the AutomationAccount to be created | False | |
|AutomationAccountRGName| Name of ResourceGroup which will hold the scanning automation account. Should be different than "AzSKRG". | True | e.g. AzSK-Category-ScanRG01 |
|AutomationAccountName| Name of the automation account which will scan the target subscriptions. (This should be different than "AzSKContinuousAssurance".) | True | e.g. AzSKScanningAccount01|
|LoggingOption| "IndividualSubs/CentralSub". This provides the capability to users to store the CA scan logs on central subscription or on individual subscriptions| False |CentralSub |
|SkipTargetSubscriptionConfig| (Optional) Use this switch if you dont have the owner permission on the target sub. This option assumes you have already one all the required configuration on the target sub. Check the note below| False| |
|CentralScanMode| Mandatory switch to specify in central scan mode| True | |
> **Note:** If you are using switch -SkipTargetSubscriptionConfig, then it assumes you have done all the required configuration on the target subscriptions. 
> Like, adding the CA SPN as Reader on target sub, Creating AzSK RG and a storage account name starting with azsk, Contributor permission to SPN on AzSKRG. 
> If any of the steps are not done, then central scan automation account will skip those target subscriptions. 
> You can use the script [here](https://github.com/azsk/DevOpsKit-docs/blob/master/04-Continous-Assurance/scripts/PrepareTargetSubscriptionForCentralModeCA.md) to prepare one or more target subscriptions for central mode scanning. The example invocation at the bottom of the script shows how to invoke the function in the script for a single target sub.
##### 2.2 Updating/modifying Central Scan mode CA (multiple Automation accounts option)
In case you want to add/update new subscriptions to any of the groups, you can do so using the command below (this is similar to the single Automation account command, except that you have to specify the AutomationAccountRGName and AutomationAccountName):
```PowerShell
$SubscriptionId = ''
$AutomationAccountRGName = '' # e.g. AzSK-Category-ScanRG01
$AutomationAccountName = '' # e.g. AzSKScanningAccount01
$TargetSubscriptionIds = '' #Need to provide comma separated list of all subscriptionId that needs to be scanned.
#if you have text file containing subscription ids then run below script
#$FileContent = Get-Content -Path ""
#$TargetSubscriptionIds = ($FileContent| foreach {$_.Trim()}) -join "," 
#if you have PowerShell array object containing subscription ids e.g. $SubIdArray = @("subid1","subid2","subid3") then run below script
#$TargetSubscriptionIds = ($SubIdArray| foreach {$_.Trim()}) -join "," 
Update-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -TargetSubscriptionIds $TargetSubscriptionIds 
        -AutomationAccountRGName $AutomationAccountRGName -AutomationAccountName $AutomationAccountName -CentralScanMode -FixRuntimeAccount
        [-LoggingOption ] 
```
> **Note:** All other parameters as described in the main Update-AzSKContinuousAssurance parameters table apply. They are not repeated below for brevity.
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central subscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of subscriptionIds that needs to be scanned by the central subscription. It would always append the values provided in this param to the current scanning list.| True | The user executing this command should be owner on these subscriptions. |
|AutomationAccountRGName| Name of Resource Group which will hold the scanning automation account | True | e.g. AzSK-Category-ScanRG01 |
|AutomationAccountName| Name of the Automation Account which will scan target subscriptions | True | e.g. AzSKScanningAccount01|
|LoggingOption| "IndividualSubs/CentralSub" | False | Only provide if you want to change the logging option|
|FixRuntimeAccount| This will correct all the permissions issues related to the scanning account| False | Provide this switch only when you want to add new subscriptions for central scanning mode or if scanning account credential needs to be updated |
|CentralScanMode| It is mandatory to use CentralScanMode switch| True | |
##### 2.3 Diagnosing the health of Central Mode CA (multiple Automation accounts option)
You can run the command below to enquire the health of CA setup in your subscription. In the case of multi-Automation account setup, you can query the status of one setup at a time. As a result, you must pass the name of the automation account and the automation account resource group as parameters. Note that the '-CentralScanMode' flag is not required for this command.
```PowerShell
$SubscriptionId = ''
$AutomationAccountRGName = '' # e.g. AzSK-Category-ScanRG01
$AutomationAccountName = ' # e.g. AzSKScanningAccount01
Get-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -AutomationAccountRGName $AutomationAccountRGName -AutomationAccountName $AutomationAccountName [-ExhaustiveCheck] 
```
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central SubscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions
|AutomationAccountRGName| Name of Resource Group which will hold the scanning automation account | True | e.g. AzSK-Category-ScanRG01 |
|AutomationAccountName| Name of the Automation Account which will scan target subscriptions | True | e.g. AzSKScanningAccount01|
|ExhaustiveCheck| (Optional) By appending this switch it would check whether all the modules installed in central automation account are up to date| False | Only include if default diagnosis is not resulting in any issue |
##### 2.4  Remove Central Scan mode CA from the master subscription (multiple Automation accounts option)
In case you want to 
(a) unregister some subs from central scanning mode, or 
(b) to delete the scan logs, or 
(c) to remove the whole automation account
```PowerShell
$SubscriptionId = ''
$AutomationAccountRGName = '' # e.g. AzSK-Category-ScanRG01
$AutomationAccountName = ' # e.g. AzSKScanningAccount01
Remove-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -DeleteStorageReports -AutomationAccountRGName $AutomationAccountRGName -AutomationAccountName $AutomationAccountName -CentralScanMode 
```
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central SubscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of target subIds which will be un-registered from the central scanning mode. | False | |
|AutomationAccountRGName| Name of Resource Group which will hold the scanning automation account | True | e.g. AzSK-Category-ScanRG01 |
|AutomationAccountName| Name of the Automation Account which will scan target subscriptions | True | e.g. AzSKScanningAccount01|
|DeleteStorageReports| Deletes all the scan logs from the azsk storage account based on the logging option and value provided in the target subscription. If used with out CentralScanMode switch, it would remove all logs from the host sub central storage account.| False | Only include if default diagnosis is not resulting in any issue |
|CentralScanMode| It is mandatory to use CentralScanMode switch| True | |
>**Note** If just subscriptionId is passed, then it would check if the host sub is in central scanning mode, if so, user needs to pass CentralScanMode switch. In these scenarios, it would remove the whole automation account from host sub.
[Back to top…](Readme.md#contents)
## Scan Databricks using custom AzSK Job
The basic idea behind setting up job in databricks workspace is to continuously validate security state of workspace. We are also exploring this as a general approach to expand AzSK scans into the ‘data’ plane for various cluster technologies.
>**Note:** This feature is currently in preview, changes are expected in upcoming releases.
### Setting up Job - Step by Step
In this section, we will walk through the steps of setting up a AzSK Job in databricks workspace. 
To get started, we need the following:
1. The user setting up Job needs to have 'admin' access to the Databricks workspace.
2. User should have generated a Personal Access Token(PAT).
**Step-1: Setup** 
0. Copy latest script from scripts section(SetupDatabricksScanJob.md).
1. Open the PowerShell ISE and paste script. 
2. Run the script after updating required parameters.
3. When prompted enter personal access token(PAT).
**Step-2: Verifying that Job Setup is complete** 
**1:** Go to your Databricks workspace that was used above. In workspace you should see an folder created by the name 'AzSK'. Inside this folder, there should be a notebook by the name "AzSK_CA_Scan_Notebook".
**2:** Go to jobs in your workspace, there should be a job by the name "AzSK_CA_Scan_Job".
>**Note:** To ensure the proper access control of Notebook and Job, you should use Workspace Access Control and Job Access Control to prevent unauthorized access to notebook contents and job.
### How it works (under the covers)
The Job installation script that sets up Job creates the following resources in your workspace:
- Secret scope (Name : AzSK_CA_Secret_Scope) :- 
To keep personal access token(PAT) that will be used further by Notebook to scan controls.
- Folder (Name : AzSK) :- To store the scan Notebook.
- Notebook (Name : AzSK_CA_Scan_Notebook) :- This is the notebook that will contain logic to run AzSK control scan over workspace.
- Job (Name : AzSK_CA_Scan_Job) :- This is the job that will be used to run Notebook on a scheduled basis.
### FAQ
#### What permission do I need to setup CA?
You need to be 'Owner' on the subscription.
This is required because, during CA setup, we add RBAC access to an Azure AD App (SPN) that's utilized for running the 'security scan' runbooks in Azure Automation. Only an'Owner' for a subscription has the right to change subscription RBAC.  
#### SPN permission could not be set while renewing the CA certificate. What should I do?
In order to fix missing permissions/ setup new runtime account, you need to be an ‘Owner’ on the subscription. This is required because we add RBAC access to an Azure AD App (SPN) that's utilized for running the 'security scan' runbooks in Azure Automation. Only an 'Owner' for a subscription has the right to change subscription RBAC. Please verify whether you have ‘Owner’ permission on the subscription.
#### What are AzSKRG and AzSK_CA_SPN used for?
The AzSK Continuous Assurance (CA) setup basically provisions your subscription with the ability to do daily scans and sends the scan results to your Log Analytics workspace.
To do the scanning, the CA setup process creates a runtime account (owned by you) and grants that account 'Reader' access to your subscription. This is the AzSK_CA_SPN_xxxx that you will notice in a 'Reader' role if you look at the Access Control (IAM) list for your subscription.
The CA setup also creates an automation account that holds the runbook (scanning code), the schedules (that trigger the daily scan) and other configuration parameters (e.g., your Log Analytics workspace info, target resource groups list, etc.) This, and other artifacts related to AzSK and functioning of AzSK commands, are held in a resource group called 'AzSKRG' in your subscription. 
Each day, the runbook executes under the identity of the AzSK_CA_SPN_xxxx runtime account and performs a scan of the subscription and contained resources (per the currently applicable baseline controls list). 
At the end of the each scan, the SPN needs some place to store the results (so that they can be examined by someone as need be later). For the purpose of storing the ZIP files from daily scans, a storage account is used. This storage account is also held within the same (AzSKRG) resource group and a blob container called 'AzSKexecutionlogs' is where the ZIP files are written each day. Because the CA SPN writes to the storage account, it needs 'Contributor' access to the 'AzSKRG' resource group. This access is also setup during the Install-AzSKContinuousAssurance (CA setup) command. 
In general, all artifacts within the AzSKRG resource group are considered 'read only'. Respective AzSK cmdlets have the logic to manage these resources built-in. You should not make any modifications directly to either the contents of this resource group or to the permissions of the SPN (AzSK_CA_SPN_xxxx) as this may impact the functioning of AzSK CA or other AzSK commands. 
#### How to fix SPN permissions for my AzSK Continuous Assurance setup?
The AzSK_CA_SPN is used to perform scanning and do the bookkeeping necessary for Continuous Assurance scans. As a result, during CA installation, it is granted 'Reader' access at subscription scope and 'Contributor' access at AzSKRG resource group scope. If any of these are changed/removed, CA functioning will be impacted. To revert to correct permissions run the following:
```PowerShell
Update-AzSKContinuousAssurance -SubscriptionId  -FixRuntimeAccount
``` 
See the above question for more info about the SPN and AzSKRG.
#### Is it possible to setup CA if there is no Log Analytics workspace?
No. The intent of CA is to scan regularly and be able to monitor the outcomes for security drift. Out of the box, AzSK CA uses Log Analytics for the monitoring capabilities. (Basically, AzSK sends control evaluation results to a connected Log Analytics workspace.)  