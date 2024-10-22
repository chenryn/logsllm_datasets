To host all the Continuous Assurance artifacts
- Storage account (Format : azskYYYYMMDDHHMMSS) :- To store the daily results of CA scans. The storage account is named with a timestamp-suffix applied to 'azsk'(e.g. azsk20170420111140)
- Azure AD App and Service Principal :- This is used as the runtime identification of the automation runbook. Adds SPN to 'Reader' role on the subscription and contributor role on the resource group containing Automation Account.
- Automation Account (Name : AzSKContinuousAssurance) :- Creates the following assets within the Automation Account,
   - Runbook (Name : Continuous_Assurance_Runbook) - To download/update Azure/AzSK modules and scan subscription/app resource groups  
   - Variables 
      - AppResourceGroupNames 
      - LAWSId 
      - LAWSSharedKey 
      - ReportLogsStorageAccountName
   - Azure Run As Account - To authenticate runbook at runtime  
      This account uses below certificate and connection.  
      AzureRunAsCertificate - This certificate gets expired after six months of installation  
      AzureRunAsConnection - This connection is created using service principal with a AzureRunAsCertificate
   - Two schedules to trigger the runbook :-
      - CA_Scan_Schedule - This is to trigger job to scan subscription and app resource groups 
      - CA_Helper_Schedule - This is a temporary schedule created by runbook to retry download of modules
   - Modules - Downloaded by the runbook
#### Next Steps
Once CA is setup in the subscription, an app team can start leveraging the Monitoring Solution from AzSK as a one-stop dashboard for visibility of security state.
Occasionally, you may also feel the need to tweak the configuration of CA. See the "Update" section below about how to do that.
[Back to top…](Readme.md#contents)
## Updating an existing Continuous Assurance setup
The '**Update-AzSKContinuousAssurance**' command can be used to make changes to a previously setup CA configuration.
For instance, you may use it to:
- update the target resource groups to include in the scanning
- switch the Log Analytics workspace information that CA should use to send control evaluation events to
- use a different AAD SPN for the runbooks 
- remove previously set LogAnalytics, AltLogAnalytics, Webhook settings or ScanOnDeployment mode for CA account.
- etc.
To do any or all of these:
1. Open the PowerShell ISE and login to your Azure account (using **Connect-AzAccount**).  
2. Run the '**Update-AzSKContinuousAssurance**' command with required parameters given in below table. 
```PowerShell
Update-AzSKContinuousAssurance -SubscriptionId  `
    [-ResourceGroupNames ] `
    [-LAWSId ] `
    [-LAWSSharedKey ] `
    [-AltLAWSId ] `
    [-AltLAWSSharedKey ] `
    [-WebhookUrl ] `
    [-WebhookAuthZHeaderName ] `
    [-WebhookAuthZHeaderValue ] `
    [-ScanIntervalInHours ] `
    [-AzureADAppName ] `
    [-FixRuntimeAccount] ` 
    [-NewRuntimeAccount] `
    [-FixModules] `
    [-RenewCertificate]`
    [-Remove Runtime account deleted(Permissions required: Subscription owner)Runtime account permissions missing(Permissions required: Subscription owner and AD App owner)Certificate deleted/expired(Permissions required: Subscription owner and AD App owner)|FALSE|None||
|NewRuntimeAccount|Use this switch to setup new runtime account and the person running the command will become new SPN owner.This feature is helpful in case when CA certificate is expired but the SPN owner who had setup CA is not available and certificate can't be renewed. |FALSE|None||
|FixModules|Use this switch in case Az.Automation/Az.Accounts module(s) extraction fails in CA Automation Account.|FALSE|None||
|RenewCertificate|Renews certificate credential of CA SPN if the caller is Owner of the AAD Application (SPN). If the caller is not Owner, a new application is created with a corresponding SPN and a certificate owned by the caller. CA uses the updated credential going forward.|FALSE|None||
|ScanOnDeployment|CA scan can be auto-triggered upon resource deployment.Updating CA with this flag will make sure that the Resource Group in which resource is deployed will be scanned.|FALSE|None||
|Remove|Use this switch to clear previously set LogAnalytics, AltLogAnalytics,Webhook settings from CA Automation Account or to unregister from scan on deployment mode|False|None||
|UsageTelemetryLevel|Use this switch to stop anonymous telemetry capture at AzSK side.|False|Anonymous||
[Back to top…](Readme.md#contents)
## Removing a Continuous Assurance setup
1. Open the PowerShell ISE and login to your Azure account (using **Connect-AzAccount**).  
2. Run the '**Remove-AzSKContinuousAssurance**' command as below. 
```PowerShell
Remove-AzSKContinuousAssurance -SubscriptionId   [-DeleteStorageReports] 
```
|Param Name |Purpose |Required?	|Default value	|Comments|
|-----|-----|-----|----|-----|
|SubscriptionId	|Subscription ID of the Azure subscription in which Automation Account exists |True |None||	 
|DeleteStorageReports |Add this switch to delete AzSK execution reports from storage account. This will delete the storage container where reports are stored. Generally you will not want to use this option as all previous scan reports will be purged. |False |None||  
[Back to top…](Readme.md#contents)
## Getting details about a Continuous Assurance setup
1. Open the PowerShell ISE and login to your Azure account (using **Connect-AzAccount**).  
2. Run the '**Get-AzSKContinuousAssurance**' command as below. 
3. Result will display the current status of CA in your subscription. If CA is not working as expected, it will display remediation steps else it will display a message indicating CA is in healthy state.  
4. Once you follow the remediation steps, run the command again to check if anything is still missing in CA setup. Follow the remediation steps accordingly until the CA state becomes healthy. 
```PowerShell
Get-AzSKContinuousAssurance -SubscriptionId  
```
**Note:** This command is compatible only for Automation Account installed after 5th May, 2017 AzSK release.
[Back to top…](Readme.md#contents)
## Continuous Assurance (CA) - 'Central Scan' mode
The description so far has focused on setting up CA in a single subscription. When you have multiple subscriptions, you can setup CA individually for scanning each subscription. Alternatively, you can also setup CA in what is called a 'central scan' mode. The 'central scan' mode is more suited for scenarios where a single central team wants to exercise oversight of several subscription using a single master subscription for scanning. This section describes this mode and how to set it up further.
Unlike the 'individual subscription' mode where each subscription get its own instance of CA automation account, runbook, scan logs etc., the 'central scan' mode uses a single 'master' subscription to perform all scanning activities from. Use the following steps to setup 'central scan' mode: 
#### Pre-requisites:
- The user executing this command should have "Owner" access on all the subscriptions that are being enabled for central scanning mode including the master subscription.
- User should have the latest version of the DevOps Kit installed on the machine (>= [AzSK v3.1.x](https://www.powershellgallery.com/packages/AzSK/3.1.0))
- [Optional: Have a custom DevOps Kit policy setup for your org. This would provide more capabilities to control the scanning behavior. 
  (See [here](../07-Customizing-AzSK-for-your-Org/Readme.md) for more details on org policy.)
### Central Scan mode - single versus multiple Automation accounts:
When setting up CA with central scan mode, you have a choice regarding division of the scanning workload between automation accounts. You can choose to have all target subscriptions scanned via a single automation account *or* you can configure multiple automation accounts to divide the scanning workload amongst them by assigning each automation account a subset of the subscriptions for scanning. These two options and when to choose which one are covered below: 
#### 1. Central Scan mode CA using a single Automation account (default behavior):
With this option, a single automation account will get created in the host (master) subscription, which will scan all the target subscriptions. This mode is suitable for scanning up to a max of 40-50 subscriptions. (As the number of target subscriptions increases, the frequency of scan for each subscription reduces. Ideally each subscription should get scanned at least once per day. The multiple Automation account option might help if the count of subscriptions to be scanned is higher.)
##### 1.1 Setting up Continuous Assurance (CA) in Central Scan mode (single Automation account option):
This can be achieved by adding extra params to the existing CA command as shown in the command below:
```PowerShell
$SubscriptionId = ''
$ResourceGroupNames = '*' #This should always be '*' for Central Scan mode CA
$LAWSId = ''
$LAWSSharedKey = '' 
$TargetSubscriptionIds = '' #Need to provide comma separated list of all subscriptionId that needs to be scanned.
Install-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -TargetSubscriptionIds $TargetSubscriptionIds 
        -ResourceGroupNames $ResourceGroupNames -LAWSId $LAWSId -LAWSSharedKey $LAWSSharedKey -CentralScanMode 
        [-LoggingOption ''] [-SkipTargetSubscriptionConfig]
```
The table below lists only the parameters that are mandatory or have specific needs when used in the central scan mode CA setup. For the overall set of parameters, please review the CA parameters table above.
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central subscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of subscriptionIds that needs to be scanned by the central subscription. Host subscription is always appended by default. No need to pass that value in this param| True | The user executing this command should be owner on these subscriptions. |
|ResourceGroupNames| Comma separated list of ResourceGroupNames| True | Since you are planning to run in the central mode, you should use * as its value. This is because you need not have the same RG across all the subscriptions|
|LAWSId| All the scanning events will be send to this Log Analytics workspace. This will act as central monitoring dashboard | True | |
|LAWSSharedKey| SharedKey for the central monitoring dashboard| True | |
|LoggingOption| "IndividualSubs/CentralSub". This provides the capability to users to store the CA scan logs on central subscription or on individual subscriptions| False |CentralSub |
|SkipTargetSubscriptionConfig| (Optional) Use this switch if you dont have the owner permission on the target sub. This option assumes you have already done all the required configuration on the target sub. Check the note below| False| |
|CentralScanMode| Mandatory switch to specify in central scan mode| True | |
|UsageTelemetryLevel| Optional paramater to turn off anonymous telemetry at AzSK side if value set as None| False | Anonymous |
> **Note:** If you are using switch -SkipTargetSubscriptionConfig, then it assumes you have done all the required configuration on the target subscriptions. 
> Like, adding the CA SPN as Reader on target sub, Creating AzSK RG and a storage account name starting with azsk, Contributor permission to SPN on AzSKRG. 
> If any of the steps are not done, then central scan automation account will skip those target subscriptions. 
> You can use the script [here](https://github.com/azsk/DevOpsKit-docs/blob/master/04-Continous-Assurance/scripts/PrepareTargetSubscriptionForCentralModeCA.md) to prepare one or more target subscriptions for central mode scanning. The example invocation at the bottom of the script shows how to invoke the function in the script for a single target sub.
##### 1.2 Updating/modifying Central Scan mode CA (single Automation account option)
In case you want to add subscriptions covered via central scanning mode you can use Update-AzSKContinuousAssurance as shown below. (All other CA configuration settings can also be updated as described in Update-AzSKContinuousAssurance earlier in this document.)
```PowerShell
$SubscriptionId = ''
$LAWSId = ''
$LAWSSharedKey = '' 
$TargetSubscriptionIds = '' #Need to provide comma separated list of all subscriptionId that needs to be scanned.
Update-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -TargetSubscriptionIds $TargetSubscriptionIds -CentralScanMode -FixRuntimeAccount
     [-LoggingOption ] 
```
> **Note:** All other parameters as described in the main Update-AzSKContinuousAssurance parameters table apply. They are not repeated below for brevity.
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central subscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of subscriptionIds that needs to be scanned by the central subscription. It would always append the values provided in this param to the current scanning list.| True | The user executing this command should be owner on these subscriptions. |
|LoggingOption| "IndividualSubs/CentralSub" | False | Only provide if you want to change the logging option|
|FixRuntimeAccount| This will correct all the permissions issues related to the scanning account| False | Provide this switch only when you want to add new subscriptions for central scanning mode |
|CentralScanMode| It is mandatory to use CentralScanMode switch| True | |
##### 1.3 Diagnosing the health of Central Mode CA (single Automation account option)
You can run the command below to enquire the health of CA setup in your subscription. Note that the '-CentralScanMode' flag is not required for this command.
```PowerShell
$SubscriptionId = ''
Get-AzSKContinuousAssurance -SubscriptionId $SubscriptionId [-ExhaustiveCheck]
```
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central SubscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|ExhaustiveCheck| (Optional) By appending this switch it would check whether all the modules installed in central automation account are up to date| False | Only include if default diagnosis is not resulting in any issue |
##### 1.4  Remove Central Scan mode CA from the master subscription (single Automation account option)
In case you want to 
(a) unregister some subs from central scanning mode, or 
(b) to delete the scan logs, or 
(c) to remove the whole automation account
```PowerShell
$SubscriptionId = ''
Remove-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -DeleteStorageReports -CentralScanMode 
```
|Param Name| Purpose| Required?| DefaultValue| Comments|
|----------|--------|----------|-------------|---------|
|SubscriptionId| Central SubscriptionId which is responsible for scanning all the other subscriptions| True | This subscription would host the Automation account which is responsible for scanning all the other subscriptions|
|TargetSubscriptionIds| Comma separated list of target subIds which will be un-registered from the central scanning mode. | False | |
|DeleteStorageReports| Deletes all the scan logs from the azsk storage account based on the logging option and value provided in the target subscription. If used with out CentralScanMode switch, it would remove all logs from the host sub central storage account.| False | Only include if default diagnosis is not resulting in any issue |
|CentralScanMode| It is mandatory to use CentralScanMode switch| True | |