Ability to customize naming of severity levels of controls (e.g., instead of High/Medium, etc. one can now have Important/Moderate, etc.) with the changes reflecting in all avenues (manual scan results/CSV, Log Analytics workspace, compliance summaries, dashboards, etc.)
###### Steps: 
 i) Edit the ControlSettings.json file to add a 'ControlSeverity' object as per below:
```JSON
{
   "ControlSeverity": {
    "Critical": "Critical",
    "High": "Important",
    "Medium": "Moderate",
    "Low": "Low"
  }
}
```
 ii) Save the file
 iii) Run the policy setup command (the same command you ran for the first-time setup)
 ###### Testing: 
Someone in your org can test this change using the `Get-AzSKAzureServicesSecurityStatus`. You will see that
the controls severity shows as `Important` instead of `High` and `Moderate` instead of `Medium` in the output CSV.
### Managing policy/advanced policy usage
#### Downloading and examining policy folder
After installing org policy, you must have observed that the command creates policy folder in local machine with some default folders and files. 
If you don't have policies, you can always download them using the following command:
```PowerShell
Get-AzSKOrganizationPolicyStatus -SubscriptionId  `
         -OrgName "Contoso" `
         -DepartmentName "IT" `
         -DownloadPolicy `
         -PolicyFolderPath "D:\ContosoPolicies"
```
These files are uploaded to the policy storage as well. You can recollect the function of each of these files from [here.](Readme.md#basic-files-setup-during-policy-setup)
#### Working with ‘local’ mode (policy dev-test-debug)
You can run the scan pointing to the local policy present on your dev box using the following steps. It will enable you test the policy customizations before pushing those to the server. 
Step 1: Point AzSK settings to local org policy folder("D:\ContosoPolicies\"). 
```PowerShell
Set-AzSKPolicySettings -LocalOrgPolicyFolderPath "D:\ContosoPolicies\"
```
This will update "AzSKSettings.json" file present at location "%LocalAppData%\Microsoft\AzSK" to point to local folder instead of server storage.
You can run Get-AzSKInfo (GAI) cmdlet to check the current AzSK settings. It will show OnlinePolicyStoreUrl as policyFolder path (instead of the blob URL). 
   ```PowerShell
   GAI -InfoType HostInfo
   ```
![Local Host Settings](../Images/07_OrgPolicy_LocalSettings.PNG)
Step 2: Perform the customization to policy files as per scenarios. 
Here you can customize the list of baseline or preview baseline controls for your org using steps already explained [here](Readme.md#d-creating-a-custom-control-baseline-for-your-org) (excluding the last step of running the policy setup or policy update command.)
Step 3: Now you run scan to see policy updates in effect. Clear session state and run scan commands (GRS or GSS) with parameters sets for which config changes are done like UseBaselineControls,ResourceGroupNames, controlIds etc.
```PowerShell
# Clear AzSK session cache for settings
Clear-AzSKSessionState
# Run subscription scan using local policy settings
Get-AzSKSubscriptionSecurityStatus -SubscriptionId 
# Run services security scan with baseline using local policy settings
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -UseBaselineControls
```     
Step 3: If scan commands are running fine with respect to the changes done to the configuration, you can update policy based on parameter set used during installations. If you see some issue in scan commands, you can fix configurations and repeat step 2. 
```PowerShell
Update-AzSKOrganizationPolicy -SubscriptionId  `
   -OrgName "Contoso" `
   -DepartmentName "IT" `
   -PolicyFolderPath "D:\ContosoPolicies"
#If custom resources names are used during setup, you can use below parameters to download policy
Update-AzSKOrganizationPolicy -SubscriptionId  `
   -OrgName "Contoso-IT" `           
   -ResourceGroupName "Contoso-IT-RG" `
   -StorageAccountName "contosoitsa" `
   -AppInsightName "ContosoITAppInsight" `
   -PolicyFolderPath "D:\ContosoPolicies"
```
Step 4: Validate if policy is correctly uploaded and there are no missing mandatory policies using policy health check command
**Note:**
It is always recommended to validate health of org policy for mandatory configurations and policy schema syntax issues using below command. You can review the failed checks and follow the remedy suggested.
```PowerShell
Get-AzSKOrganizationPolicyStatus -SubscriptionId  `
           -OrgName "Contoso" `
           -DepartmentName "IT"
#If you have used customized resource names, you can use below parameter sets to run health check
Get-AzSKOrganizationPolicyStatus -SubscriptionId  `
           -OrgName "Contoso-IT" `
           -ResourceGroupName "RGName" `
           -StorageAccountName "PolicyStorageAccountName" 
```
Step 5: If all the above steps works fine, you can point back your AzSK setting to online policy server by running "IWR" command generated at the end of *Update-AzSKOrganizationPolicy*
You can also set up a 'Staging' environment where you can do all pre-testing of policy setup, policy changes, etc. A limited number of 
people could be engaged in testing the actual end user effects of the policy changes before deploying them for broader usage. 
Also, you can choose to retain the staging setup or just re-create a fresh one for each major policy change.
For your actual (production) policies, we recommend that you check them into source control and use the local clone of *that* folder as the location
for the AzSK org policy setup command when uploading to the policy server. In fact, setting things up so that any policy
modifications are pushed to the policy server via a CICD pipeline would be ideal. (That is how we do it at CSE.)
Refer [maintaining policy in source-control]() and [deployment using CICD pipeline]().
#### Troubleshooting common issues 
Here are a few common things that may cause glitches and you should be careful about:
- Make sure you use exact case for file names for various policy files (and the names must match case-and-all
with the entries in the ServerConfigMetadata.json file)
- Make sure that no special/BOM characters get introduced into the policy file text. (The policy upload code does scrub for
a few known cases, but we may have missed the odd one.)
- Note that the policy upload command always generates a fresh installer.ps1 file for upload. If you want to make changes to 
that, you may have to keep a separate copy and upload it. (We will revisit this in future sprints.)
### How to upgrade org AzSK version to the latest AzSK version
DevOps kit team releases the newer version of the AzSK module on 15th of every month. It is recommended that you upgrade your org's AzSK version to the latest available version to ensure that your org is up to date with the latest security controls and features. You need to follow the steps below to smoothly upgrade AzSK version for your org: 
1. Install latest AzSK module in your local machine with the help of common setup command
   ```PowerShell
   # Use -Force switch as and when required 
   Install-Module AzSK -Scope CurrentUser -AllowClobber
   ```
2. Go through the [release notes](https://azsk.azurewebsites.net/ReleaseNotes/LatestReleaseNotes.html) for AzSK latest version. It typically lists the changes which may impact org policy users under section 'Org policy/external user updates'.
3. If the release notes indicate that you need to perform any additional steps before upgrading the org policy version then perform those changes with the help of [org policy updates page](OrgPolicyUpdate.md). It is highly recommended that you do these changes to your local policy folder and test those before pushing to the policy server. Instructions at [downloading your existing org policies](Readme.md#downloading-and-examining-policy-folder) and [Working with ‘local’ mode (policy dev-test-debug)](Readme.md#working-with-local-mode-policy-dev-test-debug) would be useful to do so. 
If there are no additional steps mentioned, then you can go ahead with next step. 
5. Run UOP with AzSK version update flag
   ```PowerShell
   # For Basic Setup
   Update-AzSKOrganizationPolicy -SubscriptionId  `
      -OrgName "Contoso" `
      -DepartmentName "IT" `
      -PolicyFolderPath "D:\ContosoPolicies" -OverrideBaseConfig OrgAzSKVersion
   #For custom Resource Group Setup
   Update-AzSKOrganizationPolicy -SubscriptionId  `
      -OrgName "Contoso-IT" `           
      -ResourceGroupName "Contoso-IT-RG" `
      -StorageAccountName "contosoitsa" `
      -PolicyFolderPath "D:\ContosoPolicies" -OverrideBaseConfig OrgAzSKVersion
   ```
 Internally, this will update the AzSK version in the AzSK.Pre.json file present on your org policy server.. 
#### Upgrade scenarios in different scan sources
Once org policy is updated with the latest AzSK version, you will see it in effect in all environments
 **Local scans:** If application teams are using older version(or any other version than mentioned in org policy), they will start seeing warning as shown below while running scans.
![Entry in ServerConfigMetadata.json](../Images/07_OrgPolicy_Old_Version_Warning.PNG)
**Continuous Assurance:** CA will auto-upgrade to latest org version when the next scheduled job runs. You can monitor upgrade status with the help of application insight events. Use below query in org AI 
 ``` AI Query
| customEvents
| where timestamp >= ago(6d)
| where name == "Control Scanned"
| where customDimensions.ScanSource =="Runbook"
| where customDimensions.ScannerModuleName == "AzSK"
| summarize arg_max(timestamp, *) by SubId = tostring(customDimensions.SubscriptionId)
| summarize CAModuleVersionSummary= count() by Version = tostring(customDimensions.ScannerVersion)
| render piechart
 ```
 ![CAVersionSummary.json](../Images/07_OrgPolicy_CAVersionSummary.PNG)
 **CICD:** As of now, CICD SVT task does not support version from org policy settings. It always installs latest AzSK version available in PowerShell gallery, irrespective of version mentioned in policy. Although it refers other control policies from policy store.
### Maintaining policy in source-control
Coming soon
### Policy deployment using CICD pipeline
Coming soon
# Create security compliance monitoring solutions
Once you have an org policy setup running smoothly with multiple subscriptions across your org, you will need a solution that provides visibility of security compliance for all the subscriptions across your org. This will help you drive compliance/risk governance initiatives for your organization. 
When you setup your org policy endpoint (i.e. policy server), one of the things that happens is creation of an Application Insights workspace for your setup. After that, whenever someone performs an AzSK scan for a subscription that is configured to use your org policy, the scan results are sent (as 'security' telemetry) to your org's Application Insights workspace. Because this workspace receives scan events from all such subscriptions, it can be leveraged to generate aggregate security compliance views for your cloud-based environments. 
## Create cloud security compliance report for your org using PowerBI
We will look at how a PowerBI-based compliance dashboard can be created and deployed in a matter of minutes starting with a template dashboard that ships with the AzSK. All you need apart from the Application Insights instance is a CSV file that provides a mapping of your organization hierarchy to subscription ids (so that we know which team/service group owns each subscription).
> Note: This is a one-time activity with tremendous leverage as you can use the resulting dashboard (example below) towards driving security governance activities over an extended period at your organization. 
#### Step 0: Pre-requisites
To create, edit and publish your compliance dashboard, you will need to install the latest version of PowerBI desktop on your local machine. Download it from [here](https://powerbi.microsoft.com/en-us/desktop/).
#### Step 1: Prepare your org-subscription mapping
In this step you will prepare the data file which will be fed to the PowerBI dashboard creation process as the mapping from subscription ids to the org hierarchy within your environment. The file is in a simple CSV form and should appear like the one below. 
> Note: You may want to create a small CSV file with just a few subscriptions for a trial pass and then update it with the full subscription list for your org after getting everything working end-to-end.
A sample template for the CSV file is [here](./TemplateFiles/OrgMapping.csv):
![Org-Sub metadata json](../Images/07_OrgPolicy_PBI_OrgMetadata.PNG) 
The table below describes the different columns in the CSV file and their intent.
| ColumnName  | Description | Required? | Comments |
| ---- | ---- | ---- |---- |
| BGName | Name of business group (e.g., Finance, HR, Marketing, etc.) within your enterprise | Yes |  This you can consider as level 1 hierarchy for your enterprise | 
| ServiceGroupName | Name of Service Line/ Business Unit within an organization | Yes |  This you can consider as level 2 hierarchy for your enterprise | 
| SubscriptionId | Subscription Id belonging to a org/servicegroup | Yes |   | 
| SubscriptionName | Subscription Name | Yes | This should match the actual subscription name. If it does not, then the actual name will be used.  | 
| IsActive | Use "Y" for Active Subscription and "N" for Inactive Subscription  | Yes | This will be used to filter active and inactive subscriptions .| 
| OwnerDetails | List of subscription owners separated by semi-colons (;)  | Yes | These are people accountable for security of the subscription.  | 
> **Note**: Ensure you follow the correct casing for all column names as shown in the table above. The 'out-of-box' PowerBI template is bound to these columns. If you need additional columns to represent your org hierarchy then you may need to modify the template/report as well.
#### Step 2: Upload your mapping to the Application Insights (AI) workspace
In this step you will import the data above into the AI workspace created during org policy setup. 
 **(a)** Locate the AI resource that was created during org policy setup in your central subscription. This should be present under org policy resource group. After selecting the AI resource, copy the Instrumentation Key.
 **(b)** To push org Mapping details, copy and execute the script available [here](./Scripts/OrgPolicyPushOrgMappingEvents.txt).
 > **Note**: Due to limitation of application insight, you will need to repeat this step every 90 days interval. 
#### Step 3: Create a PowerBI report file
In this section we shall create a PowerBI report locally within PowerBI Desktop using the AI workspace from org policy subscription as the datasource. We will start with a default (out-of-box) PowerBI template and configure it with settings specific to your environment. 
> Note: This step assumes you have completed Step-0 above!
**(a)** Get the ApplicationId for your AI workspace from the portal as shown below:
![capture applicationInsights AppId](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_10.PNG)
**(b)** Download and copy the PowerBI template file from [here](https://github.com/azsk/DevOpsKit-docs/blob/master/07-Customizing-AzSK-for-your-Org/TemplateFiles/AzSKComplianceReport.pbit) to your local machine.
**(c)** Open the template (.pbit) file using PowerBI Desktop, provide the AI ApplicationId and click on 'Load' as shown below:
![capture applicationInsights AppId](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_11.PNG)
**(d)** PowerBI will prompt you to login to the org policy subscription at this stage. Authenticate using your user account. (This step basically allows PowerBI to import the data from AI into the PowerBI Desktop workspace.)
![Login to AI](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_12.PNG)
Once you have successfully logged in, you will see the AI data in the PowerBI report along with org mapping as shown below: 
![Compliance summary](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_13.PNG)
The report contains 2 tabs. There is an overall/summary view of compliance and a detailed view which can be used to see control 'pass/fail' details for individual subscriptions. An example of the second view is shown below:
![Compliance summary](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_14.PNG)
> TBD: Need to add steps to control access to the detailed view by business group. (Dashboard RBAC.) 
#### Step 4: Publish the PowerBI report to your enterprise PowerBI workspace
**(a)** Before publishing to the enterprise PowerBI instance, we need to update AI connection string across data tables in the PowerBI report. The steps to do this are as below:
[a1] Click on "Edit Queries" menu option.
![Update AI Connection String](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_15.PNG)
[a2] Copy the value of "AzSKAIConnectionString"
![Update AI Connection String](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_16.PNG)
[a3] Replace the value of "AzSKAIConnectionString" with the actual connection string (e.g., AzSKAIConnectionString => "https://api.applicationinsights.io/v1/apps/[AIAppID]/query"). You should retain the "" quotes in the connection string.
![Update AI Connection String](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_17.PNG)
[a4] Repeat this operation for ControlResults_AI, Subscriptions_AI, and ResourceInventory_AI data tables.
[a5] Click on "Close and Apply".
**(b)** You can now publish your PBIX report to your workspace. The PBIX file gets created locally when you click "Publish".
Click on Publish
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_18.PNG)
Select destination workspace
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_19.PNG)
Click on "Open [Report Name] in Power BI" 
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_21.png)
**(c)** Now report got published successfully. You can schedule refresh for report with below steps
Go to Workspace --> Datasets --> Click on "..." --> Click on "Schedule Refresh"
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_22.png)
Click on "Edit credentials"
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_25.png)
Sign in with account with which policy is created
![Publish PBIX report](../Images/07_OrgPolicy_PBI_OrgMetadata_AI_26.png)
Add refresh scheduling timings and click on "Apply"