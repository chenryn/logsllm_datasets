# Command to scan subscription level controls
Get-AzSKSubscriptionSecurityStatus -SubscriptionId '' -FilterTags "OwnerAccess,GraphRead" 
# Command to scan resource level controls
Get-AzSKAzureServicesSecurityStatus -SubscriptionId '' -FilterTags "OwnerAccess,GraphRead" 
# Command to scan both subscription and resource level controls
Get-AzSKControlsStatus -SubscriptionId '' -FilterTags "OwnerAccess,GraphRead" 
```
#### How can I find out what to do for controls that are marked as 'manual'?
Refer the recommendations provided in the output CSV file for the security controls defined by AzSK. You can also email to PI:EMAIL or reach out to your security point of contact for any queries.  
#### How can I implement fixes for the failed ones which have no auto-fix available?
Refer the recommendations provided in the output CSV file for the security controls defined by AzSK. You can also email to PI:EMAIL or reach out to your security point of contact for any queries.  
#### Troubleshooting
|Error	|Comments|
| ----- |--------|
|Subscription xxxx was not found in tenant. Please verify that the subscription exists in this tenant…."|	Provide the valid Subscription Id to the 'Subscription' parameter while running the cmdlets that accept subscription id as the parameter.|
|File xxxx cannot be loaded because the execution of scripts is disabled on this system… "|	By default, PowerShell restricts execution of all scripts. Execute below cmdlet to fix this issue: **Set-ExecutionPolicy -ExecutionPolicy Unrestricted** |  
[Back to top…](Readme.md#contents)
--------------------------------------
# Express Route-connected Virtual Networks (ER-vNet)
**Summary**  
The following cmdlet can be used to scan the secure configuration of an ExpressRoute-connected virtual network (referred to as ERVnet below):
```PowerShel
 Get-AzSKExpressRouteNetworkSecurityStatus -SubscriptionId 
```
This cmdlet assumes that the vNet connected to ExpressRoute circuit is in a ResourceGroup named 'ERNetwork' or 'ERNetwork-DMZ'. 
If you have the vNet in a different resource group then the `-ResourceGroup` parameter can be used.
Just like other SVTs, this will create a summary ".CSV" file of the control evaluation and a detailed
".LOG" file that includes more information about each control and the outcome.
The following core checks are currently performed by this utility:
- There should not be any Public IPs (i.e., NICs with PublicIP) on ER-vNet VMs.
- There should not be multiple NICs on ER-vNet VMs.
- The 'EnableIPForwarding' flag cannot set to true for NICs in the ER-vNet.
- There should not be any NSGs on the GatewaySubnet of the ER-vNet.
- There should not be a UDR on *any* subnet in an ER-vNet
- There should not be another virtual network gateway (GatewayType = Vpn) in an ER-vNet.
- There should not be any virtual network peerings on an ER-vNet.
- Only internal load balancers (ILBs) may be used inside an ER-vNet.
Additionally the following other 'protective' checks are also done: 
- Ensuring that the resource lock that is setup to keep these resources from being deleted is intact.
- Ensuring that the RBAC permissions for the account used to track compliance are intact.
- Setting up alerts to fire for any of the above actions in the subscription.
[Back to top…](Readme.md#contents)
# Security IntelliSense (Dev-SecIntel)
--------------------------------------------------------------
> Note: Security IntelliSense extension works on Visual Studio 2015 Update 3 or later,  Visual Studio 2017 and Visual Studio 2019.
### Basics:
### What is Security IntelliSense?
Security IntelliSense augments standard Visual Studio IntelliSense feature with secure coding knowledge. This makes it possible to get 'inline' assistance for fixing potential security issues while writing code. Code that is vulnerable or not policy compliant is flagged with red or green squiggles based on the level of severity.
In the current drop, we have support for the following features:
- About 80 rules that cover a variety of scenarios such as: 
   - various Azure PaaS API related secure coding rules
   - ADAL-based authentication best practices
   - Common Crypto errors
   - Classic App Sec and Web App Sec issues
- Rule are auto-updated without needing to reinstall the plug-in. The plug-in periodically checks if new rules have been published to a central rule store and updates its local rule set based on that. 
The screenshots below show the core functionality at work:
- Error and warning indications for incorrect and possibly vulnerable code:
	(E.g., use of custom token cache in ADAL scenario)  
![SecIntel_Ex_1](../Images/02_SecIntel_Ex_1.PNG)
- Suggestions for corrections/compliant coding practices:
	(E.g., Instead of Random, the RNGCryptoServiceProvider class should be used in a crypto context.)  
![02_SecIntel_Ex_2](../Images/02_SecIntel_Ex_2.PNG)  
[Back to top…](Readme.md#contents)  
### How do I enable Security IntelliSense on my dev box?
* For Visual Studio 2015/2017  
   - Open Visual Studio 
   - Go to **Tools** -> **Extensions and Updates** -> In the left sidebar select **Online** -> **Visual Studio Gallery** and search for **Security IntelliSense** in the right sidebar
* For Visual Studio 2019
   - Open Visual Studio. 
      (Note: If you are using a Preview release of VS2019 then you would need to start Visual Studio in admin mode.)
   - Go to **Extensions** -> **Manage Extensions** -> In the left sidebar select **Online** -> **Visual Studio Marketplace** and search for **Security IntelliSense** in the right sidebar
![02_SecIntel_VSGallery_Download](../Images/02_SecIntel_VSGallery_Download.PNG)
- Select Security IntelliSense item and click **Download** or **Install**
- After download completes, close the Visual Studio
- It will open **VSIX Installer**, click on **Modify**.
- After installation completes, **Start Visual Studio**
[Back to top…](Readme.md#contents)
### Is there a sample I can use to see how it works?
- We have a sample project on GitHub that you can use. Run the command below to clone the repo. 
If you don't have Git setup in your machine, please visit https://git-scm.com/downloads to download it.
``` 
    git clone https://github.com/azsk/azsk-secintel-samples.git
```
- After cloning the repo, navigate to **azsk-secintel-samples** -> **SecIntelSample** and 
open the **SecIntelSample.sln** in Visual Studio (after completing the Security IntelliSense 
extension installation per steps from above).
- Build the solution (this will fetch any requisite Nuget packages)
- Go to View->Solution Explorer and then open one of demo files (e.g., "CryptoSample.cs") in the VS editor. 
   - You should see SecIntel in action -- i.e., code that is in violation of the rules in use for 
   the SecIntel VSIX plugin will appear as red-squigglies (errors) and green-squigglies (warnings).  
   ![02_SecIntel_Suggestion](../Images/02_SecIntel_Suggestion.PNG)
- Note: In the currently implemented behavior of the extension, 'errors' don’t actually fail the build. 
We will change this behavior in an upcoming sprint. After that anything that is considered an 'error' will start failing 
the build. This will be a useful feature when integrating with CICD pipelines.
[Back to top…](Readme.md#contents)
### Rules:
### What 'secure coding' rules are currently covered?
The following are some of the rules we support in current build (some are 'warnings' others 'error') -
- Azure:
   - Use of relays without client authentication
   - Creation of shared access policy without enforcing HTTPS explicitly
   - Creation of shared access policy with an overly long expiry period
   -Creation of container with access set to 'Public'
   - Creation of a blob with access set to 'Public'
- ADAL/Graph usage:
   - Use of simple member access as opposed to transitive search
   - Explicit handling of access and refresh tokens as opposed to letting ADAL manage them transparently
   - Disabling 'Authority' validation when fetching a token via ADAL
   - Use of custom mechanisms to cache the tokens (should let ADAL handle them transparently)
- Crypto:
   - Use of Random instead of RNGCryptoServiceProvider class
   - Use of MD5 for hashing instead of SHA256CryptoServiceProvider
   - Use of SHA1 for hashing instead of SHA256CryptoServiceProvider
   - Use of RijndaelManaged instead of AesCryptoServiceProvider
   - Use of key sizes that are considered inadequate
   - Use of X509Certificate2 class (that might lead to a SHA1 based HMAC as opposed to a SHA256-based one).
For a complete list of Security IntelliSense rules please go [here](Security_IntelliSense_rules_list.md)
[Back to top…](Readme.md#contents)
### How are the rules updated? Do I need to refresh the plugin periodically?
- Rule are auto-updated without the need to reinstall the plugin. Currently we have 
defined 5 different rule templates upon which individual rules are based. We have the ability to 
deploy new rules that use the existing templates silently in the background. 
- Once in a while we might add entirely new 'rule templates'. When that happens, a new version of 
the extension will need to be downloaded. When that happens will include a notification of the same 
in our release announcements.
[Back to top…](Readme.md#contents)
### Can I add my own rules over and above the default set?
- This will be included in the next month. It is a natural extension of the current behavior. We 
will merely need to include support for a locally managed rules file which has rules that adhere to 
the supported rule templates.
[Back to top…](Readme.md#contents)
### Can I 'mask' a particular rule or rules?
- This is in our backlog. We will add it in a future sprint.
[Back to top…](Readme.md#contents)
### Can I change the 'recommended' code for a rule? (e.g., I want to recommend GCM instead of CBC mode)
- This is in our backlog. We will add it in a future sprint.
[Back to top…](Readme.md#contents)
### Actions:
### What should I do to remove the extension?
-  Go to "Tools" -> "Extensions and Updates" menu option in Visual Studio and search for "Security".
   - If you have the extension installed, you will see a screen such as below with options to 
   "Disable" or "Uninstall" the extension.
- Click "Uninstall" and restart Visual Studio.
![02_SecIntel_VSGallery](../Images/02_SecIntel_VSGallery_Uninstall.PNG)  
[Back to top…](Readme.md#contents)
### What default compiler actions are configured?
- Most of the rules configured are of severity "Warning"
[Back to top…](Readme.md#contents)
### Can I customize actions for my dev box / team? (E.g. change Error -> Warnings etc.)
- Currently we do not support it. We have it in our pipeline to support it.  
[Back to top…](Readme.md#contents)