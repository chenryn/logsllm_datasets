## IMPORTANT: DevOps Kit (AzSK) is being sunset by end of FY21. More details [here](../ReleaseNotes/AzSKSunsetNotice.md)
----------------------------------------------
> The Secure DevOps Kit for Azure (AzSK) was created by the Core Services Engineering & Operations (CSEO) division at Microsoft, to help accelerate Microsoft IT's adoption of Azure. We have shared AzSK and its documentation with the community to provide guidance for rapidly scanning, deploying and operationalizing cloud resources, across the different stages of DevOps, while maintaining controls on security and governance.
AzSK is not an official Microsoft product – rather an attempt to share Microsoft CSEO's best practices with the community..
>NOTE:  
>The OMS* parameter/variable names will soon be deprecated. Please ensure that you have made the necessary changes to CA, CICD and AzSK Monitoring Solution as per below:  
>	1. Updated CA setups with new names ([details here](../04-Continous-Assurance#updating-an-existing-continuous-assurance-setup)). (Not required for CSEO subscriptions!)  
>	2. Switched to new names in CICD extension ([details here](../03-Security-In-CICD#advanced-cicd-scanning-capabilities)). (Required for all subscriptions)  
>	3. Start using the new parameters for [CA](../04-Continous-Assurance#setting-up-continuous-assurance---step-by-step) and [AzSK Monitoring Solution](../05-Alerting-and-Monitoring#1-c).
# Security Verification Tests (SVTs)
![Security_In_CICD](../Images/Security_In_CICD.png)
## Contents
- [Overview](Readme.md#overview) 
## [Security Verification Tests (SVTs) in VSTS pipeline](Readme.md#security-verification-tests-svts-in-VSTS-pipeline) 
- [Enable AzSK extension for your VSTS](Readme.md#enable-azsk-extension-for-your-vsts)
- [Walkthrough](Readme.md#walkthrough)
  - [Adding SVTs in the release pipeline](Readme.md#adding-svts-in-the-release-pipeline)
  - [Verifying that SVTs have been added and configured correctly](Readme.md#verifying-that-the-svts-have-been-added-and-configured-correctly)
- [Advanced CICD scanning capabilities](Readme.md#advanced-cicd-scanning-capabilities) 
- [FAQs](Readme.md#faqs)  
## [Security Verification Tests (SVTs) in Jenkins pipeline (Preview)](Readme.md#security-verification-tests-svts-in-jenkins-pipeline-preview-1)
- [Enable AzSDK extension for your Jenkins](Readme.md#enable-azsdk-extension-for-your-jenkins)
- [Walkthrough](Readme.md#walkthrough-1)
  - [Adding SVTs in the Jenkins pipeline](Readme.md#adding-svts-in-the-jenkins-pipeline)
  - [Verifying that SVTs have been added and configured correctly](Readme.md#verifying-that-the-svts-have-been-added-and-configured-correctly-1)
- [Remediating Failures and Next Steps](Readme.md#remediating-failures-and-next-steps)
## [AzSK ARM Template Checker](Readme.md#azsk-arm-template-checker)
- [Overview](Readme.md#overview-1) 
  - [Execute ARM Template Checker in Baseline mode](Readme.md#execute-arm-template-checker-in-baseline-mode) 
  - [Execute ARM Template Checker for specific controls](Readme.md#execute-arm-template-checker-for-specific-controls) 
  - [Execute ARM Template Checker excluding some controls from scan](Readme.md#execute-arm-template-excluding-some-controls-from-scan) 
  - [ARM Template Checker - Control coverage](Readme.md#arm-template-checker---control-coverage)
- [Enable AzSK extension for your VSTS](Readme.md#enable-azsk-extension-for-your-vsts-1)
- [Walkthrough](Readme.md#walkthrough-2)
  - [Adding ARM Template Checker in VSTS pipeline](Readme.md#adding-arm-template-checker-in-vsts-pipeline)
  - [Verifying that ARM Template Checker have been added and configured correctly](Readme.md#verifying-that-the-arm-template-checker-have-been-added-and-configured-correctly)
  - [Exclude files from scan](Readme.md#exclude-files-from-scan)
  - [Skip certain controls during scan](Readme.md#skip-certain-controls-during-scan)
  - [Use external parameter file](Readme.md#use-external-parameter-file)
  - [Advanced CICD scanning capabilities](Readme.md#advanced-cicd-scanning-capabilities-1) 
  - [Extending ARM Template Checker for your organization](Readme.md#extending-arm-template-checker-for-your-organization)
------------------------------------------------------------------
### Overview 
The AzSK contains Security Verification Tests (SVTs) for multiple PaaS and IaaS services of the Azure platform. 
As we have seen so far, these SVTs can be manually run against one or more target resources held in 
resource groups or tagged via a {tagName, tagValue} pair.
While it is invaluable to run these SVTs periodically from a PS console (to ensure that the subscription and 
the different resources that comprise your application are in a secure state), a key aspect of dev ops is 
to be able to automate such tests and integrate them as part of the dev ops workflows and release pipelines.
In other words, while checking that SVTs pass in an ad hoc manner is a good practice, it is important
to be able to also ensure that security control configuration remains intact in higher environments.
The CICD extensions feature of AzSK makes automated security configuration enforcement possible by 
making SVTs available as a Visual Studio Extension in the Marketplace so that engineering teams can run 
them within build/release pipeline. Once the build/release 
task is configured, SVTs run against a target deployment in an Azure subscription. Upon completion, 
SVTs will report the pass/fail status for controls along with aggregate control results. Hereafter, all the different 
'out-of-box' build/release workflow options from the CICD engine (e.g., VSTS)  can be used as 'next steps' based on 
the outcomes of SVTs. (For instance, one can decide whether to fail the release outright or to continue 
despite failures while sending an email to the build/release owners or to hold progress until someone 
manually approves, etc. Furthermore, if all SVTs pass in the pre-prod environment, then a release can 
be 'promoted' to prod.) 
Outcomes of the SVT execution can also be routed to a Log Analytics workspace configured to receive various events 
generated by the AzSK.
[Back to top...](Readme.md#contents)
# Security Verification Tests (SVTs) in VSTS pipeline
### Enable AzSK extension for your VSTS
This extension has been published to the VSTS gallery under "Build and Release" category. 
You can now install this extension from the Marketplace directly (https://marketplace.visualstudio.com/items?itemName=azsdktm.AzSDK-task).
> **Note:** You can also install this extension on your on-prem TFS instance. Please follow the instructions detailed at:
> https://docs.microsoft.com/en-us/vsts/marketplace/get-tfs-extensions
> **Note:** AzSK_SVT task is available in 'Release' pipeline tasks only. 
### Walkthrough
This part assumes that you are familiar with VS build tasks and pipelines at a basic level. To demonstrate 
the capability of the feature, we will use a basic MVC Web App that is checked into our trial repository. 
Our goal is to show how SVTs can be injected into the build/release workflow so that security testing for 
Azure subscription and resources is seamlessly integrated into CICD.  
[Back to top...](Readme.md#contents)
### Adding SVTs in the release pipeline
**Step-1:** Create a release definition or open an existing one.  
(Note: Here we will edit "AzSK_SVT" which is part of our test instance of VSTS.
We also have a default build definition upstream to this which is not shown here as that is a pretty 
standard web app build flow using an MSBuild task.)  
As shown below, currently the release definition is configured to simply deploy a web app upon building 
it to a particular app service at the given URL. This is likely to be the state of any working CICD
pipeline that builds and deploys a web app (or App Service) from VSTS to an Azure subscription. 
Let us take a look at the steps needed to add the AzSK-SVT task to the release definition.
![03_Create_Release_Definition](../Images/03_Create_Release_Definition.png)
**Step-2:** Add the AzSK-SVT release task to the pipeline.  
Click on "Add Tasks", and select "AzSK Security Verification Test".  
Click on "Add" and "Close". 
> **Note:** The VSTS dialog doesn't provide a good visual indication but the task does 
get added when you click "Add" once!
![03_Task_Catalog](../Images/03_Task_Catalog.PNG)
**Step-3:** Specify the input parameters for the SVT task.  
The "AzSK_SVTs" task starts showing in the "Run on Agent" list and displays some configuration inputs 
that are required for the task to run. These are none other than the familiar options we have been specifying 
while running the AzSK SVTs manually - you can choose to specify the target resource group(s) or 
a {tagname, tagvalue} pair based on how your application's resources are organized.  
When the pipeline executes, SVTs will scan the specified set of resources.
Apart from input parameter, you can also use checkboxes to enable/disable one or more below options
**Also scan subscription controls:** Switch to scan subscription security controls. This will require Azure Connection (SPN) to have atleast 'Reader' access at the subscription scope and ‘Contributor’ access on the ‘AzSKRG’ resource group.
**Send events to Log Analytics:** Switch to enable this task to publish SVT evaluation results to a Log Analytics workspace. Steps to configure workspace credentials are explained in Step-4
**Aggregate control status:** Switch to aggregate the SVTs control output. When this is turned off it would show all the failed individual controls in the task summary output.
**Do not auto-update AzSK:** Switch to toggle auto update of AzSK and required Az modules on the build server. Keep this un-checked for Hosted agent and Hosted VS2017 and while using SVT task fot the first time and if you want to update AZSK the version of AzSK. 
![03_IP_Parameter_for_Task](../Images/03_IP_Parameters_for_Task.png)
**Step-4:** (Optional) Setup connectivity from CICD to Log Analytics.  
> **Note:** You can skip this step in a first pass exploration of CICD integration of SVTs. 
This feature enables you to route the control scan results from SVTs in CICD pipelines to a Log Analytics workspace.
Configuring a Log Analytics workspace for the AzSK_SVTs task basically enables monitoring capability for 
build environments. Each time SVTs run in CICD, the AzSK events generated will be sent to 
the Azure Monitor repository and become available for subsequent queries, actions, alerts, etc. in the Log Analytics workspace.
(The AzSK includes a Monitoring solution that can be used to create a 'single dashboard' view of security 
for one or more applications across multiple dev ops stages.)  
We have added config info of a trial Log Analytics workspace used by the AzSK team below. You should choose your 
own target Log Analytics workspace and the corresponding resource group instead. (You can use Get-AzOperationalInsightsWorkspace 
cmdlet to quickly find out the resource group corresponding to your Log Analytics workspace. If you do not know your
app's Log Analytics workspace, you should check with your monitoring lead. Else you can create a trial workspace with
the 'Free' tier option.)   
The Log Analytics workspace information may be provided using one of the two options below:  
**Option-1:** Use a 'variable group'  
In this option, a single variable group may be defined at the VSTS level to represent the Log Analytics workspace 
that a collection of projects wants to share. This variable group may be 'linked' from the individual 
build/release definitions across these projects. The benefit is that, in the future, if a key value changes, 
you just have to make that change in one place and all definitions will immediately reflect the change.
The images below show this option. It involves 2 steps:  
1. 	 Create a variable group that holds the Log Analytics workspace info (if one doesn't exist for your org) 
2. 	 Link that variable group to your project's release definition
The variable group name can be a unique name you can choose (and specify in the release task definition). 
The specific variable names for workspace ID and shared key have to be exactly as shown below. The values 
of these should correspond the corresponding info for your Log Analytics workspace.  
Creating the variable group:
![03_Creating_Variable_Group](../Images/03_Creating_Variable_Group.PNG)
Linking to the release definition:
![03_Linking_To_Release](../Images/03_Linking_To_Release.PNG)
> **Note:** Variable groups can only be modified or added from the Library under VSTS instance.
**Option-2:** Directly use variables in individual build definitions.
![03_Directly_Use_Variables](../Images/03_Directly_Use_Variables.png)
Important: Ensure that the variable names used are exactly as above and the values correspond 
to *your* Log Analytics workspace. Moreover, when you specify the Log Analytics shared key, click on the 'lock' icon 
next to it so that it gets masked.
**Step-5:** Setup Online Policy URL (Mandatory for Org policy users e.g. CSE users)
This feature enables you to set up the CICD task to use your organization's AzSK policies. 
To use org-specific policies, you can get your org-specific settings by (a) running Get-AzSKInfo -InfoType HostInfo and looking at the value of 'OnlinePolicyStoreUrl' and 'EnableAADAuthForOnlinePolicyStore'(it specifies whether Org policy URL 'AzSKServerURL' is protected by AAD authentication).
Below, we have added configuration info of 'AzSKServerURL' and 'EnableServerAuth' used by the AzSK team. The URL at your org can be different assuming there is an org-policy setup unique to your org.  
The online policy URL can be configured for the CICD extension using one of the two options below:  
**Option-1**: Use a 'variable group'  
In this option, a single variable group may be defined at a VSTS level to represent the Policy URL that 
a collection of projects want to share. This variable group may be 'linked' from the individual 
build/release definitions across these projects. The benefit is that, in future, if a value changes, 
you just have to make that change in one place and all definitions will immediately reflect the change.  
The images below show this option. It involves 2 steps:  
1. Create a variable group that holds the URL info (if one doesn't exist for your org) 
2. Link that variable group to your project's release definition
The variable group name can be a unique name you can choose (and specify in the release task definition). 
The specific variable name for Policy URL  has to be exactly as shown below. 
Creating the variable group:  
![03_Online_Policy_Variable_Group](../Images/03_Online_Policy_Variable_Group.PNG)    
Linking to the release definition:    
![03_Online_Policy_Linking_Release](../Images/03_Online_Policy_Linking_Release.PNG) 
> Note: Variable groups can only be modified or added from the Library under VSO instance.
**Option-2**: Directly use variables in individual build definitions.  
![03_Online_Policy_Directly_Use_Variables](../Images/03_Online_Policy_Directly_Use_Variables.png)    
**Step-6**: Save the Release Definition.
![03_Save_Release_Definition](../Images/03_Save_Release_Definition.PNG)  
> **Note:** Please make sure that the service principal (SPN) that is used for the CICD pipeline task has the following permissions: (a) ‘Reader’ access on the resource groups that are to be scanned (or ‘Reader’ access at subscription level if all resource groups are being scanned) and (b) ‘Contributor’ access on the ‘AzSKRG’ resource group.