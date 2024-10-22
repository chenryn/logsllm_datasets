Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceTypeName Storage `
                -ResourceName $resourceName `
                -BulkAttestControlId $bulkAttestControlId `
                -ControlsToAttest NotAttested `
                -AttestationStatus NotAnIssue `
                -JustificationText $justificationText
 ``` 
The above command will record the justification and attestation input/choice for all the specified StorageAccounts for the GRS control.
A user can re-run the scan command below to confirm the final control status:
```PowerShell  
$subscriptionId = 'Your SubscriptionId'
$resourceNames = 'Comma-separated values for the Storage Account resource names' 
$controlId = 'Azure_AppService_AuthN_Use_AAD_for_Client_AuthN'
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceTypeName Storage `
                -ResourceNames $resourceName `
                -ControlIds $controlId 
 ``` 
**Bulk clearing past attestation:** 
The bulk attestation feature can also be used for situations where a user wants to clear the attestation for 
multiple resources in bulk, for a specified controlId. This can be achieved by running the command below:
 ```PowerShell  
$subscriptionId = 
$resourceGroupName = 
$resourceName = 
$bulkAttestControlId = 
$justificationText = 
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId -ResourceGroupNames $resourceGroupName -ResourceName $resourceName `
				-BulkAttestControlId $bulkAttestControlId -ControlsToAttest AlreadyAttested -BulkClear
 ``` 
> **Note**: Usage of BulkClear with 'NotAttested' Option of ControlsToAttest param, would result in failure.
### FAQs
##### Can fixing an AzSK control impact my application?
Most of the AzSK recommendations are generic and are based on security standards and best practices that are widely applicable when processing sensitive data. However, just like any other configuration change, a change to security configuration should be treated with care especially in production environments. In other words, do exercise due diligence and perform good testing (to assess impact on functionality, performance and cost) and follow the required change management discipline expected from engineering teams in your org before making changes in the context of business critical workloads. It is also useful to review any changes with the application architect/design team. This helps ensure a more comprehensive impact assessment. 
As examples, we have had a few cases where teams directly made changes to production and realized that it broke their business scenarios. E.g. there were a couple of applications where internal components in the app were using a hard-coded 'non-HTTPS' string to access a Web API also within the app. As a result, when the Web API was switched to use HTTPS-only, the application workflow started breaking. :-( 
Clearly, these changes themselves were required (per security policy/standards) and were the right thing for securing the enterprise data these applications were handling. Yet, because the applications were not themselves designed to be able to handle the change it led to production impact. (These are also important lessons for all of us on the value of embedding security from the very start in every stage of dev ops...right from subscription provisioning through prototyping, development, deployment (CICD) and operations.)
On a related note, every control in the AzSK may not be applicable to every scenario. Some controls are, by nature, contextual. Others are best practices that are 'good to have' but not a 'must'. In such cases, the control recommendations do provide indications (using wording such as 'where possible' or 'where applicable'). For example, if a backend store is accessed from a multitude of client devices practically from anywhere then an IP-based restriction may not be practical to impose on the data store. However, in another application, one may have a scenario where the backend store is accessed from a controlled pool of middle tier servers (only). In such a case, an IP-based restriction is practical and can add an extra layer of security if the data is highly sensitive in nature.
#### What permission should I have to perform attestation in AzSK?
Control attestation is a privileged operation. As a result, non-owners don't have permissions to attest controls by default.
To be able to attest to controls for your subscription, you should ask the subscription owner to grant you 'Contributor' access to the storage account under the resource group 'AzSKRG'. The storage account looks something like: 'AzSKyyyymmddhhmmss'
The AzSK docs for control attestation are [here](../00c-Addressing-Control-Failures/Readme.md#control-attestation)
#### Attestation fails with permission error even though I am Owner.
It can happen due to below reasons
1. User who is attesting doesn't have Contributor/ Owner access on the AzSKRG 
   Sol. => In this scenario the user is already co-admin.
2. "AzSK-controls-state" Container is missing in the AzSK storage account 
   Sol. => Run the below script on your subscription after replacing the storage account name. You can find the AzSK storage account under AzSKRG resource group in your subscription
   ```PowerShell
   $StorageAccountName = ""
   $keys = Get-AzStorageAccountKey -ResourceGroupName "AzSKRG"  -Name $StorageAccountName
   $currentContext = New-AzStorageContext -StorageAccountName $StorageAccountName -StorageAccountKey $keys[0].Value -Protocol Https
   $Container = Get-AzStorageContainer -Name "AzSK-controls-state" -Context $currentContext -ErrorAction SilentlyContinue
   if($null -eq $Container)
   {       
     New-AzStorageContainer -Name "AzSK-controls-state" -Permission Off -Context $currentContext
   }
   ```
3. AzSKRG resource group is not present on the subscription 
   Sol. => By setting up Continuous Assurance on your subscription will create the required AzSK artifacts.
   ```PowerShell
   Install-AzSKContinuousAssurance -SubscriptionId "" -ResourceGroupNames "*" -LAWSId "" -LAWSSharedKey ""
   ```
#### Why do I have new control failures from AzSK?
You might come across a scenario that you spent some time and fixed all the issues that you were expected to and "got to green". Now, a few days (or weeks) later, you are seeing that you have to address a bunch of issues. You may wonder - 'What happened? Why do I get new failures from AzSK?'
There are many reasons why you may see 'new' control failures after you put in the effort to resolve existing ones. Here are some common ones: 
a- You may have net new resources that were created/deployed to the subscription. The first time CA scans these resources (usually within 24 hours of their creation), it will flag any security control failures. 
b- Someone on the team perhaps changed the configuration of an existing resource. In a large subscription with many stakeholders acting on different resources and resource groups, this is quite a possibility. That is where CA helps! It watches over the drift and reports it. 
c- Baseline control set may change. As attacks get sophisticated, so must our defense. It is quite possible that a control that was not considered "core hygiene" might become so a few months down. This will mean that for existing resources, everyone now has a new control to fix. 
d- New controls may get added. Azure is a very dynamic environment. The PG adds new features and security capabilities every quarter in some services and every six months in most others. When a new security feature is added, the AzSK may be modified to add a new control to cover it. If the control is core/fundamental, then everyone will be expected to fix it on existing resources. (Remember that CA automatically picks up latest AzSK bits for scanning. So, the moment a version of AzSK gets released with a new control and it is a 'baseline' control, CA scans will start checking the control on existing resources.) 
e- Control logic for existing controls may change - due to bug fixes or additional conditions in the detection logic. This change in control behavior will, again, start reflecting in CA scans when a version of AzSK with the 'fix' or 'logic change' is released. 
f- Configuration baselines may change. What is considered a mandatory account today may not remain so tomorrow or in 6 months. Certificates expire, credentials/accounts get deprecated. The AzSK is able to detect that your subscription contains these accounts but the access permissions that CA has does not let CA make any changes. 
Phew...We hope we covered the main reasons. One last thought is that in the current "agile + dev ops + cloud" era, with all rapid iterations and changes happening at all layers, security has also become a much more 'continuous' effort compared to the past.
#### I am trying to enable diagnostic logs using the recommendation command 'Set-AzDiagnosticSetting' given in the AzSK control. But the command fails with error 'The diagnostic setting 'service' doesn't exist'. How do I resolve this error?
There is an [open issue](https://github.com/Azure/azure-powershell/issues/6833) with Set-AzDiagnosticSetting command provided by Az. You can enable the diagnostic logs using Azure portal until that issue is resolved. Steps are available [here](https://docs.microsoft.com/en-us/azure/monitoring-and-diagnostics/monitoring-archive-diagnostic-logs#archive-diagnostic-logs-using-the-portal).
Just make sure that logs are retained for a minimum of 365 days.
#### I wish to deploy virtual networking in a hub and spoke architecture, where ExpressRoute is connected to a Core network, which is then connected via VNET Peering, or VPN to other VNET’s, or other Azure datacentres. But some of the controls regarding ExpressRoute-connected Virtual Networks contradict my requirement. How does AzSK justify the controls like "There should not be another virtual network gateway (GatewayType = Vpn) in an ER-vNet" and "There should not be any virtual network peerings on an ER-vNet"? How should I satisfy them without changing my implementation plans?
The control regarding ‘do not peer another vNet with ER-connected vNet’ is a precautionary one and one that we expect would apply to most typical users of ER-Networks. However, when there are advanced users/scenarios like the one described above, you can certainly ‘attest’ the control and tell the DevOps Kit to treat it as passed in the future. However, it assumes that the person/team doing so is doing the proper diligence in ensuring that the configuration is setup securely and that it would not lead to new pathways between the wild internet and the corporate environment.
This same thinking applies to many of the other network-infra related controls. For example, we have a control that flags off ‘IP forwarding’. This would apply to 99% of scenarios…however, there are legit cases where the control may not apply and can be ‘attested’ (e.g., you may be doing additional traffic inspection using a virtual appliance on a network).
To understand the concept of attestation and how it works, you can go through the other FAQs in the Addressing Control Failures section in our documentation.
#### I am unable to evaluate/attest some Key Vault controls even with co-admin privilege. I am getting the error: Skipping attestation process for this control. You do not have required permissions to evaluate this control.(Please note that you must have access permissions to the keys & secrets in the key vault for successful attestation of this control) (If you are 'Owner' then please elevate to 'Co-Admin' in the portal and re-run in a *fresh* PS console.) 
Some key vault controls require permission(‘Get and ’List’) on keys and secrets to check certain properties like expiry date etc. If the user account/application does not have access on the keys and secrets stored in the key vault resource, then the scan will result into ‘Manual’ state as the control will not get evaluated due to insufficient permission. In such cases where the user/application is not able to evaluate any control due to permission issues then it must not be attesting them without knowing the actual risk.
Ensure the user account/application executing the scan commands has atleast ‘Get’ and ‘List’ (read permissions) Key and Secret Permissions. [Azure Portal -> Key Vault resource -> Access Policy -> User/Application -> Enable ‘get’ and ‘List’ in Key Permissions + Secret Permissions]
#### I am unable to scan/attest API connection controls independently. I am getting the error: Could not find any resources to scan under Resource Group. InvalidOperation: Could not find any resources that match the specified criteria. How should I scan and bulk attest API connection controls?
In the DevOps kit, API connections are scanned as child resource of Logic App. To scan/attest controls associated with API connection, you need to scan the parent logic app and the child resources will get scanned with it. Please note that bulk attestation is not supported in this case. API connection controls can only be attested sequentially using the below command:
```
# Scan a specific Logic App and the API connections associated with the app
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceTypeName LogicApps -ResourceNames  -ControlsToAttest NotAttested
# Scan all Logic Apps and the API connections associated with those apps
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceTypeName LogicApps -ControlsToAttest NotAttested
```
#### I cannot find the API connection on portal that is listed in the AzSK CSV scan result. Where can I find these resource on portal?
You may come across a scenario where you get multiple API connections in the scan result, but they are not available on portal. These API connections are Connectors that being used by your Logic App. To view these connectors, go to your Logic App --> Logic App Designer. Here is a document on various types of [Connectors for Azure Logic Apps](https://docs.microsoft.com/en-us/azure/connectors/apis-list). 
#### How do I remediate failing control Azure_Subscription_AuthZ_Dont_Grant_Persistent_Access_RG?
The time taken to evaluate control Azure_Subscription_AuthZ_Dont_Grant_Persistent_Access_RG, is directly proportional to the number of resource groups you have in your subscription AND total number of identities that have access on those resource groups. As a result, the GSS scan may take significant amount of time to complete for subscriptions with multiple resource groups. Hence, we have enabled this control only in CA mode. In manual mode, we skip the actual control scan and instruct the user to see the evaluation details about this control in the CA job scans.
If you have addressed the causes for control failure and you need to manually scan the control, you can override the current behavior by explicitly specifying the controlId in the scan cmdlet as shown below.
``` 
Import-Module AzSK
Get-AzSKSubscriptionSecurityStatus -SubscriptionId $subid -ControlId Azure_Subscription_AuthZ_Dont_Grant_Persistent_Access_RG
```
#### How do I remediate failing control Azure_APIManagement_DP_Use_Secure_TLS_Version?
3DES Ciphers, TLS protocols (1.1 and 1.0) and SSL 3.0 are outdated versions. Using these can expose the API to meet-in-the-middle attack, chosen-plaintext or known-plaintext attacks. Use the following command to disable the aforementioned configurations. 
Make sure you test the implications before changing the configuration.
Please note that this command may take 15 to 20 minutes to update the configuration.
```
# Enter SubscriptionId, ResourceGroupName, APIMServiceName
$SubscriptionId = ''
$ResourceGroupName = ''
$APIMServiceName = ''
Set-AzContext $SubscriptionId
# Get API Management service instance
$apim = Get-AzResource -Name $APIMServiceName -ResourceGroupName $ResourceGroupName -ResourceType Microsoft.ApiManagement/service
# Turn off unsecure protocol and cipher configurations
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Ssl30' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls10' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls11' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Ssl30' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10' = "false"
$apim.Properties.customProperties.'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11' = "false"
# Save the updated configuration
$apim | Set-AzResource -Force
```
#### How do I remediate failing control Azure_AppService_DP_Use_Secure_TLS_Version?
Using latest TLS version significantly reduces risks from security design issues and security bugs that may be present in older versions. If you are noticing this control failing for your app service, use the following command to set minimum TLS version to 1.2.
Make sure you test the implications before changing the configuration.
```
# Enter SubscriptionId, ResourceGroupName, AppServiceName
$SubscriptionId = ''
$ResourceGroupName = ''
$AppServiceName = ''
Set-AzContext $SubscriptionId
# Update TLS version
Get-AzResource -ResourceType Microsoft.Web/sites -ResourceGroupName $ResourceGroupName -Name $AppServiceName  | ForEach-Object {
    $params = @{
        ApiVersion        = '2018-02-01'
        ResourceName      = '{0}/web' -f $_.Name
        ResourceGroupName = $_.ResourceGroupName
        PropertyObject    = @{ minTlsVersion = 1.2 }
        ResourceType      = 'Microsoft.Web/sites/config'
    }
Set-AzResource @params -Force
}
```
#### Many of the Azure Databricks control goes to manual state from both CA and local scan. What should I do to evaluate Azure Databricks resources properly?
Some of the controls of Azure Databricks (ADB) can not be scanned properly from CA as they need ADB workspace's personal access token (PAT) with admin privileges. In local scan also by default such controls will go to manual state as it requires PAT to evaluate these controls and DevOps Kit will not prompt for PAT (instead it will try to read PAT via session variable) as it will result in halting the scan progress untill PAT is provided. 
So, to evaluate ADB controls properly from local scan mode, please set a session variable named 'ADBPatsForAzSK' with required value as shown in example below:
```
# For a single ADB workspace
Set-Variable 'ADBPatsForAzSK' -Scope Global -Value @{'ADBResourceName' = 'Personal access token'}
# For multiple ADB workspaces
Set-Variable 'ADBPatsForAzSK' -Scope Global -Value @{'ADBResourceName1' = 'Personal access token 1';
                                                     'ADBResourceName2' = 'Personal access token 2'}
```
Then in the same session please run scan command as follows:
``` 
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceTypeName Databricks -ResourceNames  
```
[Back to top...](Readme.md#contents)