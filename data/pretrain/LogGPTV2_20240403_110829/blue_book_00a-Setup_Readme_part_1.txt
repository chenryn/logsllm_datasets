## Important Notice: DevOps Kit (AzSK) Sunset
The Secure DevOps Kit for Azure (AzSK) will be sunset by the end of FY21. For more details, please refer to the [AzSK Sunset Notice](../ReleaseNotes/AzSKSunsetNotice.md).

---

### Overview
The Secure DevOps Kit for Azure (AzSK) was developed by the Core Services Engineering & Operations (CSEO) division at Microsoft to accelerate Microsoft IT's adoption of Azure. AzSK and its documentation have been shared with the community to provide guidance on rapidly scanning, deploying, and operationalizing cloud resources across different stages of DevOps, while maintaining security and governance controls. Please note that AzSK is not an official Microsoft product but rather a way to share best practices from Microsoft CSEO.

### Installation Guide

#### Important Note for CSE Users
If you are from CSE, please follow the installation instructions at [this link](https://aka.ms/devopskit/onboarding) to ensure that CSE-specific policies are configured for your installation. Do not use the general installation instructions provided below.

#### Prerequisites
- PowerShell 5.0 or higher
- Windows OS

1. **Verify Prerequisites:**
   - Ensure you are using a Windows OS.
   - Check your PowerShell version by running the following command in the PowerShell ISE console:
     ```PowerShell
     $PSVersionTable
     ```
   - If the PSVersion is older than 5.0, update PowerShell from [here](https://www.microsoft.com/en-us/download/details.aspx?id=54616).
     ![PowerShell Version](../Images/00_PS_Version.PNG)

2. **Install the Secure DevOps Kit for Azure (AzSK) PS Module:**
   ```PowerShell
   Install-Module AzSK -Scope CurrentUser
   ```

   **Note:**
   - You may need to use the `-AllowClobber` and `-Force` options with the `Install-Module` command if you have a different version of Az modules installed on your machine.
   - AzSK depends on specific versions of different Az service modules and installs them during the installation process.
   - To see all dependencies, run the command:
     ```PowerShell
     Find-Module AzSK -IncludeDependencies
     ```
   - In version 3.6.x, if you encounter issues during a scan, you may need to register the "Microsoft.Security" and "Microsoft.PolicyInsights" providers on your subscriptions. Refer to [this link](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-supported-services#portal) for provider registration.

### Backward Compatibility
As Azure features evolve and add more security controls, the "Secure DevOps Kit for Azure" also evolves monthly to respect the latest security features. It is always recommended to use the latest DevOps kit module to scan your subscription with the latest rules.

- **Users can continue to use N-2 versions relative to the production version.** For example, if the current production version is 3.11.x, then teams can continue to use 3.9.x and 3.10.x. When version 3.12.x becomes available, 3.9.x will stop working.

#### Impact on Different Stages of DevOps Kit
- **Adhoc Scans:**
  - Users running scans with N-3 versions from their local machine will start receiving an error asking to upgrade.
    ![Install_OlderVersionWarning](../Images/00_Install_OlderVersionWarning.PNG)
  - **Note:** This restriction has been in place since AzSDK version 2.8.x and applies to all future releases.

- **Continuous Assurance (CA) Scans:**
  - No impact. CA automatically upgrades to the latest version before every scan.

- **AzSK CICD Extension:**
  - No impact to the default behavior. The extension always runs the scan with the latest version available in the PS Gallery.
  - If teams have overridden the default behavior by specifying a version number during the build, the N-2 restriction applies.

### Auto Update
It is always recommended to scan your subscription with the latest DevOps kit module to ensure the evaluation of the latest security controls.

- **Adhoc Scans:**
  - Users running older versions of AzSK scans from their local machine will receive a warning with instructions to upgrade.
    ![Install_Autoupdate](../Images/00_Install_Autoupdate.PNG)
  - For organizations with their own instance of AzSK, users can leverage the auto-update feature introduced in AzSDK version 2.8.x.
  - To enable or disable auto-update, run the following command:
    ```PowerShell
    Set-AzSKPolicySettings -AutoUpdate On|Off
    ```
  - After running the command, close and reopen a fresh session.
  - During the execution of any AzSK command, the auto-update workflow will start automatically if a new version is available.
    ![Install_Autoupdate_Workflow](../Images/00_Install_Autoupdate_Workflow.PNG)
    - **Step 1:** User consent is required before starting the auto-update workflow.
    - **Step 2:** Close all displayed PS sessions to avoid locking the module.
    - **Step 3:** Close the current session and give user consent to start the auto-update flow.

- **Continuous Assurance (CA) Scans:**
  - The AzSK module running CA scans auto-updates itself. Each scan checks for new versions and auto-upgrades the installed module.
  - To confirm, run the following command:
    ```PowerShell
    Get-AzSKContinuousAssurance -SubscriptionId ''
    ```

- **AzSK CICD Extension:**
  - The extension always runs the scan using the latest AzSK module from the gallery. This is the default behavior for both hosted and non-hosted agents.
  - For more details about CICD, refer to [this link](../03-Security-In-CICD/Readme.md).

### FAQs
#### Getting Exception: Package 'Az.Accounts' Failed to Be Installed
Some users have encountered issues during the installation of the latest AzSK module from PSGallery. This is due to AzSK's dependency on specific Az module versions. We are investigating the issue. As a workaround, you can install the module from the AzSK repository using the following method:

```PowerShell
$AzSKModuleRepoPath = "https://azsdkossep.azureedge.net/3.7.0/AzSK.zip"
# Copy module zip to temp location
$CopyFolderPath = $env:temp + "\AzSKTemp\"
if (-not (Test-Path -Path $CopyFolderPath)) {
  mkdir -Path $CopyFolderPath -Force | Out-Null
}
$ModuleFilePath = $CopyFolderPath + "AzSK.zip"           
Invoke-WebRequest -Uri $AzSKModuleRepoPath -OutFile $ModuleFilePath
# Extract zip file to module location
Expand-Archive -Path $ModuleFilePath -DestinationPath "$Env:USERPROFILE\documents\WindowsPowerShell\modules" -Force
```

This should resolve the issue and allow you to install the AzSK module successfully.