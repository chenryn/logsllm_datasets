#### Which Log Analytics workspace should I use for my team when setting up CA?
Check with your service offering leader/org's cloud lead.
You would typically use one of the following options:
- Utilize a workspace is shared across a related set of services from your SO
- Create a new Log Analytics workspace and use that exclusively for your service ('free' tier is OK for just AzSK use cases)
- Utilize an IT-wide shared workspace  
#### Why does CA setup ask for resource groups?
CA supports scanning a subscription and a set of cloud resources that make up an application. These cloud resources are assumed to be hosted within one or more resource groups. A typical CA installation takes both the subscription info and resource groups info.
#### How can I find out if CA was previously setup in my subscription?
You can check using the "Get-AzSKContinuousAssurance" cmdlet. If CA is correctly setup, it will show a list of artifacts that are deployed during CA setup (e.g., Automation account, Connections, Schedules, Log Analytics workspace info, etc.). If CA has not been setup, you will see a message indicating so.
#### How can I tell that my CA setup has worked correctly?
There are 2 important things you should do to verify this:
Run the Get-AzSKContinuousAssurance and confirm that the output tells you as in the previous question.
Verify that the runbooks have actually started scanning your subscription and resource groups. You can check for this in Log Analytics.
#### Is providing resource groups mandatory?
We would like teams to, at a minimum, provide the list of resource groups that cover the most critical components of their application. It is unlikely that you will just have a subscription but no important resources inside it. Still, if you absolutely can't provide a resource group, then specify the "*"* as the resource group when setting up CA. 
If you do provide **"*"** as an option, CA will automatically grow/shrink the resource group list as you add/delete resource groups in your subscription.
#### What if I need to change the resource groups after a few weeks?
That is easy! Just run the Update-AzSKContinuousAssurance cmdlet with the new list of resource groups you would like monitored.
#### Do I need to also setup AzSK Monitoring solution?
This part is not mandatory for CA itself to work.
However, setting up the AzSK Monitoring solution is recommended as it will help you get a richer view of continuous assurance for your subscription and resources as scanned by CA. Secondly, it will give you several out-of-box artefacts to assist with security monitoring for your service. For instance, you will start getting email alerts if any of the high or critical severity controls from AzSK fail in your service.  
#### How to renew the certificate used for Continuous Assurance? 
#### Option 1: Renew certificate using powershell command
The SPN used for daily scanning by AzSK CA uses a cert credential which has a default expiry of 6 months. When the cert comes close to expiry both the Azure portal and the Get-AzSKContinuousAssurance command warn about a need to renew the credential. Here's how to renew the cert:
The SPN belongs to an AAD application that is created on behalf of the person who setup CA for the first time. You need to ensure that either that person performs the renewal or you can request that person to give you 'Owner' permission to that application. If the owner is unavailable (or has left the org) then you can create altogether new application in AAD (owned by you), SPN and a certificate credential and new SPN will be used for scanning your subscription moving forward.
Run the following command to renew CA certificate.
```PowerShell
Update-AzSKContinuousAssurance -SubscriptionId  -RenewCertificate
```
Run the following command to create new application in AAD (owned by you).
```PowerShell
Update-AzSKContinuousAssurance -SubscriptionId  -NewRuntimeAccount
```
Verify that it worked by running Get-AzSKContinuousAssurance again to confirm that the warning is gone.
```PowerShell
Get-AzSKContinuousAssurance -SubscriptionId 
```
Note:
If you don't know who ran CA setup earlier, you can find the owner of the AAD SPN by going to "Azure Active Directory" in the left pane in the portal and clicking "Enterprise Applications" and searching for the specific SPN (as shown below). Once you find the SPN, click on it and click "Owners". You can now contact one of the listed owners to either perform the above steps or add you as the owner so you can.
#### Option 2: Renew certificate from Portal
**Prerequisites:**
You need to be owner on the Subscription and SPN
**Steps to renew certificate from portal:**
1) Go to AzSKRG Resoure Group (or the one which has your AzSK CA automation account).
![01_RenewCertfromPortal](../Images/01_RenewCertfromPortal.png)
2) Go to "Automation Account -> Run as accounts -> Azure Run as account".Click on "Renew certificate".
![04_RenewCertfromPortal](../Images/04_RenewCertfromPortal.png)
3) After clicking "Renew certificate" click on option "Yes" and then it will initiate the certificate renewal as displayed in below screenshots. 
![05_RenewCertfromPortal](../Images/05_RenewCertfromPortal.png)
![06_RenewCertfromPortal](../Images/06_RenewCertfromPortal.png)
4) On successful renewal of certificate you will be able to see that the expiration date gets extended. 
![07_RenewCertfromPortal](../Images/07_RenewCertfromPortal.png)
#### What are some example controls that are not scanned by CA?
Here are a few examples of controls that CA cannot fully scan or can only 'partially' infer compliance for: 
* Azure_Subscription_AuthZ_Dont_Use_NonAD_Identities - requires Graph API access to determine if an AAD object is an 'external' identity 
* Azure_Subscription_AuthZ_Remove_Management_Certs - querying for management certs requires Co-Admin permission 
* Azure_AppService_AuthN_Use_AAD_for_Client_AuthN - often this is implemented in code so an app owner has to attest this control. Also, any 'security-related' config info is not accessible to the 'Reader' RBAC role. 
* Azure_CloudService_SI_Enable_AntiMalware - needs co-admin access.  
* Azure_CloudService_AuthN_Use_AAD_for_Client_AuthN - no API available to check this (has to be manually attested). 
* Azure_Storage_AuthN_Dont_Allow_Anonymous - needs 'data plane' access to storage account (CA SPN being a 'Reader' cannot do 'ListKeys' to access actual data). 
As always, the most foolproof way to check all control failures is to ensure you are doing the following:
Step-1: Update to the latest version of AzSK (it will tell you each time a command starts if your version is not the latest)
Step-2: Run a subscription controls scan (as Co-Admin) with "-UseBaselineControls" flag
Step-3: Run a complete scan of resources (as Co-Admin if you have classic resources or as Owner if you don't)
Step-4: Lastly, if you fix or attest any controls which CA cannot scan, you may need to rerun (b) or (c) above at least once so that the final status of those non-CA controls gets sent to the Azure Monitor.
#### Should I manually update modules in the AzSK CA automation account?
No! Manually updating Azure modules like that will break AzSK CA.
AzSK is reliant on a specific version of Az PowerShell modules. It is extensively tested against that version (and that version only). The Continuous Assurance setup process ensures that the correct version of Az modules is installed and imported into the CA automation account. If you attempt to update Azure modules (see pic below), it may bring in incompatible versions of Az modules and cause CA scanning to break. 
Note that once in a few months, the AzSK team reviews new releases of Az modules and updates the dependencies after extensive testing. At that point, the CA automation account will be automatically updated to import the newer modules. (No action is needed from your side.)
If Azure modules happens to be updated other than AzSK dependancy version(One option is using "Update Azure Module" in Portal), you can recover module dependency by deleting AzSK module from automation account and triggering Runbook job. Runbook will install AzSK with all dependencies. 
**Note:** If you are using Org policy feature, make sure you have latest RunbookCoreSetup file present in policy store. Org Policy update [page](https://aka.ms/devopskit/orgpolicy/updates) gives instruction to update coresetup file against latest AzSK versions.
#### Difference between scanned controls from CA v. ad hoc scans
Some controls require elevated access and are not scanned by CA because the CA runtime account is only configured with 'Reader' privilege on the subscription. 
The elevated access required may itself be different based on the control... e.g., some classic/v1 controls (such as presence of management certs) can be checked only if the runtime account has 'Co-Admin' privilege. Other controls (such as RBAC access to non-AAD identities) can be checked if you have read access to the AAD Graph. Yet others may need 'data plane' access (e.g., is a storage blob set to be publicly accessible?). 
Such controls will be counted as 'failing' by default until you run the scans manually (which is when the actual result will start reflecting for them). 
Also, when running scans manually, make sure you are on the latest version of the kit. That may also cause a discrepancy between a CA scan and a local scan. (CA always runs using the latest version of the kit.)
#### How much does it cost to setup Continuous Assurance along with the Monitoring solution?
Using the following ballpark calculations (and service costs as of Q1-FY18), we estimate that a Continuous Assurance
setup along with a Log Analytics workspace for monitoring will cost a little about $80/year for a typical
subscription with about 30-40 resources of various types. 
The average cost of AzSK CA and AzSK Monitoring solution per Azure resources comes to about $2.7 per year. (So, assuming
that a typical app has about 30 resources, we get about $81/year for an application.) 
The main/dominant component of the cost is automation runtime (storage/Azure Monitor costs are negligible in comparison). 
###### Assumptions:
- Typical application = 1 subscription + 3 resource groups (RGs) = ~30 resources (10 resources per RG)
- About 3 min per resource scan (higher side) => max ~100 min runbook time each day
- Central telemetry DB cost is not included (as in our model that’s not borne by individual app teams)
###### (a) Automation Runtime cost: ($80/year)
- Rate = $0.002/min of automation job
- For a 100 min runbook == $ 0.2 / day  
			=> $80 / year
###### (b) Blob Storage cost:  ($0.14/year)
- AzSK CA Storage accumulation = 150KB / resource * 30 =  4.5MB per day
- Average data for the month = 70MB (let’s take 100MB for simplicity) 
- Retention Cost: 
    - Rate = $.03/50TB/month for GRS-cool SKU 
		=> Average for the year ~ 0.6GB => cost =  $0.03*0.6*12/50000 ~ $4x10^-6/year 
- Access Cost (Listing): 
	- Rate = $0.2/10000 transactions
	- Our usage = ~ 1000 per year => $0.02 / year
- Access Cost (replication+retrieval): 
    - Rate = $0.1/GB
	- Our usage = ~ 1.2GB per year = $0.12 / year
- Total Blob Storage Cost (retention + listing + access)
	- 0.00 + 0.12 + 0.02 = $0.14/year
###### (c) Log Analytics storage cost: ($0.34/year)
- Assumes that the team is using Log Analytics for monitoring in general, otherwise, just for AzSK, free tier is sufficient.
- Data Upload
    - Rate = $2.3 / GB / month
	- Our usage = 10KB / resource scan => 300KB added per day = ~10MB data written for the month  = (2.3*10*12/1000) = $0.27/year
- Retention 
	- Rate - $0.10 / GB / month
	- Our usage = 60MB avg/month (at mid-year)  = $0.10 * 0.06 *12 = $0.07/year
- Total Log Analytics Cost (Upload + Retention)  
     - 0.27+0.07 = $0.34/year
[Back to top…](Readme.md#contents)
## Continuous Assurance (CA) - Trigger scan on resource deployment (Preview)
When you want to trigger scan on resource deployment in a subscription, need to use the flag -ScanOnDeployment. Using this flag will make sure to add an alert which will trigger the newly added runbook and scan the resource group in which the resource(s) have been deployed.ScanOnDeployment currently is not supported for Multi CA and Central Scan mode CA.
ScanOnDeployment works for resource deployment operation only, doesn't work on resource deletion.
#### 1. Install CA with flag -ScanOnDeployment
This can be achieved by adding extra param to the existing CA command as shown in the command below:
```PowerShell
$SubscriptionId = ''
$ResourceGroupNames = '*' #This should always be '*'
$LAWSId = ''
$LAWSSharedKey = '' 
Install-AzSKContinuousAssurance -SubscriptionId $SubscriptionId  
        -ResourceGroupNames $ResourceGroupNames -LAWSId $LAWSId -LAWSSharedKey $LAWSSharedKey -ScanOnDeployment
```
#### 2. Update CA with flag -ScanOnDeployment
In case you want to add/edit subscriptions covered via scan on deployment mode you can use Update-AzSKContinuousAssurance as shown below.
```PowerShell
$SubscriptionId = '' 
Update-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -ScanOnDeployment
```
#### 3. Remove flag -ScanOnDeployment
In case you want to unregister sub from scan on deployment mode need to run command as below:
```PowerShell
$SubscriptionId = '' 
Update-AzSKContinuousAssurance -SubscriptionId $SubscriptionId -Remove ScanOnDeployment
```
#### Troubleshooting
Please reach out to us at [PI:EMAIL]() if you face any issues with this feature. 
[Back to top…](Readme.md#contents)