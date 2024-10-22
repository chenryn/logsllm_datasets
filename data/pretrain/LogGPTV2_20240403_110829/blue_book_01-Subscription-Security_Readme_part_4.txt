                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      Example 1:  Convert permanent assignments to PIM for 'Contributor' and 'Owner' roles at subscription level . This command runs in an interactive manner so that you get an opportunity to verify the accounts being converted.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleNames "Contributor,Owner" `
                              -DurationInDays 30 `
                              -DoNotOpenOutputFolder
      ```
      Example 2:  Use *'-Force'* parameter to convert permanent assignments to PIM without giving runtime verification step.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleNames "Contributor,Owner" `
                              -ResourceGroupName "DemoRG" `
                              -ResourceName "AppServiceDemo"`
                              -DurationInDays 20 `
                              -DoNotOpenOutputFolder
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
                              -SubscriptionId  `
                              -RoleNames  `
                              [-RemoveAssignmentFor MatchingEligibleAssignments] `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -SubscriptionId  `
                              -RoleNames  `
                              [-RemoveAssignmentFor AllExceptMe] `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
                              [-Force]
      ```
      Example 1:  Remove 'Contributor' and 'Owner' roles that have permanent assignment at subscription level. This command runs in an interactive manner so that you get an opportunity to verify the accounts being removed. All the specified role with permanent access will get removed except your access.
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleNames "Contributor,Owner" `
                              -RemoveAssignmentFor AllExceptMe
                              -DoNotOpenOutputFolder
      ```
      Example 2:  Use *'-Force'* parameter to run the command in non-interactive mode. This will remove permanent assignment at resource level without giving runtime verification step. Use *-RoleNames* to filter the roles to be deleted. Here we have used *-RemoveAssignmentFor 'MatchingEligibleAssignments'*. Hence, this command deletes the specified role with permanent access only if there is a corresponding PIM role for the same.
      ```PowerShell
      Set-AzSKPIMConfiguration -RemovePermanentAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleNames "Owner" `
                              -RemoveAssignmentFor MatchingEligibleAssignments
                              -ResourceGroupName "DemoRG" `
                              -ResourceName "AppServiceDemo"`
                              -DoNotOpenOutputFolder
                              -Force
      ```
 6.  Extend PIM assignments for expiring assignments (-ExtendExpiringAssignments) 
	 Use this command to extend PIM eligible assignments that are about to expire in n days
    Example 1: Extend Owner PIM roles that are to be expired in 10 days. This command runs in an interactive manner in order to verify the assignments being extended.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			      -DurationInDays 30 # The duration in days for expiration to be extended by
                              -DoNotOpenOutputFolder
      ```
      Example 2:  Use *'-Force'* parameter to run the command in non-interactive mode. This command will extend expiry of  'Owner' PIM roles that are about to be expired in 10 days by skipping the verification step.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			      -DurationInDays 30 # The duration in days for expiration to be extended by
                              -Force
     Example 3:  Extend Owner PIM roles that are to be expired in 10 days specific to principal names.
      ```PowerShell
      Set-AzSKPIMConfiguration -ExtendExpiringAssignments `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleName "Owner" `
                              -ExpiringInDays 10
			                  -PrincipalNames "PI:EMAIL,PI:EMAIL"  
7. Configure role settings for role on an Azure resource (-ConfigureRoleSettings)  
	 Use this command to configure a  PIM role settings like maximum role assignment duration on a resource, mfa requirement upon activation etc.
     The command currently supports configuring the following settings:
      a. *For Eligible Assignment Type*: Maximum assignment duration, maximum activation duration, requirement of justification upon activation, requirement of mfa upon activation and applying conditional access policies during activation.
      b. *For Active Assignment Type*: Maximum active assignment duration, requirement of justification on assignment, requirement of mfa on assignment.
      Example 1:  Configure 'Owner' PIM role on a subscription for Eligible assignment type, to let maximum activation duration be 12 hours.
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                                -RoleNames "Owner" `
                                -MaximumActivationDuration 12`
                                -ExpireEligibleAssignmentsInDays 90 `
                                -RequireJustificationOnActivation $true
                                -RequireMFAOnActivation $true
                                -DoNotOpenOutputFolder`
      ```
	 Example 2:  Configure 'Owner' PIM role on a subscription for Eligible assignment type, to apply conditional access policy while activation.
	    Note: Currently application of both MFA and conditional policy on the same role is not supported. Either of them should be applied to a given role. 
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                                -RoleNames "Owner" `
                                -ApplyConditionalAccessPolicyForRoleActivation $true
                                -DoNotOpenOutputFolder`
      ```
	 Example 3:  Configure 'Reader' PIM role on a subscription for Active assignment type, to let maximum assignment duration be 15 days. 
      ```PowerShell
      Set-AzSKPIMConfiguration  -ConfigureRoleSettings `
                                -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                                -RoleNames "Reader" `
                                -ExpireActiveAssignmentsInDays 15 `
                                -RequireJustificationOnActiveAssignment $false `
                                -RequireMFAOnActiveAssignment $true `
                                -DoNotOpenOutputFolder
      ```
8.  Remove PIM assignments for a role on an Azure resource (-RemovePIMAssignment) 
     Use this command to remove PIM assignments of specified role, at the specified scope.
    Example 1:  Remove 'Contributor' role that have PIM assignment at subscription level. This command runs in an interactive manner so that you get an opportunity to verify the accounts being removed. All the specified principal names with PIM access on the role will get removed.
      ```PowerShell
      Set-AzSKPIMConfiguration  -RemovePIMAssignment `
                                -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                                -RoleName "Contributor" `
                                -PrincipalNames "PI:EMAIL,PI:EMAIL" 
      ```
      Example 2:  Use *'-Force'* parameter to run the command in non-interactive mode. This will remove PIM assignment at resource level without giving runtime verification step. 
      ```PowerShell
      Set-AzSKPIMConfiguration  -RemovePIMAssignment `
                                -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                                -RoleName "Contributor" `
                                -PrincipalNames "PI:EMAIL,PI:EMAIL" `
                                -ResourceGroupName "DemoRG" `
                                -ResourceName "AppServiceDemo" `
                                -Force
      ```
### Use Get-AzSKPIMConfiguration (alias 'getpim') for querying various PIM settings/status at Management Group level
  1.  List permanent assignments (-ListPermanentAssignments)   
      Use this command to list Azure role with permanent assignments at the specified scope. By default, it lists all role assignments in the selected Azure Management Group. Use respective parameters to list assignments for a specific role, or to list assignments on a specific roles.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments`
                              -ManagementGroupId  `
                              [-RoleNames ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  List all permanent assignments at Management Group level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments `
                               -ManagementGroupId 
      ```
      Example 2: List all permanent assignments at Management Group level with 'Contributor' and 'Owner' roles.
       ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments `
                               -ManagementGroupId  `
                               -RoleNames "Contributor,Owner" `
                               -DoNotOpenOutputFolder
      ```
  2.  List PIM assignments (-ListPIMAssignments) 
      Use this command to list Azure role with PIM assignments at the specified scope. By default, it lists all role assignments in the selected Azure Management Group. Use respective parameters to list assignments for a specific roles.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                              -ManagementGroupId  `
                              [-RoleNames ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  List PIM assignments at Management Group level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                               -ManagementGroupId 
      ```
      Example 2:  List 'Contributor' and 'Owner' PIM assignments at Management Group level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                               -ManagementGroupId  `
                               -RoleNames "Contributor,Owner" `
                               -DoNotOpenOutputFolder
      ```
  3.  List expiring assignments (-ListSoonToExpireAssignments) 
      Use this command to list Azure role with PIM assignments at the specified scope that are about to expire in given number of days. Use respective parameters to list expiring assignments for a specific role on a Management Group.
      ```PowerShell
	  Get-AzSKPIMConfiguration -ListSoonToExpireAssignment  `
                               -ManagementGroupId  `
                               -RoleNames  `
                               -ExpiringInDays  ` # The number of days you want to query expiring assignments for
                               [-DoNotOpenOutputFolder]
      ```
      Example 1:  List 'Owner' PIM assignments at Management Group level that will expire in 10 days.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListSoonToExpireAssignment `
                               -ManagementGroupId  `
                               -RoleNames 'Owner' `
			                   -ExpiringInDays 10`
                               -DoNotOpenOutputFolder
      ```
   4.  List existing role settings (-ListRoleSettings) 
      Use this command to list Azure role with PIM assignments at the specified scope to fetch existing settings of a role for both Eligible and Active role assignments.
      ```PowerShell
	  Get-AzSKPIMConfiguration -ListRoleSettings  `
                              -ManagementGroupId  `
                              -RoleName "Owner" `
      ```
      Example 1:  List role settings for 'Owner' PIM role at Management Group level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListRoleSettings `
                               -ManagementGroupId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleName "Owner" `
      ```
### Use Set-AzSKPIMConfiguration (alias 'setpim') for configuring/changing PIM settings at Management Group level:
  1.  Assigning users to roles (-AssignRole) 
     Use this command to assign PIM role to the specified principal, at the specified scope.
      > NOTE:
      > You must have owner access to run this command.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                              -ManagementGroupId  `