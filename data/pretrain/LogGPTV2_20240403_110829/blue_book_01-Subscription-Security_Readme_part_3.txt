Please refer [this](../07-Customizing-AzSK-for-your-Org#customizing-azsk-for-your-organization) for more details
Note:
As Azure Government and Azure China are limited to particular location, provide 'ResourceGroupLocation' parameter because the default value is EastUS2
```PowerShell
E.g., Install-AzSKOrganizationPolicy -SubscriptionId  `
           -OrgName  `
           -PolicyFolderPath  `
           -ResourceGroupLocation "USGov Virginia" `
	   -AppInsightLocation "USGov Virginia"                   (for Azure Government)
```
## AzSK: Privileged Identity Management (PIM) helper cmdlets
AzSK now supports the Privileged Identity Management (PIM) helper cmdlets. This command provides a quicker way to perform Privileged Identity Management (PIM) operations and enables you to manage access to important Azure subscriptions, resource groups and resources.
### Use Get-AzSKPIMConfiguration (alias 'getpim') for querying various PIM settings/status at Subscription scope
  1.  List your PIM-eligible roles (-ListMyEligibleRoles) 
      Use this command to list eligible PIM roles in the selected Azure subscription.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListMyEligibleRoles
      ```
  2.  List permanent assignments (-ListPermanentAssignments)   
      Use this command to list Azure role with permanent assignments at the specified scope. By default, it lists all role assignments in the selected Azure subscription. Use respective parameters to list assignments for a specific role, or to list assignments on a specific resource group or resource.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments`
                              -SubscriptionId  `
                              [-RoleNames ] `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1: List all permanent assignments at subscription level with 'Contributor' and 'Owner' roles.
       ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor,Owner" `
                               -DoNotOpenOutputFolder
      ```
      Example 2:  List all permanent assignments at 'DemoRG' resource group level with 'Contributor' role.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor" `
                               -ResourceGroupName "DemoRG" `
                               -DoNotOpenOutputFolder
      ```
      Example 3:  List all permanent assignments at resource level with 'Contributor' and 'Owner' role.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPermanentAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor,Owner" `
                               -ResourceGroupName "DemoRG" `
                               -ResourceName "AppServiceDemo" `
                               -DoNotOpenOutputFolder
      ```
  3.  List PIM assignments (-ListPIMAssignments) 
      Use this command to list Azure role with PIM assignments at the specified scope. By default, it lists all role assignments in the selected Azure subscription. Use respective parameters to list assignments for a specific role, or to list assignments on a specific resource group or resource.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                              -SubscriptionId  `
                              [-RoleNames ] `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  List 'Contributor' and 'Owner' PIM assignments at subscription level.
       ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor,Owner" `
                               -DoNotOpenOutputFolder
      ```
      Example 2:  List 'Contributor' PIM assignments at 'DemoRG' resource group level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor" `
                               -ResourceGroupName "DemoRG" `
                               -DoNotOpenOutputFolder
      ```
      Example 3:  List 'Contributor' and 'Owner' PIM assignments at resource level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListPIMAssignments `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames "Contributor,Owner" `
                               -ResourceGroupName "DemoRG" `
                               -ResourceName "AppServiceDemo" `
                               -DoNotOpenOutputFolder
      ```
3.  List expiring assignments (-ListSoonToExpireAssignments) 
      Use this command to list Azure role with PIM assignments at the specified scope that are about to expire in given number of days. Use respective parameters to list expiring assignments for a specific role on a subscription or a resource group or a resource.
      ```PowerShell
	  Get-AzSKPIMConfiguration -ListSoonToExpireAssignment  `
                              -SubscriptionId  `
                              -RoleNames  `
                              -ExpiringInDays ` # The number of days you want to query expiring assignments for
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  List 'Owner' PIM assignments at subscription level that will expire in 10 days.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListSoonToExpireAssignment `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleNames 'Owner' `
			       -ExpiringInDays 10`
                               -DoNotOpenOutputFolder
4.  List existing role settings (-ListRoleSettings) 
      Use this command to list Azure role with PIM assignments at the specified scope to fetch existing settings of a role for both Eligible and Active role assignments.
      ```PowerShell
	  Get-AzSKPIMConfiguration -ListRoleSettings  `
                              -SubscriptionId  `
                              -RoleName "Owner" `
                              [-ResourceGroupName]
                              [-ResourceName]
      ```
      Example 1:  List role settings for 'Owner' PIM role at subscription level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListRoleSettings `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleName "Owner" `
      ```
      Example 2:  List role settings for 'Contributor' PIM role at resource level.
      ```PowerShell
      Get-AzSKPIMConfiguration -ListRoleSettings `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -RoleName "Contributor" `
                               -ResourceGroupName "DemoRG" `
                               -ResourceName "AppServiceDemo" `
      ```
### Use Set-AzSKPIMConfiguration (alias 'setpim') for configuring/changing PIM settings at Subscription scope:
  1.  Assigning users to roles (-AssignRole) 
     Use this command to assign PIM role to the specified principal, at the specified scope.      
      > NOTE:
      > a. You must have owner access to run this command.
      > b. Assignment Type 'Eligible' or 'Active' can be provided in -AssignmentType parameter. If parameter is not explicitly used then role is assigned for 'Eligible' assignment type.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                              -SubscriptionId  `
                              -DurationInDays  `
                              -RoleName  `
                              -PrincipalName   `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-AssignmentType ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Grant PIM Eligible access with 'Contributor' role to a user for 30 days on a subscription.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -DurationInDays 30 `
                               -RoleName "Contributor" `
                               -PrincipalName "PI:EMAIL" `
                               -DoNotOpenOutputFolder
      ```
      Example 2:  Grant PIM Eligible access with 'Owner' role to a user for 20 days on a resource group 'DemoRG'.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -DurationInDays 20 `
                               -ResourceGroupName "DemoRG" `
                               -RoleName "Owner" `
                               -PrincipalName "PI:EMAIL" `
                               -DoNotOpenOutputFolder
      ```
      Example 3:  Grant PIM Eligible access with 'Owner' role to a user for 30 days on a resource 'AppServiceDemo'.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -DurationInDays 30 `
                               -ResourceGroupName "DemoRG" `
                               -ResourceName "AppServiceDemo" `
                               -RoleName "Owner" `
                               -PrincipalName "PI:EMAIL" `
                               -DoNotOpenOutputFolder
      ```
      Example 4:  Grant PIM Active access with 'Reader' role to a user for 30 days on a resource 'AppServiceDemo'.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignRole `
                               -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                               -DurationInDays 30 `
                               -ResourceGroupName "DemoRG" `
                               -ResourceName "AppServiceDemo" `
                               -RoleName "Reader" `
                               -PrincipalName "PI:EMAIL" `
                               -AssignmentType "Active" `
                               -DoNotOpenOutputFolder
      ```
  2.  Activating your roles (-ActivateMyRole) 
      Use this command to activate your PIM access.
      > NOTE:  
      > a. Activation duration should range between 1 to 8 hours.  
      > b. Make sure that the PIM role you are activating is eligible. If your PIM role has expired, contact subscription administrator to renew/re-assign your PIM role.  
      ```PowerShell
      Set-AzSKPIMConfiguration -ActivateMyRole `
                              -SubscriptionId  `
                              -RoleName  `
                              -DurationInHours  `
                              -Justification  `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Activate your PIM access on a resource group.
      ```PowerShell
      Set-AzSKPIMConfiguration -ActivateMyRole `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleName "Owner" `
                              -DurationInHours 8 `
                              -Justification "Add a valid justification for enabling PIM role" `
                              -ResourceGroupName "DemoRG" `
                              -DoNotOpenOutputFolder
      ```
  3.  Deactivating your roles (-DeactivateMyRole) 
      Use this command to deactivate your PIM access.
      ```PowerShell
      Set-AzSKPIMConfiguration -DeactivateMyRole `
                              -SubscriptionId  `
                              -RoleName  `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `
                              [-DoNotOpenOutputFolder]
      ```
      Example 1:  Deactivate your PIM access on a subscription.
      ```PowerShell
      Set-AzSKPIMConfiguration -DeactivateMyRole `
                              -SubscriptionId "65be5555-34ee-43a0-ddee-23fbbccdee45" `
                              -RoleName "Owner" `
                              -DoNotOpenOutputFolder
      ```
  4.  Assign PIM to permanent assignments at subscription/RG scope  (-AssignEligibleforPermanentAssignments) 
      Use this command to change permanent assignments to PIM for specified roles, at the specified scope. 
      > NOTE:  
      > This command will create PIM, but will not remove the permanent assignments. After converting permanent assignments to PIM, you can use *"Set-AzSKPIMConfiguration -RemovePermanentAssignments"* command with *"-RemoveAssignmentFor MatchingEligibleAssignments"* parameter to remove permanent assignment.
      ```PowerShell
      Set-AzSKPIMConfiguration -AssignEligibleforPermanentAssignments `
                              -SubscriptionId  `
                              -RoleNames  `
                              -DurationInDays  `
                              [-ResourceGroupName ] `
                              [-ResourceName ] `