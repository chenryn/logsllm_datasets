[Back to top…](Readme.md#contents)
### Execute SVTs using "-UsePartialCommits" switch
The Get-AzSKAzureServicesSecurityStatus command now supports checkpointing via a "-UsePartialCommits" switch. When this switch is used, the command periodically persists scan progress to disk. That way, if the scan is interrupted or an error occurs, a future retry can resume from the last saved state. This capability also helps in Continuous Assurance scans where Azure currently suspends 'long running' automation jobs by default.The cmdlet below checks security control state via a "-UsePartialCommits" switch:  
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -UsePartialCommits
```
[Back to top…](Readme.md#contents)
### Execute SVTs excluding some resource groups
The Get-AzSKAzureServicesSecurityStatus command now supports a switch 'ExcludeResourceGroupNames' to exclude some of the resource groups from getting scanned. The cmdlet below will not scan the resource groups 'azsktestRg' and 'azsktestRg1'.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeResourceGroupNames "azsktestRg,azsktestRg2"
```
[Back to top…](Readme.md#contents)
### Execute SVTs excluding some resources
The Get-AzSKAzureServicesSecurityStatus command now supports a switch 'ExcludeResourceNames' to exclude some of the resources from getting scanned. The cmdlet below will not scan the resource groups 'azsktestApp' and 'azsktestApp2'.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeResourceNames "azsktestApp,azsktestApp2"
```
[Back to top…](Readme.md#contents)
### Execute SVTs excluding a resource type
The Get-AzSKAzureServicesSecurityStatus command now supports a switch 'ExcludeResourceTypeName' to exclude resources of a particular type supported by AzSK from getting scanned. The cmdlet below will not scan any Databricks resources.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeResourceTypeName Databricks
```
> **Note:** Currently there is provision to exclude only one type of resources using switch '-ExcludeResourceTypeName'. To exclude multiple types of resources from getting scanned the switch'-ExcludeTags' can be used passing the user friendly name for the resource type as specified [here](Readme.md#execute-svts-for-a-specific-resource-type). The cmdlet below will exclude all resources belonging to the type 'AppServices' or 'Databricks' from getting scanned.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeResourceTypeName Databricks -ExcludeTags 'AppService'
```
[Back to top…](Readme.md#contents)
### Execute SVTs excluding some controls from scan
The Get-AzSKAzureServicesSecurityStatus command now supports a switch 'ExcludeControlIds' to exclude AzSK security controls from getting scanned. 
The cmdlet below will not scan 'Azure_Storage_DP_Rotate_Keys' control for any Storage type resource.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeControlIds 'Azure_Storage_DP_Rotate_Keys'
```
The cmdlet below will not scan 'Azure_Storage_DP_Rotate_Keys' and 'Azure_Storage_AuthZ_Allow_Limited_Access_to_Services' control for any Storage type resource.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ExcludeControlIds "Azure_Storage_DP_Rotate_Keys, Azure_Storage_AuthZ_Allow_Limited_Access_to_Services"
```
[Back to top…](Readme.md#contents)
### Generate FixScripts for controls that support AutoFix while executing SVTs
The command below will not only scan the controls for all the resources in the subscription but also produce scripts to fix the controls that support AutoFix. To know if a control supports AutoFix or not, look at the value for the corresponding control under the column *SupportsAutoFix* in the SecurityReport.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -GenerateFixScript"
```
Note that this switch can be used with any variant of the Get-AzSKAzureServicesSecurityStatus command. You can read more about FixScripts [here](https://github.com/azsk/DevOpsKit-docs/tree/master/00c-Addressing-Control-Failures#automatically-generating-fixes-1).
[Back to top…](Readme.md#contents)
### Prevent the output folder from opening automatically at the end of SVTs
When you run an AzSK scan, the output folder containing all the necessary components opens up automatically for you at the end of the scan. If you wish to prevent this, you just need to add the flag *-DoNotOpenOutputFolder* to any variant of the Get-AzSKAzureServicesSecurityStatus command, as shown in the example below.
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -DoNotOpenOutputFolder"
```
[Back to top…](Readme.md#contents)
### Understand the scan reports
Each AzSK cmdlet writes output to a folder whose location is determined as below:
- AzSK-Root-Output-Folder = %LocalAppData%\Microsoft\AzSKLogs  
	```
	E.g., "C:\Users\userName\AppData\Local\Microsoft\AzSKLogs"
	```
- Sub-Folder = Sub_\\\\_\  
	```
	E.g., "Sub_[yourSubscriptionName]\20170321_183800_GSS"  
	```	
Thus, the full path to an output folder might look like:  
```
E.g., "C:\Users\userName\AppData\Local\Microsoft\AzSKLogs\Sub_[yourSubscriptionName]\20170321_183800_GSS\
```
> **Note**: By default, cmdlets open this folder upon completion of the cmdlet (we assume you'd be interested in examining the control evaluation status, etc.)
The contents of the output folder are organized as under:  
![02_Output_Log_Folder](../Images/02_Output_Log_Folder.PNG)
- *\SecurityReport-\.csv*- This is the summary CSV file listing all applicable controls and their evaluation status. This file will be generated only for SVT cmdlets like Get-AzSKAzureServicesSecurityStatus, Get-AzSKSubscriptionSecurityStatus etc.  
- *\\\* - This corresponds to the resource-group or subscription that was evaluated  
	- *\\\.log*- This is the detailed/raw output log of controls evaluated  
- *\Etc*  
	- *\PowerShellOutput.log* - This is the raw PS console output captured in a file.  
	- *\EnvironmentDetails.log* - This is the log file containing environment data of current PowerShell session.  
	- *\SecurityEvaluationData.json* - This is the detailed security data for each control that was evaluated. This file will be generated only for SVT cmdlets like Get-AzSKAzureServicesSecurityStatus, Get-AzSKSubscriptionSecurityStatus etc.
	![02_Etc_Folder_Structure](../Images/02_Etc_Folder_Structure.PNG)
- *\FixControlScripts* - This folder contains scripts to fix the failed controls. The folder is generated only when 'GenerateFixScript' switch is passed and one or more failed controls support automated fixing.  
	- *\README.txt* - This is the help file which describes about the 'FixControlScripts' folder.
You can use these outputs as follows - 
1. The SecurityReport.CSV file provides a quick glimpse of the control results. Investigate those that say 'Verify' or 'Failed'.  
2. For 'Failed' or 'Verify' controls, look in the .LOG file (search for 'failed' or by control-id). Understand what caused the control to fail.
3. For 'Verify' controls, you will also find the SecurityEvaluationData.JSON file handy. 
4. For some controls, you can also use the 'Recommendation' field in the control output to get the PS command you may need to use.
5. Make any changes to the subscription/resource configurations based on steps 2, 3 and 4. 
6. Rerun the cmdlet and verify that the controls you tried to fix are passing now.
[Back to top…](Readme.md#contents)
### Generate output report in PDF format
The Get-AzSKAzureServicesSecurityStatus command now supports generating output report in PDF format using "-GeneratePDF" parameter. You can use this parameter to generate output logs in PDF format. You can use this parameter to generate report either in 'portrait'or 'landscape mode'.The cmdlet below can be used to generate PDF report:  
```PowerShell
Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -GeneratePDF 
```
The parameters required are:
- SubscriptionId – Subscription ID is the identifier of your Azure subscription.  
- GeneratePDF - This accepts either 'None', 'Portrait' or 'Landscape' as inputs.
If you execute SVTs using above command, a new PDF file with name 'SecurityReport' will get generated in the root output logs folder.
The PDF report consists of following sections:
- *Basic Details* - It consists of basic details like subscription id, name, AzSK Version, Date of generation, user, command executed etc.
- *Security Report Summary* -It displays the security status of all the controls Ids which gets scanned.
- *Powershell Output* -It displays the raw PS console output captured during execution of SVTs.
- *Detailed Output* -It displays the detailed/raw output log of controls evaluated.
[Back to top…](Readme.md#contents)
### FAQs
#### What Azure resource types that can be checked?
Below resource types can be checked for validating the security controls in SVT(GRS, GSS and CICD SVT task). please refer [this](../03-Security-In-CICD/Readme.md#arm-template-checker---control-coverage) for supported resource types in ARMChecker) 
| Resource Name |Resource Type Name	|Resource Type|
|-------| ------------- | ----------- |
|Analysis Services |AnalysisService |Microsoft.AnalysisServices/servers|
|API Connection|APIConnection|Microsoft.Web/connections|
|API Management|APIManagement|Microsoft.ApiManagement/service|
|App Services|AppService |Microsoft.Web/sites|
|Automation Account|Automation|Microsoft.Automation/automationAccounts|
|Batch accounts |Batch |Microsoft.Batch/batchAccounts|
|CDN profiles |CDN |Microsoft.Cdn/profiles|
|Cloud Services|CloudService |Microsoft.ClassicCompute/domainNames|
|Container Instances |ContainerInstances |Microsoft.ContainerInstance/containerGroups |
|Container Registry |ContainerRegistry |Microsoft.ContainerRegistry/registries |
|Cosmos DB|Cosmos DB|Microsoft.DocumentDb/databaseAccounts|
|Data Factories |DataFactory |Microsoft.DataFactory/dataFactories|
|Data Lake Analytics|DataLakeAnalytics |Microsoft.DataLakeAnalytics/accounts|
|Data Lake Store|DataLakeStore |Microsoft.DataLakeStore/accounts|
|Express Route-connected Virtual Networks|ERvNet |Microsoft.Network/virtualNetworks|
|Event Hubs|EventHub |Microsoft.Eventhub/namespaces|
|Key Vaults|KeyVault |Microsoft.KeyVault/vaults|
|Kubernetes Service |KubernetesService |Microsoft.ContainerService/ManagedClusters |
|Load Balancer|LoadBalancer|Microsoft.Network/loadBalancers|
|Logic Apps|LogicApps |Microsoft.Logic/Workflows|
|Notification Hubs|NotificationHub |Microsoft.NotificationHubs/namespaces/notificationHubs|
|On-premises Data Gateways |ODG |Microsoft.Web/connectionGateways|
|Redis Caches |RedisCache |Microsoft.Cache/Redis|
|Search services |Search |Microsoft.Search/searchServices|
|Service Bus |ServiceBus |Microsoft.ServiceBus/namespaces|
|Service Fabric clusters |ServiceFabric |Microsoft.ServiceFabric/clusters|
|SQL Databases|SQLDatabase |Microsoft.Sql/servers|
|Storage Accounts|StorageAccount |Microsoft.Storage/storageAccounts|
|Stream Analytics|StreamAnalytics|Microsoft.StreamAnalytics/streamingjobs|
|Traffic Manager profiles |TrafficManager |Microsoft.Network/trafficmanagerprofiles|
|Virtual Machines|VirtualMachine |Microsoft.Compute/virtualMachines|
|Virtual Networks|VirtualNetwork |Microsoft.Network/virtualNetworks|
This list continues to grow so best way to confirm is to look at the output of the following command:  
 ```PowerShell  
Get-AzSKSupportedResourceTypes  
 ```    
>  We regularly add SVT coverage for more Azure features. Please write to us (mailto:PI:EMAIL) if you are looking for SVTs for a service not listed here.  
#### What do the different columns in the status report mean?
Status report will be in CSV format and will contain below columns 
- ControlID - Unique ID for security control.
- Status – { Passed | Failed | Verify | Manual | Error} 
	-  Passed: The resource complies with the security control.
	-  Failed: The resource does not comply with the security control.
	-  Verify: The status needs to be verified using the data generated by the automated script. This is usually an indication that some level of human judgment is required in order to attest to the control status.
	-  Manual: The control is not automated (yet). It should be manually implemented and/or validated.
	-  Error: An error occurred due to which the control state could not be determined.
- FeatureName - Azure feature name e.g. AzureAppService, AzureSQLDB etc.
- ResourceName - Azure resource name. 
- ChildResourceName - Sub resource name of the Azure resource. E.g. for SQL Server, controls validating the databases will have the resource name as ‘SQLServerName’ and child resource name as 'SQLDBName' whereas features having no sub resources will have same value for resource name and child resource name.
- 	ResourceGroupName - Resource group name for resource name.
- 	ControlType - Control type can be ‘TCP’, ‘Best Practice’ or ‘Information’. 
- 	Automated - Yes or No	    
Note that not all security checks are automatable. The 'non-automated' checks (things that have to be manually validated/checked) are also listed in the reports from a completeness standpoint.
- 	Description - Security control description.
- 	Reference - Link to detailed document/explanation.
- 	Recommendation - Recommended steps to implement a fix for a failed control.  
#### What are Owner access controls? Why can't those be run via CA and need to be run manually?   (Or)  I have setup AzSK Continuous Assurance on my subscription. Do I still need to run the scans locally?   Description:  Running the scan locally for all the resources in the subscription is time consuming. Do I still need to run that even though I have already setup Continuous Assurance on my subscription?
Continuous Assurance scans and locally run scans have different permission models. Some of the AzSK controls need elevated permissions (e.g. Owner permissions, GraphRead access etc.). CA being runnning using SPN context, can't scan controls which need such elevated permissions. Note that SPN should not be granted elevated permissions from security stand point.
That's the reason you or anyone on your team who has elevated permissions (as mentioned in the control recommendations) on the subscription; need to run the manual scans periodically.
You can certainly minimize the time taken for the scan by runnning only those controls which are not run by CA.
```