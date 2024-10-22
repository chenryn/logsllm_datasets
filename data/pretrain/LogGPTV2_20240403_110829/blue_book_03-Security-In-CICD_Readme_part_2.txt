The first permission is required so that the SVTs can scan resources for security issues successfully and the second permission is requires so that any past attestations for controls are respected by the scan.
[Back to top...](Readme.md#contents)
### Verifying that the SVTs have been added and configured correctly
**Step-1:** Start the release pipeline. 
This can be done by adding a new release for an existing build (or trigger a new release via a minor/trial 
check-in). 
![03_Start_Release_Pipeline](../Images/03_Start_Release_Pipeline.PNG)
**Step-2:** Verify that the release pipeline has started. 
Once the release is triggered, we can see that it is in progress by clicking on "Releases" (or via 
"Build & Release" menu in the VSTS menu).
![03_Verify_Pipeline](../Images/03_Verify_Pipeline.PNG)
**Step-3:** View the release outcome.  
In a few minutes the release pipeline should complete and we can view the outcomes as shown below (in the 
pic below we can see that the release pipeline has failed):
![03_View_Release_OutCome](../Images/03_View_Release_OutCome.PNG)
**Step-4:** Look at the "Issues" to see why the release failed.  
The summary output shows the cause of failure (in this case it is because the AzSK SVTs have failed).
![03_Issues_Release_Fail](../Images/03_Issues_Release_Fail.PNG)
**Step-5:** Look at the complete output log of the AzSK portion of the release pipeline execution . 
Clicking on the "Security controls are failing" text (in the pic above) and, further, clicking on 
the "AzSK_SVTs" link (in the pic below) will show the details about the SVT execution and failures. 
Notice how the output is the same as what is displayed when SVTs are manually run in a PS console!
Essentially, the AzSK_SVTs extension gives us the capability to mirror the secure configuration state
that was established during the development/prototyping phases.
![03_Release_Task](../Images/03_Release_Task.PNG)
**Step-6:** See the summary "CSV" and detailed "LOG" output files for the AzSK SVTs.  
This is no different than the "ad hoc SVT run" scenarios. Note, above, how the SVT outputs the location 
of the "CSV" file and the "LOG" file at the end of the run. However, those locations are on the release 
agent machine. These are also packaged up in an overall ZIP file and are available to download. The 
overall ZIP file can be downloaded by clicking on the "Download all logs as ZIP" option.  
The ZIP file "ReleaseLogs_dd.zip" contains LOGs from the entire release pipeline including the master 
output for the AzSK_SVTs. The CSV file and the LOG file for AzSK SVTs are embedded in the 'inner' ZIP 
file that is named according to the parameterSet chosen to run the SVTs (in the pic below the ZIP file 
is named by the target resource group that we used 'mptestrg').
![03_Output_Folder](../Images/03_Output_Folder.png) 
Opening/extracting the "AzSK_Logs" ZIP file will reveal a folder structure and files placement identical to 
what we have seen in the case of ad hoc SVT runs:
![03_Output_logs](../Images/03_Output_logs.PNG)
[Back to top...](Readme.md#contents)
### Advanced CICD scanning capabilities
DevOps kit CICD extension enables you to leverage all the advance capabilities of toolkit while running in adhoc mode.
You could scan for specific controlIds in your build pipeline, or you could just scan for specific resources,
or you could also run a specific version of kit etc.
These advance features are available to customers through VSTS variables. Table below provide the different variables 
that are supported by the VSTS task:
|Variable Name| Usage| Examples|
|-------------|------|---------|
|LAWSId| Log Analytics workspace to continuously monitor progressive release/deployment health| e.g. c18xxxxx-xxxx-abcd-efgh-12345613489c Refer to step-4 in the above section|
|LAWSSharedKey| Log Analytics workspace shared key for extension to push the scan results from CICD| Refer step-4 from the above section for detail steps|
|AzSKServerURL| Org policy url for hosting the central policy configuration| Refer step-5 from the above section for detail steps |
|EnableServerAuth| Specifies whether Org policy URL (AzSKServerURL) is protected by AAD authentication.| e.g. true - protected by AAD authentication, false - not protected by AAD authentication|
|AzSKVersion| You could specify which version of toolkit you want to use in your CICD scan. And version specified should be >= N-2 where N is latest prod version. If variable is not provided, it uses the latest version available| e.g. 2.8.1|
|AzSKModuleName| This variable enable users to participate in the Preview testing. If you want to participate in preview, Provide the module name as "AzSKPreview". If not used, it would by default uses AzSK as module name| e.g. AzSKPreview|
|ExtendedCommand| Enables you to provide other switches supported by the Get-AzSKAzureServicesSecurityStatus command to perform focused scanning in the CICD pipeline | e.g. -ControlIds "Azure_Storage_DP_Encrypt_In_Transit,Azure_Storage_DP_Encrypt_At_Rest_Blob" or -UseBaselineControls. More switches that can be used with ExtendedCommand can be found [here](../02-Secure-Development/Readme.md#security-verification-tests-svt). |
|ExtendedCommandGSS| This variable is applicable when "Also scan subscription controls" option is enabled. It will enable you to provide additional parameters supported by the Get-AzSKSubscriptionSecurityStatus command to perform focused scanning in the CICD pipeline. ( Default implementation of GSS command in the task uses -ExcludeTags "OwnerAccess, GraphRead")| e.g. -FilterTags "AuthZ, BCDR" or -ControlIds "Azure_Subscription_Config_Azure_Security_Center". More switches that can be used with ExtendedCommandGSS can be found [here](../01-Subscription-Security/Readme.md#target-specific-controls-during-a-subscription-health-scan). |
|TreatAsPassed| This variable is to provide users with more control over behavior of the SVT extension in case of various control statuses other than ‘Passed’ or ‘Failed’. For e.g., using this, one may choose to have the extension treat statuses such as 'Verify','Manual','Exception' or 'Remediate' as 'Passed'.|e.g. The value of the variable TreatAsPassed can be passed as Verify,Manual to skip Verify and Manual controls|
|ScanOwnerAccessControlsGRS|This variable is to provide users with more control over scanning controls that need owner priviledges. With latest CICD task version 4.0.4, such controls are excluded from service controls scanby default.This behaviour can be overwritten by setting ScanOwnerAccessControlsGRS value to True. However, it is recommended not to give owner permissions to SPN over a subscription .| e.g. true
|UsageTelemetryLevel|This variable is to provide users with more control over sending anonymous telemetry for CICD scan at AzSK side. With latest CICD task version, if this variable is set to None , anonymous telemetry would not be captured at AzSK side.| e.g. Anonymous ,None 
[Back to top...](Readme.md#contents)
### FAQs
#### I have enabled AzSK_SVTs task in my release pipeline. I am getting an error ‘The specified module 'AzSK' was not loaded because no valid module file was found in any module directory’. How do I resolve this issue?
- Go to ‘AzSK_SVTs’ task in your release definition.
- Make sure that the check box  ‘Do not auto-update AzSK’ is unchecked. This will ensure to run the AzSK scan using the latest module from PS Gallery.
This error typically occurs when AzSK scan identifies non-compatible Az and AzSK modules present on the machine and tries to install the latest ones. 
#### I have enabled AzSK_SVTs task in my release pipeline. It is taking too much time every time I queue a release, how can I reduce that time?
- Go to ‘AzSK_SVTs’ task in your release definition.
- Mark the check box ‘Do not auto-update AzSK’ as checked. 
- This will help you save some time by not re-installing the AzSK from scratch in every run. This will skip the module check from PS Gallery and continue to use the installed modules for scan.
> **Note:** For Non-Hosted agent, it is always recommended to check if latest AzSK module is present on your machine before marking 'Do not auto-update AzSK' CheckBox as checked, since scan should always use latest AzSK module.  
> **Note:** You will need to keep the above checkbox unchecked if you are running the AzSK_SVTs task on any release agent for the first time OR you are running the task on Hosted VS2017 agent OR if non-hosted agent is already running on latest version.
#### I have enabled AzSK_SVTs task in my release pipeline. I am getting an error 'Cannot bind argument to parameter 'String' because it is null.'
This error is occurring because some of the configurations are missing/incorrect. Please ensure you have selected the correct subscription/service principal in the drop-down list.
If your subscription is not listed or if you want to use an existing service principal, you can setup an Azure service connection using the 'Add' or 'Manage' button.  Managed Service Identity service connection scope is limited to access granted to the Azure virtual machine running the agent. Ensure that the VM has access to specified resources.
#### I have enabled AzSK_SVTs task in my release pipeline. I am getting an error 'Could not perform AzSK SVTs scan. Please check if task configurations are correct.'
This release fails with the below error message because one or more variables of the release pipeline is missing/incorrect. Make sure the value of AzSKServerURL and EnableServerAuth in the ‘Variables’ section of the pipeline is correctly set. 
- Run the command Get-AzSKInfo -InfoType HostInfo. 
- The value of OnlinePolicyStoreURL and EnableAADAuthForOnlinePolicyStore should be used for the variable AzSKServerURL and EnableServerAuth in the variables section of the release pipeline. 
#### Why AzSK_SVTs task in my release pipeline has suddenly started failing 'Verify'/'Manual'/'Remediate'/'Exception' controls?
 All the control statuses other than 'Passed' would be treated as 'Failed' in the AzSK_SVT Task(going forward from AzSK_SVTs version 3.0.3). To treat control statuses other than 'Failed' as 'Passed' you can use 'TreatAsPassed' variable. Refer this [link](Readme.md#advanced-cicd-scanning-capabilities)
#### I want to run AzSK_SVT on non-hosted agent. What are the pre-requisites for running AzSK_SVTs task on non-hosted agent?
If you are using non-hosted agents you need to have azureps installed on it for AzSK_SVTs to run.
Make sure you have latest version of AzSK installed on the machine,since scan should always use latest AzSK module.
#### Why attestation is not getting respected in AzSK_SVT task in CICD pipeline?
To read attestation data the context from which AzSK SVT command is run must have atleast 'Contributor' access on the AzSKRG resource group. So if you want your task to respect the attestation data you must give the CICD SPN contributor access on AzSKRG.
[Back to top...](Readme.md#contents)
# Security Verification Tests (SVTs) in Jenkins pipeline (Preview)
> Note : AzSDK plugin requires PowerShell to be present on Jenkins Server. Therefore, the plugin is currently supported for Windows machines only.	
### Enable AzSDK extension for your Jenkins
Currently AzSDK CICD extension/plugin has not been published on Jenkins repository, However you can use Jenkins Web UI to upload this plugin([AzSDK_CICD_Jenkins_Plugin.hpi](Assets/AzSDK_CICD_Jenkins_Plugin.hpi) file) to Jenkins or place it in '$JENKINS_HOME/plugins' location.
**Step to upload plugin using Jenkins Web UI**
 Go to Home Page --> Manage Jenkins --> Manage plugins -->  Select Advanced --> Upload plugin file "[AzSDK_CICD_Jenkins_Plugin.hpi](Assets/AzSDK_CICD_Jenkins_Plugin.hpi)"
![03_Upload_plugin](../Images/03_Upload_Plugin.PNG)  
![03_Install_plugin](../Images/03_Install_Plugin.PNG)
 Plugin is successfully imported. Now let's use plugin to scan Azure Resources.  
[Back to top...](Readme.md#contents)
### Walkthrough
This part assumes that you are familiar with Jenkins pipeline at a basic level. To explore more on Jenkins, refer: [article](https://jenkins.io/doc/).
### Adding SVTs in the Jenkins pipeline
- #### Step-1: Configure Service Principal (SPN) credentials
	To run the SVT, AzSK need SPN/application which has reader on resource group.
	To set up an identity for the app(i.e. SPN) and assign reader role on resource group, refer: [article](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal).  
	You can configure details of SPN using below steps under Jenkins Global Credentials 
    1. Go to Home Page -->  Credentials --> System --> Global Credentials  --> Click on "Add Credentials" --> Select credential type "Microsoft Azure Service Principal"
    2. Fill out the details Subscription Id, Client ID, Client	Secret, OAuth 2.0 Token Endpoint and ID.
    3. Click on "Verify Service Principal" to validate SPN details are correct 
    4. Click Ok.
- #### Step-2: Create a Jenkins Job or open an existing one.
	Refer to this [article](https://www.tutorialspoint.com/jenkins/jenkins_setup_build_jobs.htm) to create sample build job
- #### Step-3: Add the AzSK-SVT build step to the pipeline.
	 Click on  "Add build step" and select "AzSK Security Verification Tests".
	![03_Add_Build_Steps](../Images/03_Add_Build_Steps.PNG)  
- #### Step-4: Specify the input parameters for the SVT step.
	Step displays some configuration inputs that are required for the task to run. Specify SPN credentials id as configured in Step-1. Remaining inputs are none other than the familiar options we have been specifying while running the AzSK SVTs manually. When the pipeline executes, SVTs will scan the specified set of resources.  
	![03_Input_Parameter](../Images/03_Input_Parameter.PNG)	
- #### Step-5: (Optional) Setup connectivity from CICD to Log Analytics.
	 You can also configure build to send runtime security evaluation results to Log Analytics workspace. For that configure the credentials using below steps:
 	- For adding Log Analytics workspace credentials  
		Go to Home Page -->  Credentials --> System --> Global credentials  --> Click on "Add Credentials" --> Select credential type "OMS Details"  
		Provide the details and click Ok
  	![03_Create_OMS](../Images/03_Create_OMS.PNG)  
	- Provide OMS Credentials Id in build step  
  	![03_Provide_OMS_Cred](../Images/03_Provide_OMS_Cred.PNG)	
- #### Step-6: Save the Job 
	![03_Save_Job](../Images/03_Save_Job.PNG)
[Back to top...](Readme.md#contents)
### Verifying that the SVTs have been added and configured correctly
- #### Step-1: Trigger the build.
	![03_Trigger_Build_1](../Images/03_Trigger_Build_1.PNG)  
 - #### Step-2: Verify that the build has started.
	![03_Trigger_Build_2](../Images/03_Trigger_Build_2.PNG)	  
- #### Step-3: View the 'Console Output'.
	![03_Trigger_Build_3](../Images/03_Trigger_Build_3.PNG)	  
- #### Step-4: See the summary "CSV" and detailed "LOG" output files for the AzSK SVTs.
	This is no different than the "ad hoc SVT run" scenarios. SVT outputs the location 
	of the "CSV" file and the "LOG" file at the end of the run.
	![03_Output_logs](../Images/03_Output_logs.PNG) 
[Back to top...](Readme.md#contents)
> 	Note :
> 	- Currently task is configured to not stop if SVT fails.
### Remediating failures and next steps
Once you have the CSV file and the LOG file for the SVTs execution, the process of understanding and remediating failures is no different than what is used when SVTs are run manually. Basically, you will 
 need to look at the failed SVTs in the CSV file and the corresponding details about 'what exactly caused 
each individual failure?' in the LOG file. Thereafter the issue can be remediated (additional guidance 
available from AzSK is at the link in the CSV file for each row).  
If you chose to route events to Log Analytics, you can also use the AzSK Monitoring Solution to view things 
like "build/release security health", long term trends, configure and receive alerts for various 
conditions (e.g., back to back SVT failures) etc.
[Back to top...](Readme.md#contents)
# AzSK ARM Template Checker
### Overview
The ARM Template security check script runs a scan on your given ARM Template to examine various conditions and configurations that need to be present in your ARM Template for secured resource deployment.
[Back to top…](Readme.md#contents)