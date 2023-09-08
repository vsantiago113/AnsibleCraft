# Setup and Troubleshoot WinRM

Windows Remote Management (WinRM) is Microsoft's implementation of the WS-Management Protocol, a standard Simple Object Access Protocol (SOAP)-based, firewall-friendly protocol that allows hardware and operating systems from different vendors to interoperate. WinRM is used for remote management of Windows machines and servers.

:warning: **Note**: Please remember to open your PowerShell session as an administrator when running these commands.

## More Resources

- [Windows Remote Management](https://docs.ansible.com/ansible/latest/os_guide/windows_winrm.html)
- [Setting up a Windows Host](https://docs.ansible.com/ansible/latest/os_guide/windows_setup.html)

## Table of Contents

- [Setting the Execution Policy](#setting-the-execution-policy)
- [WinRM Configuration](#winrm-configuration)
- [Installing and Configuring WinRM](#installing-and-configuring-winrm)
- [Managing Trusted Hosts](#managing-trusted-hosts)
- [Firewall Rules](#firewall-rules)
- [WinRM Listener](#winrm-listener)

---

## Setting the Execution Policy

### 1. View the current execution policy

```powershell
Get-ExecutionPolicy
```

### 2. Set the execution policy

```powershell
Set-ExecutionPolicy -Scope LocalMachine RemoteSigned -Force
```

### 3. For troubleshooting purposes set Execution Policy to Unrestricted

```powershell
Set-ExecutionPolicy -Scope LocalMachine Unrestricted -Force
```

## WinRM Configuration

### Using Command Prompt

1. Open the Command Prompt with administrative privileges.
2. Type `winrm get winrm/config` and press Enter.

## Installing and Configuring WinRM

### 1. Check if WinRM is installed

```powershell
winrm quickconfig -Force
```

### 2. Enable WinRM

```powershell
Enable-PSRemoting -Force
```

### 3. Set LocalAccountTokenFilterPolicy

```powershell
New-ItemProperty -Name LocalAccountTokenFilterPolicy -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -PropertyType DWord -Value 1 -Force
```

## Managing Trusted Hosts

### How to View Trusted Hosts

```powershell
Get-Item WSMan:\localhost\Client\TrustedHosts
```

### How to Add to Trusted Hosts

1. Add a single host by hostname or IP address:

    ```powershell
    Set-Item WSMan:\localhost\Client\TrustedHosts -Value 'MachineNameOrIPAddress' -Force
    ```

2. Append a new host to existing list:

    ```powershell
    Set-Item WSMan:\localhost\Client\TrustedHosts -Value 'MachineNameOrIPAddress' -Concatenate -Force
    ```

3. Add multiple hosts (comma-separated):

    ```powershell
    Set-Item WSMan:\localhost\Client\TrustedHosts -Value 'Machine1,Machine2' -Force
    ```

### How to Remove Trusted Hosts

1. Clear the list entirely:

    ```powershell
    Set-Item WSMan:\localhost\Client\TrustedHosts -Value '' -Force
    ```

:warning: **Important Note**: Changing Trusted Hosts can have security implications. Only add hosts that you know are secure and trusted.

## Firewall Rules

### 1. Check if the ports are open

```powershell
Get-NetFirewallRule | Where-Object { $_.Direction -eq 'Inbound' -and $_.Enabled -eq 'True' } | Get-NetFirewallPortFilter | Where-Object { $_.LocalPort -eq 5985 -or $_.LocalPort -eq 5986 }
```

### 2. To create a new inbound firewall rule

```powershell
New-NetFirewallRule -DisplayName "Windows Remote Management (HTTPS-In)" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow
```

## WinRM Listener

### 1. To view the current listeners

```powershell
winrm enumerate winrm/config/Listener
```

### 2. Configure listeners

```powershell
winrm create winrm/config/Listener?Address=*+Transport=HTTP
```

After performing these steps, remember to restart the WinRM service for the changes to take effect:

```powershell
Restart-Service WinRM
```

---

## Enable Basic Authentication for WinRM

This section will guide you on how to enable basic authentication for WinRM.

```powershell
Set-Item -Path WSMan:\localhost\Client\Auth\Basic -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true
```

### Allowing Unencrypted Traffic (Not Recommended)

```powershell
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $true
```

:warning: **Note**: Enabling Basic authentication and especially allowing unencrypted traffic can expose sensitive information. This is generally not recommended for production environments unless you are using HTTPS to encrypt the traffic.

After these changes, remember to restart the WinRM service to apply the new settings:

```powershell
Restart-Service WinRM
```

## Secure Listener Configuration with HTTPS

This script will configure WinRM to use HTTPS with a self-signed certificate.

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Remove all existing listeners
Remove-Item -Path WSMan:\localhost\Listener\* -Recurse -Force

# Configure Firewall
Set-NetFirewallRule -DisplayName "Windows Remote Management (HTTP-In)" -Enabled False
New-NetFirewallRule -DisplayName "Windows Remote Management (HTTPS-In)" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow

# Create Self-Signed Certificate
$hostname = [System.Net.Dns]::GetHostName()
$certificate = New-SelfSignedCertificate -DnsName "$hostname" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)

# Create HTTPS Listener
New-Item -Path WSMan:\LocalHost\Listener -Transport HTTPS -Address * -CertificateThumbprint $certificate.Thumbprint -Force

# Security Settings
New-ItemProperty -Name LocalAccountTokenFilterPolicy -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -PropertyType DWord -Value 1 -Force
Set-Item -Path WSMan:\localhost\Service\Auth\CbtHardeningLevel -Value Strict
Set-Item -Path WSMan:\localhost\Client\AllowUnencrypted -Value $false
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $false

# Disable Basic Auth
Set-Item -Path WSMan:\localhost\Client\Auth\Basic -Value $false
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $false

# Restart WinRM Service
Restart-Service WinRM
```

:warning: **Note**: Always remember to use secure practices when setting up any form of remote management.

After running the above script, your machine should now be configured to accept remote management requests via WinRM over HTTPS.

---

## Troubleshooting Tips

- If you encounter any errors, try running the PowerShell session as an administrator.
- Make sure the required ports are open on the firewall.
- Ensure that the computer you are trying to connect to is up and running and is available on the network.

---

That concludes the guide for setting up and troubleshooting WinRM. Follow these steps carefully to ensure a secure and effective setup.
