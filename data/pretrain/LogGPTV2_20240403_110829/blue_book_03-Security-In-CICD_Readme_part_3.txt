### Scan the security health of your ARM Template
The ARM Template health check script can be run using the command below after replacing ``
 with the path of your ARM Template
```PowerShell
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath  
```
The parameters used are:
- ARMTemplatePath – Path to ARM Template file or folder
[Back to top…](Readme.md#contents)
### Execute ARM Template Checker in Baseline mode
In 'baseline mode' a centrally defined 'control baseline' is used as the target control set for scanning.
The cmdlet below scans ARM Template in Baseline mode and generates a status report:
```PowerShell
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath   -UseBaselineControls
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath  -UsePreviewBaselineControls
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath   -UseBaselineControls -UsePreviewBaselineControls
```
### Execute ARM Template Checker for specific controls
The Get-AzSKARMTemplateSecurityStatus command now supports a switch 'ControlIds' to scan only specific controls in ARM Template. 
The cmdlet below will only scan 'Azure_AppService_Deploy_Use_Latest_Version' and 'Azure_AppService_AuthN_Use_Managed_Service_Identity' controls for the provided ARM Template.
```PowerShell
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath  -ControlIds 'Azure_AppService_Deploy_Use_Latest_Version,Azure_AppService_AuthN_Use_Managed_Service_Identity'
```
### Execute ARM Template Checker excluding some controls from scan
The Get-AzSKARMTemplateSecurityStatus command now supports a switch 'ExcludeControlIds' to exclude ARM Template controls from getting scanned. 
The cmdlet below will not scan 'Azure_AppService_Deploy_Use_Latest_Version' control for the provided ARM Template.
```PowerShell
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath  -ExcludeControlIds 'Azure_AppService_Deploy_Use_Latest_Version'
```
### Execute ARM Template Checker for specific control severity
The Get-AzSKARMTemplateSecurityStatus command now supports a parameter 'Severity' to scan controls of specified severities. 
The cmdlet below will not scan 'Azure_AppService_Deploy_Use_Latest_Version' control for the provided ARM Template.
```PowerShell
Get-AzSKARMTemplateSecurityStatus –ARMTemplatePath  -Severity "High , Medium"
```
### ARM Template Checker - Control coverage
ARM Template checker covers Baseline controls for following services:
|FeatureName|Resource Type|
|-----------|-------------|
| AppService |Microsoft.Web/sites|
| CDN |Microsoft.Cdn/profiles|
| CosmosDB |Microsoft.DocumentDb/databaseAccounts|
| DataLakeStore |Microsoft.DataLakeStore/accounts|
| RedisCache |Microsoft.Cache/Redis|
| SQLDatabase |Microsoft.Sql/servers|
| Storage |Microsoft.Storage/storageAccounts|
| TrafficManager |Microsoft.Network/trafficmanagerprofiles|
| ServiceFabric |Microsoft.ServiceFabric/clusters|
| Kubernetes |Microsoft.ContainerService/ManagedClusters|
| LogicApps |Microsoft.Logic/workflows|
| ContainerRegistry |Microsoft.ContainerRegistry/registries|
| KeyVault |Microsoft.KeyVault/vaults|
| VirtualNetwork |Microsoft.Network/virtualNetworks|
| Search |Microsoft.Search/searchServices|
| EventHub |Microsoft.EventHub/namespaces|
| ContainerInstances |Microsoft.ContainerInstance/containerGroups|
| HDInsight |Microsoft.HDInsight/clusters|
| APIManagement |Microsoft.ApiManagement/service|
| PostgreSQL |Microsoft.DBforPostgreSQL/servers|
| MySQL |Microsoft.DBforMySQL/servers|
| Analysis Services |Microsoft.AnalysisServices/servers|
ARM Templates for reference are available [here](../ARMTemplates).
### ARM Template Checker Scan - How to fix findings?
Get-AzSKARMTemplateSecurityStatus cmdlet generate outputs which are organized as under: 
- summary information of the control evaluation (pass/fail) status in a CSV file,
- detailed powershell output log in a LOG file
To address findings, you should do the following:
1. See the summary of control evaluation first in the CSV file. (Open the CSV in XLS. Use "Format as Table", "Hide Columns", "Filter", etc.)
2. Review controls that are marked as "Failed", "Verify" or "Manual"
3. Use the following approach based on control status:
     - For the “Verify” controls, look at the expected property, expected value and description column in .CSV file to decide whether to consider the    control as "Passed" or not. 
     - For the “Failed” controls, look at the .CSV file to get the supporting information like expected property, expected value, line no. and resource path etc.
> **Note**: If 'ExpectedProperty' column in .CSV file contains multiple properties (for e.g. $.properties.siteConfig.alwaysOn | $.properties.alwaysOn), in this case you only need to provide expected value in anyone of these properties to fix the failed control.
#### Scan multiple ARM Templates :-	 
To scan multiple ARM Templates at a time you can pass folder path containing different ARM Template(s) to “–ARMTemplatePath” parameter in “Get-AzSKARMTemplateSecurityStatus” cmdlet.
e.g. :
```PowerShell
 Get-AzSKARMTemplateSecurityStatus  –ARMTemplatePath "D:\DSRE\TestARMChecker\" [-Recurse]
```
> **Note**: You need to pass “-Recurse” switch in cmdlet if you want to scan ARM Templates in the specified location and in all child folders of the location.
[Back to top...](Readme.md#contents)	
### Enable AzSK extension for your VSTS
This extension has been published to the VSTS gallery under "Build and Release" category. 
You can now install this extension from the Marketplace directly (https://marketplace.visualstudio.com/items?itemName=azsdktm.AzSDK-task).
> **Note:** You can also install this extension on your on-prem TFS instance. Please follow the instructions detailed at:
> https://docs.microsoft.com/en-us/vsts/marketplace/get-tfs-extensions
### Walkthrough
This part assumes that you are familiar with VS build tasks and pipelines at a basic level. To demonstrate 
the capability of the feature, we will use a basic ARMTemplate that is checked into our trial repository. 
Our goal is to show how ARM checker can be injected into the build/release workflow so that security testing for 
Azure resources can be done before deployment of ARM Template seamlessly in CICD.  
[Back to top...](Readme.md#contents)
### Adding ARM Template Checker in VSTS pipeline
**Step-1:** Create a release definition or open an existing one.   
As shown below, currently the release definition is configured to simply deploy a ARM Template using Azure Powershell script. This is likely to be the state of any working CICD pipeline that deploys a ARM Template from VSTS to an Azure subscription.
Let us take a look at the steps needed to add the AzSK-ARM Template Checker task to the release definition.
![03_Create_Release_Definition](../Images/03_Create_Release_Definition_ARM.JPG)
**Step-2:** Add the AzSK-ARM Template Checker release task to the pipeline.
Click on "Add Tasks", and select "AzSK ARM Template Checker".
Click on "Add" and "Close".
> **Note:** The VSTS dialog doesn't provide a good visual indication but the task does 
get added when you click "Add" once!
![03_Task_Catalog](../Images/03_Task_Catalog_ARM.JPG)
**Step-3:** Specify the input parameters for the ARM Checker task.
The "AzSK ARM Template Checker" task starts showing in the "Run on Agent" list and displays some configuration inputs that are required for the task to run. These are none other than the familiar options we have been specifying while running the AzSK ARM Template Checker manually - you can specify the target ARM Template file path or a folder path based on your requirement.
Along with input parameter, you can check for below options
**Recurse:** Switch this if you want to scan ARM Templates in the specified location and in all child folders of the location.
**Do not auto-update AzSK:** Switch to toggle auto update of AzSK and required Az modules on the build server. Keep this un-checked for Hosted agent and Hosted VS2017 and while using SVT task fot the first time and if you want to update AZSK the version of AzSK. 
![03_IP_Parameter_for_Task](../Images/03_IP_Parameter_for_Task_ARM.JPG)
**Step-4**: Specify AzSKServerURL and EnableServerAuth variables if you want to use your own org-policy. Please follow this [link](../07-Customizing-AzSK-for-your-Org#how-does-azsk-use-online-policy) to understand how does AzSK use online policy.
AzSKServerURL -> AzSK OnlinePolicyStoreUrl
EnableServerAuth -> EnableAADAuthForOnlinePolicyStore
![ARMChecker_Orgpolicy_Variables](../Images/ARMChecker_Orgpolicy_Variables.jpg)
**Step-5**: Save the Release Definition.
[Back to top...](Readme.md#contents)
### Verifying that the ARM Template Checker have been added and configured correctly
**Step-1:** Start the release pipeline. 
This can be done by adding a new release for an existing build (or trigger a new release via a minor/trial 
check-in). 
![03_Start_Release_Pipeline](../Images/03_Start_Release_Pipeline_ARM.JPG)
**Step-2:** Verify that the release pipeline has started. 
Once the release is triggered, we can see that it is in progress by clicking on "Releases" (or via 
"Build & Release" menu in the VSTS menu).
![03_Verify_Pipeline](../Images/03_Verify_Pipeline_ARM.JPG)
**Step-3:** View the release outcome.  
In a few minutes the release pipeline should complete and we can view the outcomes as shown below (in the 
pic below we can see that the release pipeline has failed):
![03_View_Release_OutCome](../Images/03_View_Release_OutCome_ARMChecker.png)
**Step-4:** Look at the "Issues" to see why the release failed.  
The summary output shows the cause of failure (in this case it is because the AzSK ARM Template Checker have failed).
![03_Issues_Release_Fail](../Images/03_Issues_Release_Fail_ARM.JPG)
**Step-5:** Look at the complete output log of the ARM Checker portion of the release pipeline execution . Notice how the output is the same as what is displayed when ARM Template Checker cmdlet manually run in a PS console.
![03_Release_Task](../Images/03_Release_Task_ARM.JPG)
**Step-6:** See the summary "CSV" and detailed "LOG" output files for the AzSK_ARMTemplateChecker. 
This is no different than the "ad hoc ARM Template Checker run" scenarios. Note, above, how the ARM Template Checker outputs the location of the "CSV" file and the "LOG" file at the end of the run. However, those locations are on the release 
agent machine. These are also packaged up in an overall ZIP file and are available to download. The 
overall ZIP file can be downloaded by clicking on the "Download all logs as ZIP" option.  
The ZIP file "ReleaseLogs_dd.zip" contains LOGs from the entire release pipeline including the master 
output for the AzSK_ARMTemplateChecker. The CSV file and the LOG file for AzSK ARM Template Checker are embedded in the 'inner' ZIP 
file that is named as ArmTemplateChecker_Logs_yyyymmdd_hhmmss.zip .
![03_Output_Folder](../Images/03_Output_Folder_ARM.JPG) 
Opening/extracting the "ArmTemplateChecker_Logs" ZIP file will reveal a folder structure and files placement identical to 
what we have seen in the case of ad hoc ARMChecker runs:
![03_AzSDK_Logs](../Images/03_ARMChecker_Logs.JPG)
[Back to top...](Readme.md#contents)
### Exclude files from scan
To scan multiple ARM Templates at a time you can pass folder path containing different ARM Template(s) but it is possible that folder may contain some ARM Template(s) that are not valid or currently not supported by ARM Checker. In this case AzSK ARM Template Checker Task will skip those file(s) and will fail.
![03_SkippedFile_Error_ARMChecker](../Images/03_SkippedFile_Error_ARMChecker.JPG)
The overall ZIP file can be downloaded by clicking on the "Download all logs as ZIP" option. The ZIP file "ReleaseLogs_dd.zip" contains LOGs from the entire release pipeline including the master output for the AzSK_ARMTemplateChecker. The CSV file and the LOG file for   AzSK ARM Template Checker are embedded in the 'inner' ZIP file that is named as ArmTemplateChecker_Logs_yyyymmdd_hhmmss.zip . Download "ArmTemplateChecker_Logs" ZIP file and then Open/extract the "ArmTemplateChecker_Logs". It will contains SkippedFiles.LOG file along with other files. On opening this file you will get list of all file(s) skipped during scan. 
![03_Skipped_Files_Log_ARMChecker](../Images/03_Skipped_Files_Log_ARMChecker.JPG)
In such case you can exclude files from scan using "Exclude Files" input, you need to pass name of the files (comma separated) you want to exclude in "Exclude Files" input as shown in image below:
![03_ExcludeFiles_Param_ARMChecker](../Images/03_ExcludeFiles_Param_ARMChecker.JPG)
[Back to top...](Readme.md#contents)
### Skip certain controls during scan
AzSK ARM Template Checker will fail if any security control will fail for provided ARM Template. But in some case it may be possible that some controls failure you don't want to fix. In such case you can skip specific controls from scan using below step:
**Step-1:** The overall ZIP file can be downloaded by clicking on the "Download all logs as ZIP" option. The ZIP file "ReleaseLogs_dd.zip" contains LOGs from the entire release pipeline including the master output for the AzSK_ARMTemplateChecker. The CSV file and the LOG file for AzSK ARM Template Checker are embedded in the 'inner' ZIP file that is named as ArmTemplateChecker_Logs_yyyymmdd_hhmmss.zip . Opening/extracting the "ArmTemplateChecker_Logs" ZIP file will reveal a folder structure and files placement as shown below:
![03_ARMChecker_Logs](../Images/03_ARMChecker_Logs.JPG)
**Step-2:** Open CSV file and start editing, keep only those controls with failed status which you want to skip from scan.