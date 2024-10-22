![03_FailedControl_Logs_ARMChecker](../Images/03_FailedControl_Logs_ARMChecker.JPG)
After editing CSV should look like this,
![03_Skip_Controls_File_ARMChecker](../Images/03_Skip_Controls_File_ARMChecker.JPG)
**Step-3:** Upload this edited CSV file to your repository and give path of this file in "Skip Controls From File" input as shown in below image:
![03_Skip_Controls_Param_ARMCheckerJPG](../Images/03_Skip_Controls_Param_ARMCheckerJPG.JPG)
[Back to top...](Readme.md#contents)
### Use external parameter file
To pass parameter values while scanning your ARM Template by ARM Checker, you can use external parameter file. The parameter file contains a value for the parameter. This value is automatically passed to the template during scanning. 
To pass external paramter file, give path of this file in "Parameter file path or folder path" input as shown in below image:
![03_Use_ParamFiles_ARMCheckerJPG](../Images/03_Use_ParamFiles_ARMCheckerJPG.jpg)
> **Note:** If you are passing folder path instead of single parameter file path, then parameter file must follow specific naming convention, [Template file name].parameters.json 
> for e.g. 
> ARM template file name - storage.json 
> Related parameter file name- storage.parameters.json
[Back to top...](Readme.md#contents)
### Advanced CICD scanning capabilities
DevOps kit CICD extension enables you to leverage all the advance capabilities of toolkit while running in adhoc mode.
You could scan for specific controlIds in your build pipeline, or you could exclude some controls from scan,
or you could also run a specific version of kit etc.
These advance features are available to customers through VSTS variables. Table below provide the different variables 
that are supported by the ARM Checker task:
|Variable Name| Usage| Examples|
|-------------|------|---------|
|AzSKServerURL| Org policy url for hosting the central policy configuration| Refer step-5 from the [above section](Readme.md#adding-svts-in-the-release-pipeline) for detail steps |
|EnableServerAuth| Specifies whether Org policy URL (AzSKServerURL) is protected by AAD authentication.| e.g. true - protected by AAD authentication, false - not protected by AAD authentication|
|AzSKVersion| You could specify which version of toolkit you want to use in your CICD scan. And version specified should be >= N-2 where N is latest prod version. If variable is not provided, it uses the latest version available| e.g. 3.12.0|
|AzSKModuleName| This variable enable users to participate in the Preview testing. If you want to participate in preview, Provide the module name as "AzSKPreview". If not used, it would by default uses AzSK as module name| e.g. AzSKPreview|
|ExtendedCommand| Enables you to provide other switches supported by the Get-AzSKARMTemplateSecurityStatus command to perform focused scanning in the CICD pipeline | e.g. -ControlIds "Azure_AppService_Deploy_Use_Latest_Version,Azure_AppService_AuthN_Use_Managed_Service_Identity" or -UseBaselineControls or -Severity "High, Medium"
|TreatAsPassed| This variable is to provide users with more control over behavior of the SVT extension in case of various control statuses other than ‘Passed’ or ‘Failed’. For e.g., using this, one may choose to have the extension treat statuses such as 'Verify','Manual' as 'Passed'.|e.g. The value of the variable TreatAsPassed can be passed as Verify,Manual to skip Verify and Manual controls|
|FailTaskIfNoControlsScanned| This variable is to control the behavior of the SVT extension in case of no controls scanned. For e.g., using this, one may choose to pass the task if it is configured to scan only 'High' severity control but there are no resources for which 'High' severity controls are applicable.| e.g. The value of the variable 'FailTaskIfNoControlsScanned' can be passed as 'true' to fail the task if no controls scanned or 'false' to pass the task if no controls scanned|
> **Note:** If you are using custom org policy features such as baseline controls scan etc., please make sure that CheckBox 'Use Org Baseline(s)' is checked and also provide an active azure service connection.
### Extending ARM Template Checker for your organization
If you are using [ org-policy ](../07-Customizing-AzSK-for-your-Org) feature, you can extend/customize the ARM Template Checker for your organization such as (a) by adding new controls to existing services or (b) by adding support to scan altogether new services. In this section, let us walk through the steps required to do so. However, before learning about extending ARM Template Checker, let us first understand how it works.
### How ARM Checker scans a control
To understand this, let's look at a single control for any service (e.g., Storage -> encrypt-in-transit control), 
```json
{ 
"featureName": "Storage", 
"supportedResourceTypes": ["Microsoft.Storage/storageAccounts"], 
"controls": [ 
	{ 
	"id": "AzureStorage160", 
	"controlId": "Azure_Storage_DP_Encrypt_In_Transit_Test", 
	"isEnabled": true, 
	"description": "HTTPS protocol must be used for accessing Storage Account resources", 
	"rationale": "Use of HTTPS ensures server/service authentication and protects data in transit from network layer man-in-the-middle, eavesdropping, session-hijacking attacks. When enabling HTTPS one must remember to simultaneously disable access over plain HTTP else data can still be subject to compromise over clear text connections.", 
	"recommendation": "Run command 'Set-AzStorageAccount -ResourceGroupName  -Name  -EnableHttpsTrafficOnly `$true'. Run 'Get-Help Set-AzStorageAccount -full' for more help.", 
	"severity": "Medium", 
	"jsonPath":  ["$.properties.supportsHttpsTrafficOnly"], 
	"matchType": "Boolean", 
	"data": {"value": true} 
	} 
	] 
} 
```
Once you pass ARM Template file to ARM Checker for scanning, while scanning ARM Template it follows steps mentioned below:
1. First of all, ARM Checker checks if the services used in the ARM template being scanned are supported by looking at the "SupportedResourceType" field in a file called “ARMControls.json” that is a global list of all services and corresponding controls covered by the ARM Checker. (It will look for this file in the folder “%userprofile%\Documents\WindowsPowerShell\Modules\AzSK\\Framework\Configurations\ARMChecker\ARMControls.json”. For instance, for the above example, it will look for: "Microsoft.Storage/storageAccounts".)
> **Note:** If "ARMControls.json" file is present on your org-server, server file will override the file present in your local machine.
2. For each service type that is covered, it will look under the “controls” list for that service type to identify the properties it needs to check for in the ARM template as mentioned by the “jsonPath” for each control (in our example,  Microsoft.Storage/storageAccounts -> properties -> supportsHttpsTrafficOnly) 
3. If the corresponding property is found on the object in the ARM template, it will compare with the expectation by using the “MatchType” and “Data” fields in the control. 
	* If the property is found and it's value matches with the value(s) specified in the "data" field (e.g., "True" above), ARM Checker will pass the control. 
	* If the property is not found, or its value doesn't match with expected value ARM Checker will fail the control. 
### How to add new controls to an existing service
1. Edit ARMControls.json 
2. Go to the service in which you want to add new controls 
3. Add new control object in the "controls" array.  
	``` json
	{ 
		"id": "TBD910", 
		"controlId": "TBD", 
		"isEnabled": true, 
		"description": "TBD", 
		"rationale": "TBD", 
		"recommendation": "TBD", 
		"severity": "High", 
		"jsonPath": [ "$.properties.properties1" ], 
		"matchType": "Boolean", 
		"data": { 
			"value": false 
			}  
	}
	```
> **Note:** For control id, please use format like featureName  + Integer (should be greater than 900) e.g. "id" : TrafficManager910 .
#### Important properties in control object:  
* "isEnabled" :  To enable/disable control during scan. If set to 'false' control will not be scanned. 
* "jsonPath":  Path of the property/object in ARM Template which will be evaluated by ARM Checker. 
* "matchType":  This field defines the type of property/object, expected at the path provided as "jsonPath"
* "data": This field determines control evaluation, different properties and values of those properties depends on the "matchType" defined above.
#### Supported Match type and their respective Data type:
    MatchType
    Data.Type
    Data.Value
    Data.IsCaseSensitive
    Description
    Example
    Boolean
    NA
    true/false
    NA
    Property should be present at "JsonPath", Property value should be a boolean and matches the value as mentioned in "data.value"
    If we want to ensure, in App Service "remote debugging" should be turned off, "jsonPath": [ "$.properties.siteConfig.remoteDebuggingEnabled"] "matchType": "Boolean", "data": {      "value": false }
    IntegerValue
    GreaterThan/LesserThan/Equals
    &lt; Any integer value &gt;
    NA
    Property should be present at "JsonPath", Property value should be a integer and Property value should be "GreaterThan/LesserThan/Equals" ( as mentioned in "data.type" ) to value (as mentioned in "data.value")
    If we want to ensure, App Service must be deployed on a minimum of two instances,      "jsonPath": [ "$.sku.capacity" ],    "matchType": "IntegerValue",    "data": {    "type": "GreaterThan",    "value": 1}
    ItemCount
    GreaterThan/LesserThan/Equals
    &lt; Any integer value &gt;
    NA
    Property should be present at "JsonPath", Property value should be an Array and Count of object in Array should be "GreaterThan/LesserThan/Equals" ( as mentioned in "data.type" ) to value (as mentioned in "data.value")
    If we want to ensure, CosmosDB uses replication,   "jsonPath": [ "$.properties.locations" ],    "matchType": "ItemCount",    "data": {    "type": "GreaterThan",    "value": 1}
    StringWhitespace
    NA
    false/true
    NA
    Property should be present at "JsonPath" and Property value should be "Empty string " or "Non empty String" (as mentioned in "data.value" )
    If we want to ensure, App Service must authenticate users using AAD backed credentials   "jsonPath": [ "$.properties.siteConfig.siteAuthSettings.clientId"],    "matchType": "StringWhitespace",      "data": {
            "value": false
          }
    StringSingleToken
    Allow/NotAllow
    &lt; Any string value &gt;
    false/true
    Property should be present at "JsonPath", Property value should be string and Property value should be "equal to (Allow)" or "not to equal(Not Allow)" (as mentioned in "data.type" )
    If we want to ensure, latest version of .NET framework version must be used for App Service        "jsonPath": [ "$.properties.siteConfig.netFrameworkVersion"],    "matchType": "StringSingleToken",      "data": {
            "type": "Allow",
            "value": "v4.7",
            "isCaseSensitive": false
          }
    VerifiableSingleToken
    NA
    NA
    NA
    Property should be present at "JsonPath" and Property value should be string
     If we want to ensure, only the required IP addresses are configured on Cosmos DB firewall  "jsonPath": [ "$.properties.ipRangeFilter" ],    "matchType": "VerifiableSingleToken",",  "data": {}
### How to add a new service
1. Edit ARMControls.json
2. Add new Service object in  "resourceControlSets" array like,
	```json
	{
	"featureName": "NewServiceName",
	"supportedResourceTypes": [ "Microsoft.XYZ/abc" ],
	"controls": [ ]			
	}
	```
	E.g.
	```json
	{
     "featureName": "ContainerRegistry",
     "supportedResourceTypes": [ "Microsoft.ContainerRegistry/registries" ],
     "controls": []
    }
	```
> **Note:** Resource type defined in "supportedResourceTypes" must be exactly same as resource type present in ARM template of the service.
If a service contains multiple resource type, you can add multiple types in "supportedResourceTypes" array.
 E.g. 
"supportedResourceTypes": [ "Microsoft.Web/sites", "Microsoft.Web/serverfarms", "Microsoft.Web/sites/config" ]
### Uploading extended ARM controls to policy store
Once you have tested your new ARM Checker controls on your machine.You need to upload these new controls to org policy store so that these new controls will be available for all users in your organization.
1. Go to org policy folder(in your local machine)
2. Create ARMControls.ext.json file with content given below.(if not present already)
   	```json
	{
	  "resourceControlSets": [ ]			
	}
	```
3. If you have added new service in ARM Checker, copy the whole service object (with all controls) from ARMControls.json and add it to "resourceControlSets" in ARMControls.ext.json file.
4. If you have extended controls in any existing service in ARM Checker, copy the service object (with only new controls) from ARMControls.json and add it to "resourceControlSets" in ARMControls.ext.json file. 
5. Run Update-AzSKOrganizationPolicy command to upload ARMControls.ext.json file to policy store.