	Get-AzSKSubscriptionSecurityStatus -SubscriptionId '' -ControlIds 'Azure_Subscription_AuthZ_Limit_Admin_Count_Ext'
```
##### B. Extending a GRS SVT
We will add a mock control that 'storage accounts must be created in 'eastus2' region.
1) Get preview policy downloaded to local folder:
    ```Powershell
    gop -SubscriptionId  -OrgName  -DepartmentName  -PolicyFolderPath  -DownloadPolicy
    ```
2) Copy Storage.ps1 from module folder ->        \Storage.ext.ps1
    a)  Clean up all but constructor, change to StorageExt, base-class to Storage, remove any class members.
    b) Add method that will implement the new control
    (see example file attached)
3) Copy Storage.json from module folder -> \Storage.ext.json
    a) Remove all, except one existing control (to edit into new control JSON)
    b) Edit the one control to reflect desired control-id, description, etc.
    Few important things:
    i) ControlId and Id should not conflict with existing ones
    ii) MethodName should correctly reflect the new method you wrote in Storage.ext.ps1 above
    iii) Do not change 'Storage' to 'StorageExt' inside the JSON (at the root node) 
4) Update org policy... (Important: you don't need to edit anything else or manually tweak policy in the blob)!
    ```Powershell    
    uop -SubscriptionId  -OrgName  -DepartmentName  -PolicyFolderPath  
    ```
Important: Also note that the "ext" in the file-names above is in all lower-case!
===============================================================
Verifying that the added control works:
1) Put your local AzSK into the target policy mode... (run "iwr" that is echoed by Step-4 above).
2) Run grs for a storage accounts and verify that the control is getting scanned:
        grs -s  -rgns  -rtn Storage
3) Run specific control-id, and across a couple of storage accounts in diff regions (the AzSKRG one will pass 'eastus2' check):
```Powershell
    grs -s  -ResourceGroupNames 'AzSKRG, , ' -ResourceTypeName Storage -ControlIds 'Azure_Storage_Create_In_Approved_Regions'
```
### Steps to override the logic of existing SVT:
1. Add new Feature.ext.ps1/SubscriptionCore.ext.ps1 file with the new function that needs to be executed as per the above documentation.
2. Customize Feature.json file as per https://github.com/azsk/DevOpsKit-docs/blob/master/07-Customizing-AzSK-for-your-Org/Readme.md#d-customizing-specific-controls-for-a-service by overriding "MethodName" property value with the new function name that needs to be executed.
3. That's it!! You can now scan the older control with overridden functionality. 
### Steps to add extended control in baseline control list:
1. Add new control to Feature.ext.json/SubscriptionCore.ext.json file as per the above documentation.
2. Add the new ControlId in baseline control list as per https://github.com/azsk/DevOpsKit-docs/blob/master/07-Customizing-AzSK-for-your-Org/Readme.md#c-creating-a-custom-control-baseline-for-your-org
3. That's it!! The newly added control will be scanned while passing "-UseBaselineControls" switch to GSS/GRS cmdlets.
### Steps to debug the extended control while development:
Extended Feature.ext.ps1 files are downloaded at C:\Users\\AppData\Local\Microsoft\AzSK\Extensions folder in the execution machine. While debugging, breakpoints need be inserted in those files. 
### Steps to add a new SVT to the AzSK module:
The following instructions will help you develop SVT for a new Azure service from scratch. That is, using these steps you can add an SVT for an Azure service that is not currently supported in DevOps Kit.
For illustration purpose, we will be developing SVT for Application Insights (as Application Insights is a resource type not currently supported in the DevOps kit.)
>**Note:** Currently, adding a completely new SVT to AzSK requires collaboration with the DevOps Kit team. This is because we need to make some changes in the core module to support the new SVT. Please email PI:EMAIL to initiate a discussion. Typically, we will be able to turn such requests around within our monthly sprint. 
> However, while that process is under way, you can still make progress on this task and, in fact, have a completely functioning new SVT created and tested within your org. Only thing is that you may need to do some renaming/minor file updates after the base support is included by the DevOps Kit team in the AzSK code (after which you can deploy for all users in your org for SDL/CICD/usage).
>In the steps below, those marked '###' are the steps that you have to do when writing your own new SVT for the first time. However, after you communicate the requirement to the AzSK team, we will include changes corresponding to those steps in the official module for future sprints. Subsequently, you will only need to maintain the code corresponding to the remaining steps.
The steps below follow roundabout the same model as in section [Extending AzSK Module](Readme.md#block-diagram-to-represent-the-extension-model). All controls you implement for the new SVT will be treated as ‘extended’ controls of a blank core SVT.
1. [###] Create files AppInsights.json and AppInsights.ps1 to represent base classes/control placeholders in the core module.
    Basically these files will serve the purpose of the (within-module) base class for AppInsights SVT and the controls you will write will go into the SVT extension.
    a.	Save AppInsights.json (content below) to \AzSK\\Framework\Configurations\SVT\Services.
    AppInsights.json
    ```PowerShell
    {
    "FeatureName": "AppInsights",
    "Reference": "aka.ms/azsktcp/appinsights",
    "IsMaintenanceMode": false,
    "Controls": []
    }
    ```
    b.	Save AppInsights.ps1 (content below) to \AzSK\\Framework\Core\SVT\Services.
    AppInsights.ps1
    ``` PowerShell
    Set-StrictMode -Version Latest
    class AppInsights: AzSVTBase
    {
        hidden [PSObject] $ResourceObject;
        AppInsights([string] $subscriptionId, [SVTResource] $svtResource):
            Base($subscriptionId, $svtResource)
        {
            $this.GetResourceObject();
        }
        hidden [PSObject] GetResourceObject()
        {
            if (-not $this.ResourceObject)
            {
                # Get resource details from AzureRm
                $this.ResourceObject = Get-AzureRmApplicationInsights -Name $this.ResourceContext.ResourceName -ResourceGroupName $this.ResourceContext.ResourceGroupName -Full 
                if(-not $this.ResourceObject)
                {
                    throw ([SuppressedException]::new(("Resource '$($this.ResourceContext.ResourceName)' not found under Resource Group '$($this.ResourceContext.ResourceGroupName)'"), [SuppressedExceptionType]::InvalidOperation))
                }
            }
            return $this.ResourceObject;
        }
    }
    ```
    Note that the content/structure of these files is similar to the other SVT base class files (e.g., Batch.json/Batch.ps1). Only that these are hollow classes (i.e., they do not have any controls implemented.)
2. Create AppInsights.ext.json and AppInsights.ext.ps1 (using the content below) wherever you store AzSK extension code in your source tree.
    Also copy these files to the (local) org policy folder (e.g., %userprofile%\Desktop\ContosoPolicies).
    Note that below we have implemented a single dummy control for App Insights called ‘Azure_AppInsights_No_Limited_Basic_Plan’ (which merely checks and fails if the pricing plan is ‘Limited Basic’). 
    AppInsights.ext.json
    ```PowerShell
    {
        "FeatureName": "AppInsights",
        "Reference": "aka.ms/azsktcp/appinsights", 
        "IsMaintenanceMode": false,
        "Controls": [
            {
                "ControlID": "Azure_AppInsights_No_Limited_Basic_Plan", 
                "Description": "Do not use ‘Limited Basic' tier plan for enterprise apps.", 
                "Id": "AppInsights1001", 
                "ControlSeverity": "Medium", 
                "Automated": "Yes",  
                "MethodName": "CheckAIPricingPlan", 
                "Recommendation": "Use an enterprise grade pricing plan other than ‘Limited Basic’.",
                "Tags": [
                    "SDL",
                    "Best Practice",
                    "Automated",
                    "AppInsights"
                ],
                "Enabled": true,
                "Rationale": "Logical intention for the extended control"
            }
        ]
    }
    ```
    AppInsights.ext.ps1
    ``` PowerShell
    Set-StrictMode -Version Latest
    # Class name must have Ext suffix. Class must be inherited from Feature class
    class AppInsightsExt: AppInsights
    {       
        AppInsightsExt([string] $subscriptionId, [SVTResource] $svtResource):
            Base($subscriptionId, $svtResource)
        { 
            $this.GetResourceObject();
        }
        hidden [ControlResult] CheckAIPricingPlan([ControlResult] $controlResult)
        {
            # Your function logic goes here.
            Write-Host("Checking AI pricing plan...")
            $ai = $this.ResourceObject
            if ($ai.PricingPlan -eq 'Limited Basic')
            {
                $controlResult.VerificationResult = [VerificationResult]::Failed
                $controlResult.AddMessage("AI: Use an enterprise grade pricing plan other than ‘Limited Basic’");
            }
            else {
                $controlResult.VerificationResult = [VerificationResult]::Passed
                $controlResult.AddMessage("AI: Non-basic plan is used per expectation!");
            }
            return $controlResult;
        }
    } 
    ```
3.	Now push the extension files to the org policy server using the command below:
    ``` PowerShell
    Update-AzSKOrganizationPolicy -SubscriptionId  `
    -OrgName "Contoso" `
    -DepartmentName "IT" `
    -PolicyFolderPath "%userprofile%\Desktop\ContosoPolicies"
    ```
4.	[###] Edit AllResourceTypes.json (\AzSK\\Framework\Configurations\SVT\) in the local module by adding an entry for the Application Insights resource type at the end (note the comma).
    Basically, this is where AzSK looks in the core module code to determine if a resource type is supported or not.
    ``` PowerShell
                                     ,
      "Microsoft.Insights/Components"
    ]
    ```
    >**Note:** To determine the exact name for a resource type you are trying to implement an SVT for, you can use the following commands (shown here for Application Insights):
    ```PowerShell
    # List all RPs/registration state:
    Get-AzureRmResourceProvider -ListAvailable | Select-Object ProviderNamespace, RegistrationState
    # microsoft.insights
    (Get-AzureRmResourceProvider -ProviderNamespace microsoft.insights).ResourceTypes.ResourceTypeName
    ```
5.	[###] Edit SVTMapping.ps1 (\AzSK\\Framework\Helpers) to add a resource type mapping entry for Application Insights.
    This mapping is how AzSK determines which PowerShell class implements the controls for the resource type.
    ```PowerShell
        [ResourceTypeMapping]@{
            ResourceType = "Microsoft.Insights/Components";
            ClassName = "AppInsights";
            JsonFileName = "AppInsights.json";
            ResourceTypeName = "AppInsights";
        },
    ```
6.	(In a fresh PS session) Run the following scan command to evaluate the control:
    ```PowerShell
      Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceTypeName AppInsights
      #or
      Get-AzSKAzureServicesSecurityStatus -SubscriptionId  -ResourceGroupNames  -ResourceNames 
    ```
### FAQs:
#### I have added ext control in Storage/AppService/VirtualMachine feature as per documentation. My control is still not getting executed. The control is not even coming as Manual in the csv.
Controls in the services like Storage/AppService/VirtualMachine must have some required "Tags" in the feature.ext.json. While initialization of the feature, calculation of applicable control should be done based on those Tags. If the tags are not present in the control, it will be filtered out and will not be executed. Below are some examples of the Tags which are required for the specific features.  
      **Storage**: Either "StandardSku" or "PremiumSku"/ or both should be added based on application of the ext control  
      **AppService**:  Either "AppService" or "FunctionApp" / or both should be added based on application of the ext control  
      **VirtualMachine**: Either "Windows" or "Linux" / or both should be added based on application of the ext control  
      **SQLDatabase**: "SqlDatabase" should be added if control is applicable for SQLDatabase.   
      For more details about Tag please refer: [Tag details](https://github.com/azsk/DevOpsKit-docs/blob/master/01-Subscription-Security/Readme.md#target-specific-controls-during-a-subscription-health-scan) 
### References:
- [SubscriptionCore.ext.json](SubscriptionCore.ext.json)
- [SubscriptionCore.ext.ps1](SubscriptionCore.ext.ps1)
- [Feature.ext.json](Feature.ext.json)
- [Feature.ext.ps1](Feature.ext.ps1)
- [ListenerName.ext.ps1](ListenerName.ext.ps1)