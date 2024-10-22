                              -DurationInDays  `
                              -RoleName  `
                              -PrincipalNames   `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Grant PIM access with 'Contributor' role to a user for 30 days on a Management Group.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                               -ManagementGroupId  `
                               -DurationInDays 30 `
                               -RoleName "Contributor" `
                               -PrincipalName "PI:EMAIL" `
                               -DoNotOpenOutputFolder
      ```
  2.  Activating your roles (-ActivateMyRole) 
      Use this command to activate your PIM access.
      > NOTE:  
      > a. Activation duration should range between 1 to 8 hours.  
      > b. Make sure that the PIM role you are activating is eligible. If your PIM role has expired, contact subscription administrator to renew/re-assign your PIM role.  
      ```PowerShell
      Set-AzSKPIMConfiguration -ActivateMyRole `
                              -ManagementGroupId  `
                              -RoleName  `
                              -DurationInHours  `
                              -Justification  `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Activate your PIM access on a Management Group.
      ```PowerShell
      Set-AzSKPIMConfiguration -ActivateMyRole `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
                              -DurationInHours 8 `
                              -Justification "Add a valid justification for enabling PIM role" `
                              -DoNotOpenOutputFolder
      ```
  3.  Deactivating your roles (-DeactivateMyRole) 
      Use this command to deactivate your PIM access.
      ```PowerShell
      Set-AzSKPIMConfiguration -DeactivateMyRole `
                              -ManagementGroupId  `
                              -RoleName  `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Deactivate your PIM access on a subscription.
      ```PowerShell
      Set-AzSKPIMConfiguration -DeactivateMyRole `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
                              -DoNotOpenOutputFolder
      ```
  4.  Assign PIM to permanent assignments at Management Group scope  (-AssignEligibleforPermanentAssignments) 
      Use this command to change permanent assignments to PIM for specified roles, at the specified scope. 
      > NOTE:  
      > This command will create PIM, but will not remove the permanent assignments. After converting permanent assignments to PIM, you can use *"Set-AzSKPIMConfiguration -RemovePermanentAssignments"* command with *"-RemoveAssignmentFor MatchingEligibleAssignments"* parameter to remove permanent assignment.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              –ManagementGroupId  `
                              -RoleNames  `
                              -DurationInDays  `
                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      Example 1:  Convert permanent assignments to PIM for 'Contributor' and 'Owner' roles at Management Group level. This command runs in an interactive manner so that you get an opportunity to verify the accounts being converted.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              –ManagementGroupId  `
                              -RoleNames "Contributor,Owner" `
                              -DurationInDays 30 `
                              -DoNotOpenOutputFolder
      ```
      Example 2:  Use '-Force' parameter to convert permanent assignments to PIM without giving runtime verification step.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              –ManagementGroupId  `
                              -RoleNames "Contributor,Owner" `
                              -DurationInDays 30 `
                              -DoNotOpenOutputFolder `
                              -Force
      ```
  5.  Removing permanent assignments altogether (-RemovePermanentAssignments) 
      Use this command to remove permanent assignments of specified roles, at the specified scope.
      There are two options with this command:
        a. *-RemoveAssignmentFor MatchingEligibleAssignments (Default)*: Remove only those permanent roles which have a corresponding eligible PIM role.
        b. *-RemoveAssignmentFor AllExceptMe*: Remove all permanent role except your access.
      > NOTE:
      > This command will *not* remove your permanent assignment if one exists.
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -ManagementGroupId  `
                              -RoleNames  `
                              [-RemoveAssignmentFor MatchingEligibleAssignments] `
                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -ManagementGroupId  `
                              -RoleNames  `
                              [-RemoveAssignmentFor AllExceptMe] `
                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      Example 1:  Remove 'Contributor' and 'Owner' roles that have permanent assignment at Management Group level. This command runs in an interactive manner so that you get an opportunity to verify the accounts being removed. All the specified role with permanent access will get removed except your access.
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -ManagementGroupId  `
                              -RoleNames "Contributor,Owner" `
                              -RemoveAssignmentFor AllExceptMe
                              -DoNotOpenOutputFolder
      ```
 6.  Extend PIM assignments for expiring assignments (-ExtendExpiringAssignments) 
	 Use this command to extend PIM eligible assignments that are about to expire in n days
    Example 1: Extend Owner PIM roles that are to be expired in 10 days. This command runs in an interactive manner in order to verify the assignments being extended.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			                  -DurationInDays 30 # The duration in days for expiration to be extended by
                              -DoNotOpenOutputFolder
      ```
      Example 2:  Use *'-Force'* parameter to run the command in non-interactive mode. This command will extend expiry of  'Owner' PIM roles that are about to be expired in 10 days by skipping the verification step.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			                  -DurationInDays 30 # The duration in days for expiration to be extended by
                              -Force
      ```
       Example 3:  Extend Owner PIM roles that are to be expired in 10 days specific to principal names.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			                  -PrincipalNames "PI:EMAIL,PI:EMAIL"  
      ```
7.  Configure role settings for role on an Azure resource (-ConfigureRoleSettings) 
	Use this command to configure a  PIM role settings like maximum role assignment duration on a resource, mfa requirement upon activation etc.
     The command currently supports configuring the following settings:
      a. *For Eligible Assignment Type*: Maximum assignment duration, maximum activation duration, requirement of justification upon activation, requirement of mfa upon activation and applying conditional access policies during activation.
      b. *For Active Assignment Type*: Maximum active assignment duration, requirement of justification on assignment, requirement of mfa on assignment.
      Example 1:  Configure 'Owner' PIM role on a Management Group for Eligible assignment type, to let maximum activation duration be 12 hours.
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -ManagementGroupId  `
                                -RoleNames "Owner" `
                                -MaximumActivationDuration 12`
                                -ExpireEligibleAssignmentsInDays 90 `
                                -RequireJustificationOnActivation $true
                                -RequireMFAOnActivation $true
                                -DoNotOpenOutputFolder`
      ```
	 Example 2:  Configure 'Owner' PIM role on a Management Group for Eligible assignment type, to apply conditional access policy while activation.
	    Note: Currently application of both MFA and conditional policy on the same role is not supported. Either of them should be applied to a given role. 
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -ManagementGroupId  `
                                -RoleNames "Owner" `
                                -ApplyConditionalAccessPolicyForRoleActivation $true
                                -DoNotOpenOutputFolder`
      ```
      Example 3:  Configure 'Reader' PIM role on a Management Group for Active assignment type, to let maximum assignment duration be 15 days. 
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -ManagementGroupId  `
                                -RoleNames "Reader" `
                                -ExpireActiveAssignmentsInDays 15 `
                                -RequireJustificationOnActiveAssignment $false `
                                -RequireMFAOnActiveAssignment $true `
                                -DoNotOpenOutputFolder
      ```
## AzSK: Credential hygiene helper cmdlets
To help avoid availability disruptions due to credential expiry, AzSK has introduced cmdlets that will help you track and get notified about important credentials across your subscription. AzSK now offers a register-and-track solution to help monitor the last update of your credentials. This will help you periodically track the health of your credentials which are nearing expiry/need rotation.
AzSK has also introduced the concept of ‘credential groups’ wherein a set of credentials belonging to a specific application/functionality can be tracked together for expiry notifications.
NOTE:
      Ensure you have atleast 'Contributor' access on the subscription before running the below helper commands. To configure expiry notifications for the tracked credentials, ensure you have 'Owner' access on the subscription.
### Use New-AzSKTrackedCredential to onboard a credential for tracking 
```PowerShell
   New-AzSKTrackedCredential -SubscriptionId '' `
                             -CredentialName '' `
                             -CredentialLocation '' `
                             -RotationIntervalInDays  `
                             -NextExpiryInDays  `
                             [-CredentialGroup ''] `
                             -Comment ''    
```
|Param Name|Purpose|Required?|Allowed Values|
|----|----|----|----|
|SubscriptionId|Subscription ID of the Azure subscription in which the to-be-tracked credential resides.|TRUE|None|
|CredentialName|Friendly name for the credential.|TRUE|None|
|CredentialLocation|Host location of the credential.|TRUE|Custom/AppService/KeyVault|
|RotationIntervalInDays|Time in days before which the credential needs an update.|TRUE|Integer|
|NextExpiryInDays|Time in days for the next expiry of the credential.|TRUE|Integer|
|CredentialGroup|(Optional) Name of the action group to be used for expiry notifications|FALSE|Valid action group name.|
|Comment|Comment to capture more information about the credential for the user for future tracking purposes.|TRUE|None|
> NOTE 1:
      > For credential location type 'AppService', you will have to provide app service name, resource group, app config type (app setting/connection string) & app config name. Make sure you have the required access on the resource.
> NOTE 2:
      > For credential location type 'KeyVault', you will have to provide key vault name, credential type (key/secret) & credential name. Make sure you have the required access on the resource.
> NOTE 3:
      > Use credential location type 'Custom', if the credential doesn't belong to an appservice or key vault.
### Use Get-AzSKTrackedCredential to list the onboarded credential(s) 
```PowerShell
   Get-AzSKTrackedCredential -SubscriptionId '' [-CredentialName ''] [-DetailedView]
```
> NOTE:
      > Not providing credential name will list all the AzSK-tracked credentials in the subscription. Use '-DetailedView' flag to list down detailed metadata about the credentials.
### Use Update-AzSKTrackedCredential to update the credential settings and reset the last updated timestamp
```PowerShell
    Update-AzSKTrackedCredential -SubscriptionId '' `
                                 -CredentialName '' `
                                 [-RotationIntervalInDays ] `
                                 [-CredentialGroup ''] `
                                 [-ResetLastUpdate] `
                                 -Comment ''                              
```
> NOTE:
      > Use '-ResetLastUpdate' to reset the last update time to current timestamp. 
### Use Remove-AzSKTrackedCredential to deboard a credential from AzSK tracking 
```PowerShell
   Remove-AzSKTrackedCredential -SubscriptionId '' [-CredentialName ''] [-Force]
```
### Use New-AzSKTrackedCredentialGroup to configure email alerts to notify users about AzSK-tracked credentials that are about to expire (' -AlertEmail ''
```