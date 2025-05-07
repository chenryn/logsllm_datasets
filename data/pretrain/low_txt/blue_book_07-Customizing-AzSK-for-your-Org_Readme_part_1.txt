## Important Notice: DevOps Kit (AzSK) Sunset
The Secure DevOps Kit for Azure (AzSK) will be sunset by the end of FY21. For more details, please refer to the [AzSK Sunset Notice](../ReleaseNotes/AzSKSunsetNotice.md).

----------------------------------------------
### About AzSK
The Secure DevOps Kit for Azure (AzSK) was developed by the Core Services Engineering & Operations (CSEO) division at Microsoft to accelerate the adoption of Azure within Microsoft IT. We have shared AzSK and its documentation with the community to provide guidance on rapidly scanning, deploying, and operationalizing cloud resources across different stages of DevOps, while maintaining controls on security and governance. 

Please note that AzSK is not an official Microsoft product but rather a means to share best practices from Microsoft CSEO with the community.

# Customizing AzSK for Your Organization

### Overview
- [When and why should I set up org policy?](Readme.md#when-and-why-should-i-setup-org-policy)
- [How does AzSK use online policy?](Readme.md#how-does-azsk-use-online-policy)

### Setting Up Org Policy
- [What happens during org policy setup?](Readme.md#what-happens-during-org-policy-setup)
- [The org policy setup command: `Install-AzSKOrganizationPolicy`](Readme.md#the-org-policy-setup-command-install-azskorganizationpolicy)
- [First-time policy setup - an example](Readme.md#first-time-policy-setup---an-example)

### Consuming Custom Org Policy
- [Running scan in local machine with org policy](Readme.md#running-scan-in-local-machine-with-custom-org-policy)
- [Setting up Continuous Assurance](Readme.md#setting-up-continuous-assurance)
- [Using CICD Extension with org policy](Readme.md#using-cicd-extension-with-custom-org-policy)

### Modifying and Customizing Org Policy
- [Getting Started](Readme.md#getting-started)
- [Basic scenarios for org policy customization](Readme.md#basic-scenarios-for-org-policy-customization)
  - [Changing the default 'Running AzSK using…' message](Readme.md#a-changing-the-default-running-azsk-using-message)
  - [Changing control settings](Readme.md#b-changing-a-control-setting-for-specific-controls)
  - [Customizing specific controls for a service SVT](Readme.md#c-customizing-specific-controls-for-a-service)
  - [Setting up and updating baselines for your org](Readme.md#d-creating-a-custom-control-baseline-for-your-org)
  - [Customizing severity labels](Readme.md#e-customizing-severity-labels)

### Managing Policy/Advanced Policy Usage
- [Downloading and examining policy folder](Readme.md#downloading-and-examining-policy-folder)
- [Working with ‘local’ mode (policy dev-test-debug)](Readme.md#working-with-local-mode-policy-dev-test-debug)
- [How to upgrade org version to the latest AzSK version](Readme.md#how-to-upgrade-org-azsk-version-to-the-latest-azsk-version)
  - [Upgrade scenarios in different scan sources (SDL/CA/CICD)](Readme.md#upgrade-scenarios-in-different-scan-sources)
- [Maintaining policy in source control](Readme.md#maintaining-policy-in-source-control)
- [Policy deployment using CICD pipeline](Readme.md#policy-deployment-using-cicd-pipeline)

### Creating Compliance and Monitoring Solutions
- [Create cloud security compliance report for your org in PowerBI](Readme.md#create-cloud-security-compliance-report-for-your-org-using-powerbi)
- [AzSK org health monitoring dashboard](Readme.md#azsk-org-health-monitoring-dashboard)
- [Detailed resource inventory dashboard](Readme.md#detail-resource-inventory-dashboard)

### Compliance Notifications
- [Create compliance notification to subscription owners](Readme.md#compliance-notification-to-subscription-owners)

### Advanced Scenarios for Org Policy Customization/Extending AzSK
- [SVT customization](Readme.md#customizing-the-svts)
  - [Update/extend existing control by augmenting logic](./Extending%20AzSK%20Module/Readme.md#steps-to-override-the-logic-of-existing-svt)
  - [Add new control for existing GSS/GRS SVT](./Extending%20AzSK%20Module/Readme.md#steps-to-extend-the-control-svt)
  - [Add new SVT altogether (non-existing SVT)](./Extending%20AzSK%20Module/Readme.md#steps-to-add-a-new-svt-to-the-azsk-module)
- [Subscription security provisioning](Readme.md#customizing-subscription-security)
  - [ARM policy](Readme.md#arm-policy)
  - [Alert set](Readme.md#alert-set)
  - [Security center configurations](Readme.md#security-center-configurations)
  - [Mandatory/deprecated RBAC list](Readme.md#rbac-mandatorydeprecated-lists)
- [ARM checker policy customization](Readme.md#arm-checker-policy-customization)
- [Scenarios for modifying scan agent](Readme.md#scenarios-for-modifying-scanagent)
  - [Scanning only baseline controls using continuous assurance setup](Readme.md#scanning-only-baseline-controls-using-continuous-assurance-setup)
  - [Scanning admin and graph access controls using CA](Readme.md#scanning-owner-and-graph-access-controls-using-ca)
  - [Reporting critical alerts](#reporting-critical-alerts)
- [Change default resource group name (AzSKRG) and location (EastUS2) created for AzSK components](Readme.md#change-default-resource-group-name-(AzSKRG)-and-location-(EastUS2)-created-for-AzSK-components)

### Org Policy Usage Statistics and Monitoring Using Telemetry
- [Org policy usage statistics and monitoring using telemetry](Readme.md#org-policy-usage-statistics-and-monitoring-using-telemetry-1)

### Troubleshooting Common Issues
- [Testing and troubleshooting org policy](Readme.md#testing-and-troubleshooting-org-policy-1)

### Frequently Asked Questions
- [Frequently Asked Questions](Readme.md#frequently-asked-questions)

----------------------------------------------
## Overview

### When and Why Should I Set Up Org Policy?
When you run any scan command from AzSK, it relies on JSON-based policy files to determine various parameters that affect the behavior of the command. These policy files are downloaded on the fly from a policy server. When you run the public version of the toolkit, the policy files are accessed from a CDN endpoint managed by the AzSK team. Thus, whenever you run a scan from a vanilla installation, AzSK accesses the CDN endpoint to get the latest policy configuration and runs the scan using it.

The JSON inside the policy files dictates the behavior of the security scan, including:
- Which set of controls to evaluate?
- What control set to use as a baseline?
- What settings/values to use for individual controls?
- What messages to display for recommendations?

Note that the policy files needed for security scans are downloaded into each PowerShell session for all AzSK scenarios. This includes manually-run scans from your desktop, as well as scans included in CICD pipelines or Continuous Assurance setups. The AzSK policy files on the CDN are based on what we use internally in Core Services Engineering and Operations (CSEO) at Microsoft and are kept up to date with each release.

While the out-of-the-box files on the CDN may be suitable for limited use, in many contexts, you may want to customize the behavior of the security scans for your environment. You may want to:
- Enable/disable some controls.
- Change control settings to better match specific security policies within your organization.
- Change various messages.
- Add additional filter criteria for certain regulatory requirements that teams in your organization can leverage.

To achieve this, you need a way to create and manage a dedicated policy endpoint customized to the needs of your environment. The organization policy setup feature helps you do this in an automated fashion.

### How Does AzSK Use Online Policy?
Let's look at how policy files are leveraged in more detail. When you install AzSK, it downloads the latest AzSK module from the PowerShell Gallery. Along with this module, there is an offline set of policy files that go into a sub-folder under the `%userprofile%\documents\WindowsPowerShell\Modules\AzSK` folder. It also places (or updates) an `AzSKSettings.JSON` file in your `%LocalAppData%\Microsoft\AzSK` folder, which contains the policy endpoint (or policy server) URL used by all local commands.

Whenever any command is run, AzSK uses the policy server URL to access the policy endpoint. It first downloads a metadata file that contains information about the available files on the policy server. After that, whenever AzSK needs a specific policy file to perform a scan, it loads the local copy of the policy file into memory and overlays any settings if the corresponding file is found on the server-side.

The image below shows this flow with inline explanations:

## Setting Up Org Policy

### What Happens During Org Policy Setup?
At a high level, the org policy setup support for AzSK does the following:
- Sets up a storage account to hold various policy artifacts in the subscription you want to use for hosting your policy endpoint. (This should be a secure, limited-access subscription used only for managing your organization's AzSK policy.)
- Uploads the minimum set of policy files required to bootstrap your policy server.
- Sets up an Application Insights telemetry account in the subscription to facilitate visibility of control scan/telemetry events in your central subscription. (This is where control 'pass/fail' events will be sent when others in the organization start using the version of AzSK customized for your organization.)
- Creates a special folder (or uses one specified by you) for storing a local copy of all customizations made to the policy.
- Creates an organization-specific (customized) installer that others in your organization will use to install and configure AzSK according to your organization's policy.

### The Org Policy Setup Command (`Install-AzSKOrganizationPolicy`)
This command helps the central security team of an organization to customize the behavior of various functions and security controls checked by AzSK. As discussed in previous sections, AzSK runtime behavior is mainly controlled through JSON-based policy files with a predefined schema. The command helps in creating a policy store and other required components to host and maintain a custom set of policy files that override the default AzSK behavior.

| Parameter | Description | Required? | Default Value | Comments |
| --- | --- | --- | --- | --- |
| SubscriptionId | Subscription ID of the Azure subscription in which the organization policy store will be created. | Yes | None |  |
| OrgName | The name of your organization. The value will be used to generate names of Azure resources being created as part of policy setup. This should be alphanumeric. | Yes | None |  |
| DepartmentName | The name of a department in your organization. If provided, this value is concatenated to the org name parameter. This should be alphanumeric. | No | None |  |
| PolicyFolderPath | The local folder in which the policy files capturing org-specific changes will be stored for reference. This location can be used to manage policy files. | No | User Desktop |  |
| ResourceGroupLocation | The location in which the Azure resources for hosting the policy will be created. | No | EastUS2 | To obtain valid locations, use the `Get-AzLocation` cmdlet. |
| ResourceGroupName | Resource Group name where policy resources will be created. | No | AzSK--RG | Custom resource group name for storing policy resources. **Note:** `ResourceGroupName`, `StorageAccountName`, and `AppInsightName` must be passed together to create custom resources. The same parameters must be used to update org policy. |
| StorageAccountName | Name for policy storage account. | No | azsk--sa |  |
| AppInsightName | Name for application insight resource where telemetry data will be pushed. | No | AzSK--AppInsight |  |
| AppInsightLocation | The location in which the Application Insights resource will be created. | No | EastUS |  |

### First-Time Policy Setup - An Example
The following example sets up policies for the IT department of the Contoso organization. You must be an 'Owner' or 'Contributor' for the subscription in which you want to host your organization's policy artifacts. Ensure that the org name and dept name are purely alphanumeric and their combined length is less than 19 characters. The policy setup command is lightweight in terms of effort/time and costs incurred.

```PowerShell
Install-AzSKOrganizationPolicy -SubscriptionId <subscription-id> `
           -OrgName "Contoso" `
           -DepartmentName "IT" `
           -PolicyFolderPath "D:\ContosoPolicies"
```

**Note:** For Azure environments other than Azure Cloud (like Azure Gov, China, etc.), provide the `ResourceGroupLocation` as the default value won't work in those environments.

The execution of the command will create the following resources in the subscription (if they don't already exist):
1. Resource Group (AzSK-Contoso-IT-RG) - AzSK--RG.
2. Storage Account (azskcontosoitsa) - azsk--sa.
3. Application Insight (AzSK-Contoso-IT-AppInsight) - AzSK--AppInsight.
4. Monitoring dashboard (DevOpsKitMonitoring (DevOps Kit Monitoring Dashboard [Contoso-IT])).

**Note:** You must not have any other resources in the org policy resource group except those created by the setup command.

It will also create a basic 'customized' policy involving the following files uploaded to the policy storage account:

| File | Container | Description |
| --- | --- | --- |
| AzSK-EasyInstaller.ps1 | installer | Org-specific installation script. This installer ensures that anyone who installs AzSK using your 'iwr' command not only gets the core AzSK module but also configures their local installation of AzSK to use org-specific policy settings (e.g., policy server URL, telemetry key, etc.). **IMPORTANT:** Ensure that anyone in your organization who needs to scan according to your policies uses the above 'iwr' command to install AzSK. They should not use `Install-Module AzSK` directly. Anyone using an incorrect setup will not get your custom policy when they run any AzSK cmdlet. |
| AzSK.Pre.json | policies | This file contains a setting that controls/defines the AzSK version that is 'in effect' at an organization. An organization can use this file to specify the specific version of AzSK that will be used in SDL/CICD/CA scenarios at the organization for people who have used the org-specific 'iwr' to install and configure AzSK. **Note:** During the first-time policy setup, this value is set with the AzSK version available on the client machine that was used for policy creation. Whenever a new AzSK version is released, the org policy owner should update the AzSK version in this file with the latest released version after performing any compatibility tests in a test setup. You can get notified of new releases by following the AzSK module in PowerShell Gallery or the release notes section [here](https://azsk.azurewebsites.net/ReleaseNotes/LatestReleaseNotes.html). |
| RunbookCoreSetup.ps1 | policies | Used in Continuous Assurance to set up the AzSK module. |
| RunbookScanAgent.ps1 | policies | Used in Continuous Assurance to run daily scans. |
| AzSk.json | policies | Includes org-specific messages, telemetry key, InstallationCommand, CASetupRunbookURL, etc. |
| ServerConfigMetadata.json | policies | Index file with a list of policy files. |

Output of the command looks like the following:

If you note section 3 of the command output, an 'iwr' command line is printed to the console. This command leverages the org-specific installation script from the storage account for installing AzSK. You can run this IWR followed by some scan commands (GSS/GRS) to see the org policy in effect in your development box.

```PowerShell
# IWR to install org-specific configurations
iwr 'https://azskcontosoitsa.blob.core.windows.net/installer/AzSK-EasyInstaller.ps1' -UseBasicParsing | iex
# Subscription Scan with org policy
Get-AzSKSubscriptionSecurityStatus -SubscriptionId <subscription-id>
```

### Next Steps
Once your org policy is set up, all scenarios/use cases of AzSK should work seamlessly with your org policy server as the policy endpoint for your organization (instead of the default CDN endpoint). You should be able to do one or more of the following using AzSK:
- People will be able to install AzSK using your special org-specific installer (the 'iwr' install command).
- Developers will be able to run manual scans for the security of their subscriptions and resources (GRS, GSS commands).
- Teams will be able to configure the AzSK SVT release task in their CICD pipelines.
- Subscription owners will be able to set up Continuous Assurance (CA) from their local machines (after they've installed AzSK using your org-specific 'iwr' installer locally).
- Monitoring teams will be able to set up the AzSK Log Analytics view and see scan results from CA (and also manual scans and CICD if configured).
- You will be able to do central governance for your organization by leveraging telemetry events that will collect in the master subscription from all the AzSK activity across your organization.

## Consuming Custom Org Policy

### Running Scan in Local Machine with Custom Org Policy
To run a scan with a custom org policy from any machine, get the IWR cmdlet from the org policy owner. This IWR is generated at the time of policy setup (IOP) or policy update (UOP) in the following format:

```PowerShell
# Sample IWR to install org-specific configurations
iwr 'https://azskcontosoitsa.blob.core.windows.net/installer/AzSK-EasyInstaller.ps1' -UseBasicParsing | iex
# Run subscription scan cmdlet and validate if it is running with org policy
Get-AzSKSubscriptionSecurityStatus -SubscriptionId <subscription-id>
```

This step is a prerequisite for the other two scan methods.

### Setting Up Continuous Assurance
Setting up Continuous Assurance (CA) with org policy is straightforward. Once you have followed the first step (running IWR in the local machine), you can set up CA with the help of the documentation [here](https://github.com/azsk/DevOpsKit-docs/blob/master/04-Continous-Assurance/Readme.md#setting-up-continuous-assurance---step-by-step). The CA setup command will refer to policy settings from your local machine and configure them in the automation runbook.

For existing CA, you just need to run `Update-AzSKContinuousAssurance` in your local environment.

You can validate if CA is running with custom org policy via the options below:
- **Option 1:**
  - Go to the central CA resource group → automation account → Jobs → Open one of the completed jobs → It prints initials of `PolicyStoreURL` (Policy Store URL is nothing but the org policy storage account blob URL).
  - ![AzSK org policy check using runbook](../Images/07_OrgPolicy_CA_PolicyCheck-0.PNG)

- **Option 2:**
  - Download the latest AzSK scan logs stored in the storage account (inside `AzSKRG`).
  - ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-1.PNG)
  - Open the `PowerShellOutput.log` file under the `etc` folder and validate the policy name.
  - ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-2.PNG)

- **Option 3:**
  - Go to the Log Analytics workspace configured during CA setup and execute the following query:
    ```AI Query
    AzSK_CL | where Source_s == "CA" | summarize arg_max(TimeGenerated, *) by SubscriptionId | project SubscriptionId, PolicyOrgName_s | render table
    ```
  - It will show the subscriptions running with org policy in a table as depicted below:
    - ![AzSK Scan Logs](../Images/07_OrgPolicy_CA_PolicyCheck-3.PNG)

### Using CICD Extension with Custom Org Policy
To set up CICD when using custom org policy, follow these steps: