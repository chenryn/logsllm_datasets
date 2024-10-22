 Sample summary of attestation after workflow is completed:
 ![02_SVT_Attest_2](../Images/02_SVT_Attest_2.PNG) 
 Sample summary of scan of attested controls:
 ![02_SVT_Attest_4](../Images/02_SVT_Attest_4.PNG) 
Attestation details corresponding to each control (e.g., justification, user name, etc.) are also captured in the CSV file in next scan as shown below:
 ![02_SVT_Attest_3](../Images/02_SVT_Attest_3.PNG) 
The attestation process for application resources is similar to that for subscriptions. For example, the command below shows how to 
trigger attestation for a specific resource in an RG:
```PowerShell  
$subscriptionId = 
$resourceGroupName = 
$resourceName = 
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceGroupNames $resourceGroupName `
                -ResourceName $resourceName `
                -ControlsToAttest NotAttested `
                -DoNotOpenOutputFolder 
``` 
If, for any reason, the attestations of previously attested controls need to be revisited, it can be done by simply changing the 'NotAttested' flag in the commands above with 'AlreadyAttested'.  
[Back to top...](Readme.md#contents)
### How AzSK determines the effective control result
During the attestation workflow, the user gets to provide attestation (sub)status for each control attested. This basically represents the user's attestation preference w.r.t.
a specific control (i.e., whether the user wants to override/augment the AzSK status and treat the control as passed or whether the user agrees with the AzSK status but wants to defer
fixing the issue for the time being):
|Attestation Status | Description|
|---|---|
|None | There is no attestation done for a given control. User can select this option during the workflow to skip the attestation|
|NotAnIssue | User has verified the control data and attesting it as not an issue with proper justification to represent situations where the control is implemented in another way, so the finding does not apply. |
|WillNotFix | User has verified the control data and attesting it as not fixed with proper justification|
|WillFixLater | User has verified the control data and attesting it as not fixed with proper justification stating the future fix plan|
|**NotApplicable | User has verified the control data and attesting it as not applicable for the given design/context with proper justification. |
|**StateConfirmed | User has verified the control data and attesting it as state confirmed to represent that the control state is correct/appropriate with proper justification. |
 >  ** These are special attestation status which are supported only in selected controls.
The following table shows the complete 'state machine' that is used by AzSK to support control attestation. 
The columns are described as under:
- 'Control Scan Result' represents the technical evaluation result 
- 'Attestation Status' represents the user choice from an attestation standpoint
- 'Effective Status' reflects the effective control status (combination of technical status and user input)
- 'Requires Justification' indicates whether the corresponding row requires a justification comment
- 'Comments' outlines an example scenario that would map to the row
|Control Scan Result  |Attestation Status |Effective Status|Requires Justification | ExpiryInDays| Comments |
|---|---|---|---|---|---|
|Passed |None |Passed |No | -NA- |No need for attestation. Control has passed outright!|
|Verify |None |Verify |No | -NA- |User has to ratify based on manual examination of AzSK evaluation log. E.g., SQL DB firewall IPs list.|
|Verify |NotAnIssue |Passed |Yes | 90 |User has to ratify based manual examination that finding does not apply as the control has been implemented in another way. For example, AAD authentication for App Service was implemented through code. |
|Verify |WillNotFix |Exception |Yes | Based on the control severity table below|Valid security issue but a fix cannot be implemented immediately. E.g., A 'deprecated' account was found in the subscription. However, the user wants to check any dependencies before removal.|
|Verify |WillFixLater |Remediate |Yes| Based on the control severity table below|Valid security issue but a fix cannot be implemented immediately. E.g., A 'deprecated' account was found in the subscription. However, the user wants to check any dependencies before removal.|
|Verify |NotApplicable |Passed |Yes| 90 |User has to ratify based on manual examination that the finding is not applicable for given design/context. E.g., Runbook does not contain any hard-coded secure information. |
|Verify |StateConfirmed |Passed |Yes| Based on the control severity table below|User has to ratify based on manual examination that the control state is correct/appropriate. E.g., SQL firewall IPs scenario, where all IPs are legitimate.|
|Failed |None |Failed |No | -NA- | Control has failed but has not been attested. Perhaps a fix is in the works...|	 
|Failed |NotAnIssue |Passed |Yes | 90 |Control has failed. However, the finding does not apply as the control has been implemented in another way. For example, AAD authentication for App Service was implemented through code.|
|Failed |WillNotFix |Exception |Yes | Based on the control severity table below| Control has failed. The issue is not benign, but the user has some other constraint and cannot fix it. E.g., Need an SPN to be in Owner role at subscription scope.|
|Failed |WillFixLater |Remediate |Yes | Based on the control severity table below| Control has failed. The issue is not benign, but the user wishes to defer fixing it for later. E.g., AAD is not enabled for Azure SQL DB.|
|Failed |NotApplicable |Passed |Yes| 90 |Control has failed. However, user confirms based on manual examination that the finding is not applicable for given design/context.|
|Failed |StateConfirmed |Passed |Yes| Based on the control severity table below|Control has failed. However, user confirms based on manual examination that the control state is correct/appropriate. |
|Error |None |Error |No | -NA- | There was an error during evaluation. Manual verification is needed and is still pending.|
|Error |NotAnIssue |Passed |Yes | 90| There was an error during evaluation. Manual verification by user indicates that the finding does not apply as the control has been implemented in another way.|
|Error |WillNotFix |Exception |Yes | Based on the control severity table below| There was an error during evaluation. Manually verification by the user indicates a valid security issue.|
|Error |WillFixLater |Remediate |Yes | Based on the control severity table below| There was an error during evaluation. Manually verification by the user indicates a valid security issue.|
|Error |NotApplicable |Passed |Yes| 90 |There was an error during evaluation. However, user confirms based on manual examination that the finding is not applicable for given design/context.|
|Error |StateConfirmed |Passed |Yes| Based on the control severity table below|There was an error during evaluation. However, user confirms based on manual examination that the control state is correct/appropriate.|
|Manual |None |Manual |No | -NA-| The control is not automated and has to be manually verified. Verification is still pending.| 
|Manual |NotAnIssue |Passed |Yes | 90| The control is not automated and has to be manually verified. User has reviewed the security concern and implemented the fix in another way.|
|Manual |WillNotFix |Exception |Yes | Based on the control severity table below| The control is not automated and has to be manually verified. User has reviewed and found a security issue to be fixed.|
|Manual |WillFixLater |Remediate |Yes | Based on the control severity table below| The control is not automated and has to be manually verified. User has reviewed and found a security issue to be fixed.|
|Manual |NotApplicable |Passed |Yes| 90 |The control is not automated and has to be manually verified. User confirms based on manual examination that the finding for given design/context is not applicable. |
|Manual |StateConfirmed |Passed |Yes| Based on the control severity table below| The control is not automated and has to be manually verified. User has verified that there's no security concern.|
-NA- => Not Applicable
Control Severity Table:
|ControlSeverity| ExpiryInDays|
|----|---|
|Critical| 7|
|High   | 30|
|Medium| 60|
|Low| 90|
The following table describes the possible effective control evaluation results (taking attestation into consideration).
|Control Scan Result| Description|
|---|---|
|Passed |Fully automated control. Azure resource/subscription configuration meeting the AzSK control requirement|
|Verify |Semi-automated control. It would emit the required data in the log files which can be validated by the user/auditor. e.g. SQL DB IP ranges|
|Failed |Fully automated control. Azure resource/subscription configuration not meeting AzSK control requirement|
|Error |Automated control. Currently failing due to some exception. User needs to validate manually|
|Manual |No automation as of now. User needs to validate manually|
|Exception |Risk acknowledged. The 'WillNotFix' option was chosen as attestation choice/status. |
|Remediate |Risk acknowledged with a remediation plan. The 'WillFixLater' option was chosen as attestation choice/status.|
[Back to top...](Readme.md#contents)
### Permissions required for attesting controls:
The attestation feature internally stores state in a storage account in a resource group called AzSKRG. (This RG is also used by other features in the AzSK for stateful scenarios.)
If this RG has already been created, then a user needs 'Owner' permission to it.
If this RG is not present (as is possible when none of the scenarios that internally create this RG have been run yet), then the user needs 'Owner' or 'Contributor' permission to the subscription.
> **Note**: The attestation data stored in the AzSKRG is opaque from an end user standpoint. Any attempts to access/change it may impact correctness of security evaluation results.  
[Back to top...](Readme.md#contents)
### Attestation expiry:
All the control attestations done through AzSK is set with a default expiry. This would force teams to revisit the control attestation at regular intervals. 
Expiry of an attestation is determined through different parameters like control severity, attestation status etc. 
There are two simple rules for determining the attestation expiry. Those are:
Any control with evaluation result as not passed, 
 1. and attested as 'NotAnIssue' or 'NotApplicable', such controls would expire in 90 days.
 2. and attested as 'WillFixLater' or 'WillNotFix' or 'StateConfirmed', such controls would expire based on the control severity table below.
|ControlSeverity| ExpiryInDays|
|----|---|
|Critical| 7|
|High   | 30|
|Medium| 60|
|Low| 90|
The detailed matrix of attestation details and its expiry can be found under [this](Readme.md#how-azsk-determines-the-effective-control-result) section. Attestation expiry date is also emitted in CSV scan result as shown in [this](../Images/02_SVT_Attest_3.PNG) image.
> **Note**: 
> * All the controls are subjected to an initial grace period from the first scanned date. On expiry of grace period for a control,
>  1. 'WillFixLater' option will be disabled for further attestation.
>  2. if the control was attested as 'WillFixLater', then attestation will expire.
> User will then have the option to either fix the control or use other available attestation states with proper justification.
> 
>* Attestation may also expire before actual expiry in cases when the attested state for the control doesn't match with current control state.
[Back to top...](Readme.md#contents)
### Bulk attestation
In some circumstances, you may have to perform attestation for a specific resource type across several instances. For instance,
you may have 35 storage accounts for which you need to perform attestation for one specific control. To do this one resource at
a time can be inefficient - especially if the reason for attesting the control is the same across all those resource instances. The
bulk attestation feature helps by empowering subscription/security owners to provide a common justification for a set of resources
all of which have a specific (single) controlId that requires attestation. This essentially 'automates' attestation by using 
a slightly different combination of parameters alongside '-ControlsToAttest'.
 ```PowerShell  
$subscriptionId = 'Your subscription Id'
$resourceGroupNames = 'Comma-separated list of resource groups'
$resourceNames = 'Comma-separated list of resources'
$bulkAttestControlId = 'AzSK ControlId string'     # You can get this from the CSV file, first column.
$justificationText = 'Rationale behind your choice of AttestationStatus here...'
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceGroupNames $resourceGroupNames `
                -ResourceNames $resourceNames `
                -ControlsToAttest NotAttested `
                -BulkAttestControlId $bulkAttestControlId `                 # ControlId to be attested
                -AttestationStatus  ` # Attestation choice/input, use one of these.
                -JustificationText $justificationText                   # Additional (text) justification
``` 
|Parameter Name| Description|
|---|---|
|BulkAttestControlId |ControlId to bulk-attest. Bulk attest mode supports only one controlId at a time.|
|ControlsToAttest | See table in the  [Starting Attestation](Readme.md#starting-attestation) section. |
|AttestationStatus | Attester must select one of the attestation reasons (NotAnIssue, WillNotFix, WillFixLater)|
|JustificationText | Attester must provide an apt justification with proper business reason.|
To understand this better, let us take two example scenarios where bulk attestation can help,
###### Scenario 1: ######
The application uses multiple App Services where AAD authentication has been implemented through code. 
The control has been evaluated as 'Verify' by AzSK because it cannot infer the status from the settings.
You know that for all these applications, AAD-authentication has been correctly implemented and want to 'Attest' that
control for all of them in a single pass. 
In this scenario, bulk attestation can be used as below to 'attest' the ControlId 'Azure_AppService_AuthN_Use_AAD_for_Client_AuthN' 
for all App Service objects: 
```PowerShell  
$subscriptionId = 'Your SubscriptionId'
$resourceNames = 'Comma-separated list of AppService names' 
$bulkAttestControlId = 'Azure_AppService_AuthN_Use_AAD_for_Client_AuthN'
$justificationText = 'AAD authentication has been enabled through code and has been tested.'
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceTypeName AppService `
                -ResourceNames $resourceName `
                -ControlsToAttest NotAttested `
                -BulkAttestControlId $bulkAttestControlId `
                -AttestationStatus NotAnIssue `
                -JustificationText $justificationText
 ``` 
The above command will record the justification and attestation input for all specified AppServices for the AAD-AuthN control. 
A user can re-run the scan command below, to confirm the control result status.
```PowerShell  
$subscriptionId = 'Your SubscriptionId'
$resourceNames = 'Comma separated values for the AppService resource names' 
$controlId = 'Azure_AppService_AuthN_Use_AAD_for_Client_AuthN'
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceTypeName AppService `
                -ResourceNames $resourceName `
                -ControlIds $controlId 
 ``` 
###### Scenario 2: ###### 
An application uses many Storage Accounts, of which a subset is used only to store web site performance logs. 
Because these logs aren't critical business data, the business does not want to incur the expense of geo-redundant
storage for the storage accounts holding them. All other storage accounts, however, store critical business data which business absolutely
cannot afford to lose in the event of regional disasters. Thus, we have a situation where an AzSK control (in this case
the GRS setting for Storage Accounts) must pass for a subset of resources while it need to be 'attested' for 
the remainder.
In this scenario, bulk attestation can be used as shown below to attest the 'Azure_Storage_Deploy_Use_Geo_Redundant' ControlId 
for a specific set of storage accounts:
```PowerShell  
$subscriptionId = 'Your SubscriptionId'
$resourceNames = 'Comma-separated values for the Storage Account resource names' 
$bulkAttestControlId = 'Azure_Storage_Deploy_Use_Geo_Redundant'
$justificationText = 'Storage Account currently used for perf logs only. Business agrees that GRS option is not needed.'