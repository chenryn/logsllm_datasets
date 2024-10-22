	| sort by AggregatedValue desc
	```
- List: The query below shows the list of resource type that have one or more control failing along with the number of controls failing for each resource type.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated > ago(3d) 
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"  
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s 
	| where ControlStatus == "Failed" | summarize AggregatedValue = count() by FeatureName_s 
	| sort by AggregatedValue desc	
	```
**4) Resource Security (RS-2):** This blade shows resources present on your subscription(s) that have some baseline controls failing. The below image depicts the blade:
![05_Log_Analytics_Blade_RS2](/Images/05_Log_Analytics_Blade_RS2.PNG)
- Tile: The query below shows the number of unique resources that have at least one control failing. 
	``` AIQL
	AzSK_CL  
	| where TimeGenerated >ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"  
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s 
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ResourceName_s  
	| count 
	```
- List: The query below shows the the list of resources that have one or more control failing along with the number of failed controls for each resource.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated >ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"  
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s 
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ResourceName_s 
	```
**5) Resource Security (RS-3):** This blade shows resource groups present on your subscription(s) that failed baseline controls. The below image depicts the blade:
![05_Log_Analytics_Blade_RS3](/Images/05_Log_Analytics_Blade_RS3.PNG)
- Tile: The query below shows the number of unique resource groups containing resources that are failing.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated > ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"   
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s  
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ResourceGroup 
	| count
	```
- List: The query below shows list of resource groups that have one or more controls failing along with the number of failed controls for each resource group.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated > ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"   
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s  
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ResourceGroup
	```
**6) Resource Security (RS-4):** This blade shows baseline security controls that are failing on your subscription(s). The below image depicts the blade:
![05_Log_Analytics_Blade_RS4](/Images/05_Log_Analytics_Blade_RS4.PNG)
- Tile: The query below shows the number of unique controls that are failing.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated > ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"   
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s  
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ControlId_s 
	| count 
	```
- List: The query below shows the list of controls that are failing along with the number of failures for each control.
	``` AIQL
	AzSK_CL  
	| where TimeGenerated > ago(3d)  
	| where HasRequiredAccess_b == true and IsBaselineControl_b == true  
	| where FeatureName_s != "SubscriptionCore"   
	| extend ControlStatus = iff(ControlStatus_s == "Passed", "Passed","Failed") 
	| summarize arg_max(TimeGenerated, *) by SubscriptionId, ResourceId, ControlId_s  
	| where ControlStatus == "Failed" 
	| summarize  AggregatedValue = count() by ControlId_s
	```
**7) Useful Queries:** In this last blade, we have included a few queries that you can use as is or tweak to create your own custom queries. These queries are similar to the queries for various other blades except that they will show the status of **all controls** (opposed to baseline controls only). These can be used as a starting point for setting up your own alerts, doing auto-heal, etc. 
[Back to top…](Readme.md#contents)
### Next Steps
Assuming that you have setup the AzSK Monitoring solution and configured AzSK control event routing from one or more of 
the dev ops stages (developer machines (SDL stage), your build environment (CICD stage) and operational environment (CA)) 
with the appropriate Log Analytics settings, you are all set to monitor and act on security issues/drift for your 
cloud subscription and (application) resources across the multiple stages of dev ops.
As next steps, you can modify, customize and enhance the default AzSK Monitoring solution in several interesting ways.
Here are some interesting ideas to pursue:
***Create additional search queries***
Out of the box, the AzSK Monitoring solution provides some common search queries you may find useful. However, you can 
use the Azure Monitor Logs to create and save your own queries that you may find valuable towards monitoring. 
***Setup Alerts in Log Analytics***
Based on threat modeling for critical, alertworthy conditions, you can setup Microsoft Azure alerts based on search
queries. These alerts can be raised over Email or SMS or can also trigger some action (e.g., an auto-correct script) 
via webhooks/runbooks. (For instance, if you know that a particular storage account contains extremely sensitive data, 
you can define a search query and a respective alert for any hint of abnormal activity on that storage account.) 
***Implement 'auto-correction' scripts***
For critical resources which you want to never go out of compliance, you can implement 'auto-correct' scripts 
using search queries to define the condition that should trigger corrective action. For most controls which are 
'auto-correctable', the AzSK can help you generate the 'auto-correct' script by using the -GenerateFixScript flag
in the AzSK scan commands such as Get-AzSKAzureServicesSecurityStatus.
***Create views application-centric views***
You can start by cloning the default view and make modifications to the queries underpinning the individual blades 
to make your own custom views. For example, you can modify the cloned view to monitor specific applications using the AzSK Monitoring solution. 
This can be done simply by filtering the default queries underpinning the blades by resource groups corresponding to 
one or more applications. You could monitor all apps via different blades in the same view or create multiple views - 
one for each application.
***Create views with separate blades for SDL/CICD/CA stages***
You can further refine application-specific views to observe the security status as the application flows through
different dev ops stages. For instance, the view shown below can be generated by querying for AzSK control events 
corresponding to different dev ops stages ("SDL", "CICD", "CA") in respective blades. 
(Note: Events from CA appear with a source tag of "CC" which stands for 'Continuous Compliance' the older name 
for "Continuous Assurance".)
![05_Setting_Log_Analytics_Workspace_App_Specific_View_Details](../Images/05_Setting_Log_Analytics_Workspace_App_Specific_View_Details.png)
[Back to top…](Readme.md#contents)
--------------------------
## Appendix ##
### [A] Creating a Log Analytics workspace ###
**Step-1 (Ops team):** Create a new Log Analytics workspace.
Go [here](https://docs.microsoft.com/en-in/azure/azure-monitor/learn/quick-create-workspace) and follow the simple steps to create a new Log Analytics workspace.
![05_Setting_New_Log_Analytics_Workspace](../Images/05_Setting_New_Log_Analytics_Workspace.png)
**Note:** If you already have a Log Analytics workspace that is used for other monitoring activities, 
then, ideally, the same workspace should be used for setting up the AzSK Monitoring solution as well. 
The idea is that the security views appear alongside other views on the 'general' operations dashboard and 
not in a standalone one.
**Step-2 (Ops Team):** Capture the Workspace ID and Primary Key for the Log Analytics workspace by navigating to "Advanced Settings -> Connected Sources -> Windows Servers".
![05_Log_Analytics_Workspace_WsId_ShrKey](../Images/05_Log_Analytics_Workspace_WsId_ShrKey.png)
### [B] Testing Log Anaytics workspace connectivity ###
Let us look at how to send events to the Log Analytics workspace from AzSK running on a local machine. This is a handy way to 
test connectivity and to see if the  Logs can display the received events.
**Step-1 (App Team):** 
Connect the local (dev box) installation of AzSK to your Log Analytics workspace for sending AzSK control evaluation events.
Run the below in a PS session after logging in to Azure (this assumes that you have the latest AzSK installed).
```PowerShell
 $wsID = 'workspace_ID_here'       #See pictures in [A] above for how to get wsId and shrKey
 $shrKey = 'workspace_PrimaryKey_here'
 Set-AzSKMonitoringSettings -WorkspaceID $wsID -SharedKey $shrKey
```
Close the current PS window and start a new one. (This is required for the new settings to take effect.)
After this, all AzSK cmdlets, SVTs, etc. run on the local machine will start sending events (outcomes of 
security scans) into the Log Analytics repository corresponding to the workspace ID above.
**Step-2 (App Team):** Generate some AzSK events and validate that they are reaching the configured Log Analytics workspace.
Run a few AzSK cmdlets to generate events for the Log Analytics repo. 
For example, you can run one or both of the following:
```PowerShell
 Get-AzSKSubscriptionSecurityStatus -SubscriptionId $subID 
 Get-AzSKAzureServicesSecurityStatus -SubscriptionId $subID -ResourceGroupNames 'app_rg_name'
```
After the above scans finish, if we go into Log Analytics workspace Logs and search for 'AzSK_CL', it should show 
AzSK events similar to the below ("_CL" stands for "custom log"):
![05_Setting_Log_Analytics_Workspace_Custom_Log](../Images/05_Setting_Log_Analytics_Workspace_Custom_Log.png)
If you have already set the AzSK Monitoring solution up, you will also be able to see these in pictorial form
in the AzSK Log Analytics Workspace Summary (Overview). However, the workspace summary can be setup later as it is not required just to check if 
the events are being sent into the Log Analytics workspace.
### [C] Routing AzSK events to Log Analytics
Note that the Security Verification Tests (SVTs) from AzSK can be run in 3 stages:
1. Development (referred to as "SDL")
2. Build/Deployment ("CICD")
3. Continuous Assurance ("CA")
The results of control evaluation generated by running AzSK SVTs in **all** of these stages can be 
(independently) sent to Log Analytics. Depending on the dev ops stage the mechanism used to 'wire up' AzSK with Log Analytics is different. 
1. In the development ("SDL") stage, the following command can be used to set the Log Analytics workspace that will collect events 
generated via various AzSK-scripts/SVTs etc. in a subscription:
```PowerShell
 Set-AzSKMonitoringSettings -WorkspaceId  -SharedKey 
```
Basically, after the above command is run (once) on your desktop, subsequent AzSK SVT control evaluation events will be sent
to the Log Analytics workspace configured above. 
> Note: You will need to close and reopen PS session after running the above command for the setting change to take effect.
2. In the build/deployment (CICD) stage, Log Analytics settings are specified via input parameters for the [AzSK SVTs build/release extension](../03-Security-In-CICD/Readme.md#adding-svts-in-the-release-pipeline).
3. For Continuous Assurance (CA), the Log Analytics workspace info is specified in the input parameters of the [Continuous Assurance setup script](../04-Continous-Assurance/Readme.md#setting-up-continuous-assurance---step-by-step).  
Events sent from these (different dev ops) stages of one or more applications get aggregated 
in the Log Analytics workspace alongside events from various out-of-box solutions available in the Log Analytics Solution gallery.   
Overall, this provides a single pane view of the security across the entire set of cloud resources in 
a subscription. A schematic of this (aggregate view model) is shown below:
> Note AzSK control evaluation results (AzSK events) show up as Type=AzSK_CL in the Log Analytics workspace.
[Back to top…](Readme.md#contents)
### [D] Leveraging other Management Solutions from the Azure Marketplace ###
The Azure Monitor contains several out of the box solutions that are invaluable to use towards 
a comprehensive coverage of monitoring and alerts of various Azure resource types. Many resources generate
a rich set of 'data plane' diagnostics and logs which can be routed into a Log Analytics dashboard for monitoring
using these solutions. In the part, we will look at how to leverage a couple of common solutions. You can
add more based on the specific resources (SQL, VM, Service Fabric, Key Vault, etc.) you are using in your subscription.
The AzSK solution complements the coverage from these individual solutions by its focus on cloud resource configuration.
It is also unique in its coverage of events across dev ops stages.
You can read more about intalling a Management Solution to Log Analytics workspace [here](https://docs.microsoft.com/en-in/azure/azure-monitor/insights/solutions#install-a-management-solution).
> **Note**: Setting up other solutions from the Azure Marketplace is not required for the AzSK Monitoring Solution to work.
**Step-1: Optional** (Ops Team) Configure alerts on Analytics queries.
Read more about setting up Log alerts [here](https://docs.microsoft.com/en-in/azure/azure-monitor/platform/alerts-log).
**Step-2: Optional** (Ops Team) Collect and analyze Azure activity logs in Log Analytics
Below are the steps to connect to a log source:
1. This connection is setup in the Log Analytics subscription by going into the Log Analytics workspace feature and 
clicking on "Azure Activity Log" in the Workspace Data Sources list as below:
![05_Setting_OMS_Workspace_Azure_Activity_Log](../Images/05_Setting_Log_Analytics_Workspace_Azure_Activity_Log.png)  
2. From the Log Analytics Subscription, one can view all subscriptions that the Ops team person (current user) 
has at least "Log Analytics Reader" level access. It means that App team 
subscriptions will show here as an option only if at least "Log Analytics Reader" access is granted to the 
current Log Analytics user.
Choose the subscription(s) corresponding to the apps that are being monitored and click 'Connect'.
![05_Setting_Log_Analytics_Workspace_Connecting_Log_Analytics](../Images/05_Setting_Log_Analytics_Workspace_Connecting_Log_Analytics.png)
> Note: The above steps have to be done from the **Log Analytics** subscription.
At this point, the app subscription is setup to pipe it's Azure Activity Log events to the Log Analytics workspace. 
In the next steps we will configure AzSK to send data to the Log Analytics workspace from a PowerShell session. This can be done by running commands discussed in [[B] Testing Log Anaytics workspace connectivity](Readme.md#b-testing-log-anaytics-workspace-connectivity).
This is just so that we can verify that events generated AzSK are getting routed to the Log Analytics workspace
correctly. 