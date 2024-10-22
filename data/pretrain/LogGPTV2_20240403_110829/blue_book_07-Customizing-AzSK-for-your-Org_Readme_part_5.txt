If you want to run commands with Org-neutral policy only, you can delete tag (AzSKOrgName_{OrgName}) present on AzSKRG and run the commands.
If you are maintaining multiple org policies and you want to switch scan from one policy to other, you can run Set/Update commands with '-Force' flag using policy you wanted to switch. 
#### Latest AzSK is available but our org CA are running with older version?
AzSK keeps on adding and enhancing features with different capabilities to monitor Security compliance for org subscriptions. During these enhancement in new releases, it may include latest features and some breaking changes. To provide smoother upgrade and avoid policy breaks, AzSK provides feature for org policy to run AzSK with specific version by using configuration present in AzSK.Pre.json. This configuration is referred in multiple places for installing org supported AzSK version in different environments like Installer (IWR) (Installs AzSK in local machine), RunbookCoreSetup (Install AzSK in CA). You need to update property "CurrentVersionForOrg" in AzSK.Pre.json to latest available version after validating if org policy is compatible with latest AzSK version.
#### We have configured baseline controls using ControlSettings.json on Policy Store, But Continuous Assurance (CA) is scanning all SVT controls on subscription?
Continuous Assurance (CA) is configured to scan all the controls. We have kept this as a default behavior since org users often tend to miss out on configuring baseline controls. This behavior is controlled from org policy. If you observed, there are two files present in policy store, RunbookCoreSetup.ps1 (Responsible to install AzSK) and RunbookScanAgent.ps1 (Performs CA scans and export results to storage account). You can update RunbookScanAgent to make only baseline scan. (By passing -UseBaselineControls parameter to Get-AzSKAzureServicesSecurityStatus and Get-AzSKSubscriptionSecurityStatus commands present in RunbookScanAgent.ps1 file). 
#### Continuous Assurance (CA) is scanning less number of controls as compared with manual scan?
 CA automation account runs with minimum privileges i.e. 'Reader' RBAC permission and cannot scan some controls that require more access.
 Here are a few examples of controls that CA cannot fully scan or can only 'partially' infer compliance for:
Azure_Subscription_AuthZ_Dont_Use_NonAD_Identities - requires Graph API access to determine if an AAD object is an 'external' identity
Azure_Subscription_AuthZ_Remove_Management_Certs - querying for management certs requires Co-Admin permission
Azure_AppService_AuthN_Use_AAD_for_Client_AuthN - often this is implemented in code, so an app owner has to attest this control. Also, any 'security-related' config info is not accessible to the 'Reader' RBAC role.
Azure_CloudService_SI_Enable_AntiMalware - needs co-admin access
Azure_CloudService_AuthN_Use_AAD_for_Client_AuthN - no API available to check this (has to be manually attested)
Azure_Storage_AuthN_Dont_Allow_Anonymous - needs 'data plane' access to storage account (CA SPN being a 'Reader' cannot do 'ListKeys' to access actual data).
In general, we make practice to individual teams to perform scan with high privileged role on regular basis to validate Owner access controls results. If you wanted to scan all controls using continuous assurance, you have to 
- Provide CA SPN's as [Owner/Co-Admin RBAC role](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal#grant-access) at subscription scope and [graph API read permissions](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-integrating-applications#updating-an-application).
- Remove *-ExcludeTags "OwnerAccess"* parameter against scan commands (*Get-AzSKAzureServicesSecurityStatus* and *Get-AzSKSubscriptionSecurityStatus*) present in RunbookScanAgent.ps1 file on policy store. 
#### How should I protect org policy with AAD based auth?
Currently basic org policy setup uses read only SAS token to fetch policy files. You will be able to protect policy based on AAD auth using below steps
1. Setup AAD based API: 
	Create API Service with [AAD auth](https://docs.microsoft.com/en-us/azure/app-service/app-service-mobile-how-to-configure-active-directory-authentication) which will point to and return files from Policy container present under org policy Store. API URL looks like below
    ```
	https://.azurewebsites.net/api/files?version=$Version&fileName=$FileName
    ```
> **Note:** Here version and file name are dynamic and passed during execution of AzSK commands. 
2. Update Installer(IWR) with latest policy store url:
	Go to IWR file location(present in policy store --> installer
	--> AzSK-EasyInstaller.ps1) 
	a. Update OnlinePolicyStoreUrl with AD based auth API URL from step 1. (**Note:** Keep tilt(\`) escape character as is)
		https://.azurewebsites.net/api/files?version=`$Version&fileName=`$FileName
	b. Search for command "Set-AzSKPolicySettings" in IWR and add parameter "-EnableAADAuthForOnlinePolicyStore"
3. Update local settings to point to latest API:
	Run IWR command in local machine PowerShell. This will point your local machine to latest policy store URL and AzSK commands will start using AAD based auth.  
4. Update existing CA to point to latest API:
	If CA is already installed on subscriptions. You can just run Update-CA command. This will update runbook to use latest policy store URL.
5. Update CICD task to point to latest API:
	Refer [step 5](https://github.com/azsk/DevOpsKit-docs/tree/master/03-Security-In-CICD#adding-svts-in-the-release-pipeline) from SVT Task documentation to update policy url in pipeline. Make sure you set EnableServerAuth variable to true. 
**Note:** We are already exploring on latest AAD based auth feature available on Storage to protect policy. Above steps will be updated in future once AzSK is compatible with latest features.
#### Can I completely override policy. I do not want policy to be run in Overlay method?
Yes. You can completely override policy configuration with the help index file. 
**Steps:**
i) Copy local version of configuration file to policy folder. Here we will copy complete AppService.json. 
Source location: "%userprofile%\Documents\WindowsPowerShell\Modules\AzSK\\Framework\Configurations\SVT"
Destination location:
 "D:\ContosoPolicies"
![Copy Configurations](../Images/07_OrgPolicy_CopyConfiguration.png)
ii) Update configurations for all required controls in AppService.json
iii) Add entry for configuration in index file(ServerConfigMetadata.json) with OverrideOffline property 
![Override Configurations](../Images/07_OrgPolicy_ServerConfigOverride.png)
iv) Run update/install org policy command with required parameters. 
### Control is getting scanned even though it has been removed from my custom org-policy.
If you want only the controls which are present on your custom org-policy to be scanned, set the  OverrideOffline flag to true in the ServerConfigMetadata.json file.
Example: If you want to scan only the ARMControls present in your org-policy, then set the OverrideOffline flag to true as shown below.
![ARM Controls override](../Images/07_Custom_Policy_ARMControls.png)
##### Testing:
Run clear session state command(Clear-AzSKSessionState) followed by services scan (Get-AzSKAzureServicesSecurityStatus). Scan should reflect configuration changes done.
### How to customize attestation expiry period for controls? 
There are two methods with which attestation expiry period can be controlled using org policy. 
1. Update attestation expiry period for control severity 
2. Update attestation expiry period for a particular control in SVT  
**Note:** Expiry period can be customized only for statuses "WillNotFix", "WillFixLater" and "StateConfirmed". For status "NotAnIssue" and "NotApplicable", expiry period can be customized using "Default" period present as part of ControlSettings configuration.
#### 1. Update attestation expiry period for control severity 
   Steps:
   i) Go to ControlSettings configuration present in module folder.  
      Source location: "%userprofile%\Documents\WindowsPowerShell\Modules\AzSK\\Framework\Configurations\SVT\ControlSettings.json"
   ii) Copy "AttestationExpiryPeriodInDays" settings
   iii) Create/update "ControlSettings.json" in org policy configuration folder (It is the same folder from where org policy is installed) and paste AttestationExpiryPeriodInDays configurations to file
   iv) Update attestation expiry period against control severity. For e.g., here we will make "High" severity control to expire after 60 days, "Critical" to 15 days and others set to 90 days 
   ![Controls attestation expiry override](../Images/07_OrgPolicy_AttestationExpiryOverride.png)
   v) Update org policy with the help of Update-AzSKOrganizationPolicy (UOP) cmdlet. (If you have created policy custom resources, mention resource names as parameter for UOP cmdlet)
   ```
      Update-AzSKOrganizationPolicy -SubscriptionId $SubId -OrgName "Contoso" -DepartmentName "IT" -PolicyFolderPath "D:\ContosoPolicies"
   ```
##### Testing:
1. Run clear session state command (Clear-AzSKSessionState).
2. You can attest one of the "High" severity controls or if you have control already attested, you can go to step 3
   Example: In this example, we will attest storage control with "WillNotFix" status
   ```
   Get-AzSKAzureServicesSecurityStatus -SubscriptionId $SubId `
                                    -ResourceNames azskpreviewcontosopr3sa `
                                    -ControlIds "Azure_Storage_AuthN_Dont_Allow_Anonymous" `
                                    -ControlsToAttest NotAttested 
   ```
   Output:
   ![Controls attestation expiry override](../Images/07_OrgPolicy_AttestationFlow.png)
3. Run Get-AzSKInfo (GAI) cmdlet to get all attested controls in Sub with expiry details. 
   Note: Make sure cmdlet is running with org policy. If not you will need to run "IWR" generated at the time of IOP or UOP cmdlet.
   ```
   Get-AzSKInfo -InfoType AttestationInfo -SubscriptionId 
   ```
4. Open CSV or detailed log file generated at the end of command execution. It will show expiry period column for attested column.
   Detailed log:
   ![Controls attestation expiry override](../Images/07_Custom_Policy_AttestationExpiryReportOutput.png)
   CSV report:
   ![Controls attestation expiry override](../Images/07_Custom_Policy_AttestationExpiryReport.png)
#### 2. Update attestation expiry period for particular control in SVT 
i) Copy the Storage.json from the AzSK module to your org-policy folder
   Source location: "%userprofile%\Documents\WindowsPowerShell\Modules\AzSK\\Framework\Configurations\SVT\Services\Storage.json"
   Destination location: Policy config folder in local (D:\ContosoPolicies\Config)
ii) Remove everything except the ControlID, the Id and add property "AttestationExpiryPeriodInDays" as shown below. 
   ```
   {
    "Controls": [
     {
        "ControlID": "Azure_Storage_AuthN_Dont_Allow_Anonymous",
        "Id": "AzureStorage110",
        "AttestationExpiryPeriodInDays": 45
     }
    ]
   }
   ```
iii) Update org policy with the help of UOP cmdlet with required parameters. 
   ```
      Update-AzSKOrganizationPolicy -SubscriptionId $SubId -OrgName "Contoso" -DepartmentName "IT" -PolicyFolderPath "D:\ContosoPolicies"
   ```
##### Testing:
   For testing follow same steps mentioned above for [scenario 1](./#testing-7)
### How to configure non-AAD identity providers for AppService?
   You will be able to configure non-AAD identity providers and external redirect URLs using below settings:
i)Copy the ControlSettings.json from the AzSK installation to your org-policy folder.
ii)Update required values in below tags under AppService:
```JSON
"AllowedAuthenticationProviders": [
  ],
"AllowedExternalRedirectURLs": [
   ]
```
iii)Make sure identity providers from AllowedAuthenticationProviders are removed from NonAADAuthProperties.
```JSON
"NonAADAuthProperties": [
	   "googleClientId",
      "facebookAppId"
      "twitterConsumerKey",
      "microsoftAccountClientId"
    ]
```
iv) Save the file.
v) Override ControlSettings.json in ServerConfigMetaData.json as shown below:
```JSON
   {
    "OnlinePolicyList" : [
        {
            "Name" : "AzSK.json"
        }, 
        {
            "Name" : "ControlSettings.json",
			   "OverrideOffline" :true
        }, 
        {
            "Name" : "ServerConfigMetadata.json",
			   "OverrideOffline" : true
        }
    ]
}
```
vi) Rerun the policy update or setup command (the same command you ran for the first-time setup).
### How can we treat each public IP address as an individual resource?
   Org policy admins can enable public IP address as an individual resource by making following org policy settings:
i) Copy the ControlSettings.json from the AzSK installation to your org-policy folder.
   a) If you already have a overridden ControlSettings.json, add the following new settings to it.
   ```JSON
"PublicIpAddress": {
    "EnablePublicIpResource": false
   },
```
ii) Update the EnablePublicIpResource setting to true.
```JSON
"PublicIpAddress": {
    "EnablePublicIpResource": true
   },
```
iii) Save the file.
iv)  Edit the ServerConfigMetadata.json file in your local org-policy folder and create an entry for "ControlSettings.json" as below:
```JSON
   {
    "OnlinePolicyList" : [
        {
            "Name" : "AzSK.json"
        }, 
        {
            "Name" : "ControlSettings.json",
        }, 
    ]
}
```
v) If you are using an already overridden ControlSettings.json, edit the ServerConfigMetadata.json file as follows:
```JSON
   {
    "OnlinePolicyList" : [
        {
            "Name" : "AzSK.json"
        }, 
        {
            "Name" : "ControlSettings.json",
            "OverrideOffline" : true
        }, 
    ]
}
```
vi) Rerun the policy update or setup command (the same command you ran for the first-time setup).
vii) Command that will be helpful in scanning a public IP address resource:
```PowerShell
 $subscriptionId = 
$resourceGroupName = 
$resourceName = 
$ControlId = 'Azure_PublicIpAddress_Justify_PublicIp'
Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subscriptionId `
                -ResourceGroupNames $resourceGroupName `
                -ResourceName $resourceName `
                -ControlId $ControlId
   ```