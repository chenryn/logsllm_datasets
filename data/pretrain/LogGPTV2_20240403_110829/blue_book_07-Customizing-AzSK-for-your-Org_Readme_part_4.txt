> **Note:** You may not see "Schedule refresh" option if step [a3] and [a4] is not completed successfully.
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_24.png)
## AzSK org health monitoring dashboard
Monitoring dashboard gets created along with policy setup and it lets you monitor the operations for various DevOps Kit workflows at your org.(e.g. CA issues, anomalous control drifts, evaluation errors, etc.). 
You will be able to see the dashboard at the home page of Azure Portal. If not, you can navigate to the following path to see the dashboard
Go to Azure Portal --> Select "Browse all dashboards" in dashboard dropdown -->  Select type "Shared Dashboard" --> Select subscription where policy is setup -->Select "DevOps Kit Monitoring Dashboard [OrgName]"
Below is snapshot of the dashboard
## Detail resource inventory dashboard
With the help of telemetry events you will be able to monitor resources inventory in the Org. This will give the visibility over all resources along with control failures over all subscriptions. The PowerBI based template will be shared soon
# Compliance notifications
## Compliance notification to subscription owners
Coming soon
# Advanced usage of org policy (extending AzSK)
## Customizing the SVTs
 It is powerful capability of AzSK to enable an org to customize the SVT behaviour.  Refer [extending AzSK modules](./Extending%20AzSK%20Module/Readme.md) for more details. You will be able to achieve the following scenarios.
   - [Update/extend existing control by augmenting logic](./Extending%20AzSK%20Module/Readme.md##steps-to-extend-the-control-svt)
   - [Add new control for existing GSS/GRS SVT](./Extending%20AzSK%20Module/Readme.md#a-extending-a-gss-svt)
   - [Add an altogether new SVT (non-existing service scan)](./Extending%20AzSK%20Module/Readme.md#steps-to-add-a-new-svt-to-the-azsk-module)
## Customizing subscription security
   Along with subscription security checks, AzSK provides security provisioning commands (e.g. setting up mandatory ARM policies, RBAC roles, ASC configurations etc.) on a subscription. Refer [link](https://github.com/azsk/DevOpsKit-docs/blob/master/01-Subscription-Security/Readme.md#azsk-subscription-security-provisioning-1) for more details on provisioning commands. Each provisioning status is validated with the help of subscription scan controls. Below table gives the details of provisioning commands , GSS control to validate provisioning status and policy file name where all provisioning configurations are present.
| Component  | Provisioning Command | Control in GSS  | Policy File Name | Description | 
| ---- | ---- | ---- |---- | ---- |
| ARM Policy | Set-AzSKARMPolicies | Azure_Subscription_Config_ARM_Policy | Subscription.ARMPolicies.json | Sets ARM policies corresponding to certain actions that are considered insecure. |
| Critical Alerts | Set-AzSKAlerts | Azure_Subscription_Audit_Configure_Critical_Alerts |  Subscription.InsARMAlerts.json | Configuration of subscription and resource alerts for activities with significant security implications |
| Azure Security Center configuration | Set-AzSKAzureSecurityCenterPolicies | Azure_Subscription_Config_Azure_Security_Center |  SecurityCenter.json | Default enterprise policy settings for Azure Security Center like configuring security contact information in ASC etc. |
| RBAC roles/permissions | Set-AzSKSubscriptionRBAC | Azure_Subscription_AuthZ_Add_Required_Central_Accounts |  Subscription.RBAC.json | Setup mandatory accounts that are required for central scanning/audit/compliance functions. |
Common steps for configuring policies for subscription provisioning
 i) Copy the provisioning policy file from the AzSK installation folder (%userprofile%\documents\WindowsPowerShell\Modules\AzSK\\Framework\Configurations\SubscriptionSecurity) to your org-policy folder
 ii) Edit policy file with schema and guidance given below section for each component 
 iii) Add entry for configuration in index file (ServerConfigMetadata.json) with OverrideOffline property. OverrideOffline is required for all provisioning policies as it does not support overlay method. 
![Override Configurations](../Images/07_OrgPolicy_PovisioningPolicy.PNG)
 iv) Rerun the org policy update or setup command (the same command you ran for the first-time setup)
Once policy is updated, it will start respecting in subscription scan command and failing controls with details of missing configuration on subscriptions. 
Ideally below steps are expected to be executed by individual subscription owners.
 i) Run subscription scan
   ```PowerShell
   # Subscription scan
   Get-AzSKSubscriptionSecurityStatus -SubscriptionId 
   # Scanning perticular policy control 
   Get-AzSKSubscriptionSecurityStatus -SubscriptionId  -ControlIds "Azure_Subscription_Config_ARM_Policy"
   ```
ii) Validate detail logs printing missing policies expected by Org policy
iii) Execute [provisioning command](../01-Subscription-Security/Readme.md#azsk-subscription-security-provisioning-1) with required parameters
   > **Note:** If you want to configure all policies(alert,ARM policy, ASC and RBAC), you can use all in one command Set-AzSKSubscriptionSecurity.
iv) Run subscription scan again and validate control gets passed. 
### Schema for policy files 
#### ARM policy 
   ```C#
   {
      "Version": "3.1809.0",
      "Policies": [      
         {
            "policyDefinitionName": "AzSK_ARMPol_Deny_Classic_Resource_Create", // Friendly policy name. The format used is AzSK_ARMPol___ 
            "policyDefinition": "{\"if\":{\"anyOf\":[{\"field\":\"type\",\"like\":\"Microsoft.ClassicCompute/*\"},{\"field\":\"type\",\"like\":\"microsoft.classicStorage/*\"},{\"field\":\"type\",\"like\":\"Microsoft.ClassicNetwork/*\"}]},\"then\":{\"effect\":\"deny\"}}", // Policy definition. Here we are defining denial of classic resource creation
            "description": "Policy to deny upon creation of classic/v1 (i.e., ASM-based) resources", //  Description about the policy
            "tags": [   
               "Mandatory"
            ], // Tag for policy. Mandatory tag is always picked up by set-AzSKARMPolicy command. If you mention any other tags, you will need to pass explicitly to set command
            "enabled": true, // Defines whether the ARM policy is enabled or not.
            "scope": "/subscriptions/$subscriptionId" // Scope at which policy needs to be applied
         }
      ],
      "DeprecatedPolicies" : [] // Array of deprecated policydefinitionnames. This policy will get removed during policy setup
   }
   ```
To view the samples of ARM policy definitions rules and syntaxes, refer [link](https://docs.microsoft.com/en-us/azure/governance/policy/samples/)
#### Alert set
You will find current supported alert list [here](/02-Secure-Development/ControlCoverage/Feature/AlertList.md).  
   ```C#
   {
      "Version": "3.1803.0",
      "AlertList": [ 
         {
            "Name": "AzSK_Subscription_Alert", // Alert name containing group of all operations.  
            "Description": "Alerts for Subscription Activities", // Alert description
            "Enabled": true, // Defines alert is enabled or not
            "Tags": [ 
            "Mandatory"
            ], // Tag for Alerts group. Mandatory tag is always picked up by set-AzSKAlerts command. 
            "AlertOperationList": [
            {
               "Name": "AzSK_Assign_the_caller_to_User_Access_Administrator_role", // Friendly name for operations
               "Description": "Grants the caller User Access Administrator access at the tenant scope", // operation details
               "OperationName": "Microsoft.Authorization/elevateAccess/action", // operation name
               "Tags": [
                  "Mandatory"
               ],
               "Severity": "Critical", // severity for operation Critial/High. Critical operations are considered for SMS alerts
               "Enabled": true  // // Defines operation is enabled or not
            }
            ]
         }
   }
   ```
You will get all activity operations that can be added as part of alert using below command 
```PowerShell
Get-AzProviderOperation | FT
```
#### Security center configurations
   Security center can be configured for three things
   -  Autoprovisioning 
   -  SecurityContacts
   -  Default policy setup
```C#
{
    "Version": "3.1906.0",    
    "autoProvisioning" : {
        "id": "/subscriptions/{0}/providers/Microsoft.Security/autoProvisioningSettings/default",
        "name": "default",
        "type": "Microsoft.Security/autoProvisioningSettings",
        "properties": {
        "autoProvision": "On"
        }
    },
    "securityContacts" : {
        "id": "/subscriptions/{0}/providers//Microsoft.Security/securityContact/default",
        "name": "default",
        "type": "Microsoft.Security/securityContact",
        "properties": {
            "alertNotifications": {
               "state": "On",
               "minimalSeverity": "Medium"
            },
            "emails": "{1}",
            "notificationsByRole": {
               "state": "On",
               "roles": [
                  "Owner",
                  "ServiceAdmin"
               ]
            },
            "phone": "{2}"
         }
    },
    "policySettings" : {
        "properties": {
            "displayName": "ASC Default (subscription: {0})",
            "policyDefinitionId": "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8",
            "scope": "/subscriptions/{0}",
            "notScopes": [],
            "parameters": {                                                              
                "endpointProtectionMonitoringEffect": {
                    "value": "AuditIfNotExists"
                }
            },
            "description": "This policy assignment was automatically created by Azure Security Center",
            "metadata": {
                "assignedBy": "Security Center"
            }
        },
        "id": "/subscriptions/{0}/providers/Microsoft.Authorization/policyAsssignments/SecurityCenterBuiltIn",
        "type": "Microsoft.Authorization/policyAssignments",
        "name": "SecurityCenterBuiltIn"
    },
    "optionalPolicySettings" : {}
}
```
   ### RBAC mandatory/deprecated lists
   You will be able to check/configure mandatory and deprecated list of RBAC for all subscriptions with the help of below schema
   ```C#
   {
      "ActiveCentralAccountsVersion": "2.1709.0",
      "DeprecatedAccountsVersion": "2.1709.0",
      "ValidActiveAccounts": [
         {
            "Name": "Contoso Cost Trackers", // Name of the account to be provisioned or checked for. 
            "Description": "This AAD group account is deployed as Reader on all subscriptions at Contoso to monitor cost.", //Description for your account. 
            "ObjectId": "", // Object id for user or group or SPN in tenant 
            "ObjectType": "Group", // ServicePrincipal or User or Group.
            "RoleDefinitionName": "Reader", //Subscription RBAC rolename. 
            "Scope": "/subscriptions/$subscriptionId", //Scope of access.
            "Type": "Provision or Validate. E.g., Provision",
            "Tags": [ "Mandatory" ], //Commma separated list of tags each in double quotes. The tag 'Mandatory' means this account is deployed by default and always checked during verification. 
            "Enabled": true
         }
      ],
      "DeprecatedAccounts": [
         {
            "Name": "Name of the account that is considered deprecated and must be deprovisioned. E.g., AutoDeploySPN",
            "Description": "Description for the account. E.g., This was used for automated deployments in the past. It must be removed from all subscriptions.",
            "ObjectId": "object_id_for_user_or_group_or_SPN_in_tenant",
            "ObjectType": "ServicePrincipal or User or Group, E.g., ServicePrincipal",
            "Enabled": false
         }
      ]
   }
```
## ARM checker policy customization
Check [this](https://github.com/azsk/DevOpsKit-docs/blob/master/03-Security-In-CICD/Readme.md#extending-arm-template-checker-for-your-organization)
## Change default resource group name (AzSKRG) and location (EastUS2) created for AzSK components
You can control default resource group name and location using AzSK config present in org policy. Follow below steps to override default behaviour.
> **Note:** Changing default resource group name will break existing continuous assurance setup. You will need to do re-setup of all CA.
**Steps:**
i) Open the AzSK.json from your local org-policy folder
ii) Add the properties for  as under:
    "AzSKRGName" : "",
    "AzSKLocation" : ""
iii) Save the file
iv) Run the policy update command.
##### Testing:
Run "IWR" in a fresh PS session (you can ask any other user to run this IWR) to setup policy setting in local. If you have already installed policy using IWR, just run CSS (Clear-AzSKSessionState) followed by command *Set-AzSKSubscriptionSecurity* with required parameters as per the [doc](../01-Subscription-Security/Readme.md#azsk-subscription-security-provisioning-1). This will provision AzSK components(Alerts/Storage etc) under new resource group and location.
**Note:** For continuous assurance setup, you need to follow two extra steps.
i) Pass location parameter "AutomationAccountLocation" explicitly during execution of installation command (Install-AzSKContinuousAssurance). 
ii) Update $StorageAccountRG variable (In RunbookScanAgent.ps1 file present in policy store) value  to AzSKRGName value.
## Scenarios for modifying ScanAgent
   ### Scanning only baseline controls using continuous assurance setup
   Continuous Assurance (CA) is configured to scan all the controls. We have kept this as a default behavior since org users often tend to miss out on configuring baseline controls. This behavior is controlled from org policy. 
   If you observed, there are two files present in policy folder under **CA-Runbook** folder, 
   - RunbookCoreSetup.ps1: Responsible to install AzSK module  
   - RunbookScanAgent.ps1: Performs CA scans and export results to storage account 
   If you open RunbookScanAgent and search for the scan command text Get-AzSKAzureServicesSecurityStatus and Get-AzSKSubscriptionSecurityStatus, you will find it is scanning for all controls excluding "OwnerAccess" control. This is due to the CA SPN having limited (reader) permissions on the subscription.  
   To make CA scan only thr baseline controls, append parameter '-UseBaselineControls' to these scan commands.
   Follow the same steps as earlier to publish these files to org policy server. 
   After policy update, CA will start scanning only the baseline controls.
   ### Scanning owner and graph access controls using CA
   During CA setup, SPN is assigned with minimum privileges i.e. reader access on subscription and contributor access on AzSKRG. As a reader, it will not be able to scan controls requiring owner or graph read permissions. You can elevate SPN permission to 'Owner' and remove '-ExcludeTags "OwnerAccess"' parameter against the scan commands in above 2 files. As always, follow the same steps tp publish these files to org policy server.
   However, in general we let SPN have minimum permissions assigned and make it a practice for individual teams to perform scan with high privileged role on regular basis to validate Owner access controls.
   ### Reporting critical alerts
   Comming soon
# Org policy usage statistics and monitoring using telemetry
The telemetry data can be leveraged by org policy owners to understand AzSK usage, monitor compliance drift, CA health, resource inventory, troubleshooting etc. All helpful AI queries are listed on page [here](https://github.com/azsk/DevOpsKit-docs/tree/master/06-Security-Telemetry/App-Insights-Queries).
## Frequently Asked Questions
#### I am getting exception "The current subscription has been configured with DevOps kit policy for the '***' Org, However the DevOps kit command is running with a different ('org-neutral') org policy....."?
When your subscription is running under org policy, AzSK marks subscription for that Org. If user is running scan commands on that subscription using Org-neutral policy, it will block those commands as that scan/updates can give invalid results against org policy. You may face this issue in different environments. Below steps will help you to fix issue
**Local Machine:**
- Run “**IWR**" installation command shared by Policy Owner. This will ensure latest version installed with org policy settings.(**Note:** If you are from CSE, please install the AzSK via instructions at https://aka.ms/devopskit/onboarding so that CSE-specific policies are configured for your installation.)
- Run "*Clear-AzSKSessionState*" followed by any scan command and validate its running with org policy. It gets displayed at the start of command execution "Running AzSK cmdlet using ***** policy"
**Continuous Assurance:**
- Run "*Update-AzSKContinuousAssurance*" command with org policy. This will ensure that continuous assurance setup is configured with org policy settings.
- After above step, you can trigger runbook and ensure that after job completion, scan exported in storage account are with org policy. You can download logs and validate it in file under path /ETC/PowerShellOutput.LOG. 
Check for message during start of command "Running AzSK cmdlet using ***** policy"
**CICD:**
- You need to configure policy url in pipeline using step **5** defined [here](https://github.com/azsk/DevOpsKit-docs/tree/master/03-Security-In-CICD#adding-svts-in-the-release-pipeline)
- Make sure that the variables you have configured have correct names and values. You may refer [this table.](https://github.com/azsk/DevOpsKit-docs/blob/master/03-Security-In-CICD/Readme.md#advanced-cicd-scanning-capabilities)
- To validate if pipeline AzSK task is running with org policy. You can download release logs from pipeline. Expand "AzSK_Logs.zip" --> Open file under path "/ETC/PowerShellOutput.LOG" --> Check for message at the start of command execution "Running AzSK cmdlet using ***** policy"