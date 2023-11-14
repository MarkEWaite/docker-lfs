Import-Module -DisableNameChecking -Force $PSScriptRoot/../jenkins-support.psm1

function Test-CommandExists($command) {
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = 'stop'
  $res = $false
  try {
      if(Get-Command $command) { 
          $res = $true 
      }
  } catch {
      $res = $false 
  } finally {
      $ErrorActionPreference=$oldPreference
  }
  return $res
}

# check dependencies
if(-Not (Test-CommandExists docker)) {
    Write-Error "docker is not available"
}

function Retry-Command {
    [CmdletBinding()]
    param (
        [parameter(Mandatory, ValueFromPipeline)] 
        [ValidateNotNullOrEmpty()]
        [scriptblock] $ScriptBlock,
        [int] $RetryCount = 3,
        [int] $Delay = 30,
        [string] $SuccessMessage = "Command executed successfully!",
        [string] $FailureMessage = "Failed to execute the command"
        )
        
    process {
        $Attempt = 1
        $Flag = $true
        
        do {
            try {
                $PreviousPreference = $ErrorActionPreference
                $ErrorActionPreference = 'Stop'
                Invoke-Command -NoNewScope -ScriptBlock $ScriptBlock -OutVariable Result 4>&1              
                $ErrorActionPreference = $PreviousPreference

                # flow control will execute the next line only if the command in the scriptblock executed without any errors
                # if an error is thrown, flow control will go to the 'catch' block
                Write-Verbose "$SuccessMessage `n"
                $Flag = $false
            }
            catch {
                if ($Attempt -gt $RetryCount) {
                    Write-Verbose "$FailureMessage! Total retry attempts: $RetryCount"
                    Write-Verbose "[Error Message] $($_.exception.message) `n"
                    $Flag = $false
                } else {
                    Write-Verbose "[$Attempt/$RetryCount] $FailureMessage. Retrying in $Delay seconds..."
                    Start-Sleep -Seconds $Delay
                    $Attempt = $Attempt + 1
                }
            }
        }
        While ($Flag)
    }
}

function Get-SutImage {
    $DOCKERFILE = Get-EnvOrDefault 'DOCKERFILE' ''
    $IMAGENAME = Get-EnvOrDefault 'CONTROLLER_IMAGE' '' # Ex: jdk17-hotspot-windowsservercore-ltsc2019

    $REAL_DOCKERFILE=Resolve-Path -Path "$PSScriptRoot/../${DOCKERFILE}"

    if(!($DOCKERFILE -match '^(?<os>.+)[\\/](?<flavor>.+)[\\/](?<jvm>.+)[\\/]Dockerfile$') -or !(Test-Path $REAL_DOCKERFILE)) {
        Write-Error "Wrong Dockerfile path format or file does not exist: $DOCKERFILE"
        exit 1
    }

    return "pester-jenkins-$IMAGENAME"
}

function Run-Program($cmd, $params, $verbose=$false) {
    if($verbose) {
        Write-Host "$cmd $params"
    }
    $psi = New-Object System.Diagnostics.ProcessStartInfo 
    $psi.CreateNoWindow = $true 
    $psi.UseShellExecute = $false 
    $psi.RedirectStandardOutput = $true 
    $psi.RedirectStandardError = $true
    $psi.WorkingDirectory = (Get-Location)
    $psi.FileName = $cmd 
    $psi.Arguments = $params
    $proc = New-Object System.Diagnostics.Process 
    $proc.StartInfo = $psi 
    [void]$proc.Start()
    $stdout = $proc.StandardOutput.ReadToEnd() 
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit() 
    if($proc.ExitCode -ne 0) {
        Write-Host "`n`nstdout:`n$stdout`n`nstderr:`n$stderr`n`n"
    }

    return $proc.ExitCode, $stdout, $stderr
}

function Build-Docker($tag) {
    $exitCode, $stdout, $stderr = Run-Program 'docker-compose' '--file=build-windows.yaml build --parallel'
    if($exitCode -ne 0) {
        return $exitCode, $stdout, $stderr
    }
    return(Run-Program 'docker' $('tag {0}/{1}:{2} {3}' -f $env:DOCKERHUB_ORGANISATION, $env:DOCKERHUB_REPO, $env:CONTROLLER_IMAGE, $tag))
}

function Build-DockerChild($tag, $dir) {
    Get-Content "$dir/Dockerfile-windows" | ForEach-Object{$_ -replace "FROM bats-jenkins","FROM $(Get-SutImage)" } | Out-File -FilePath "$dir/Dockerfile-windows.tmp" -Encoding ASCII
    return (Run-Program 'docker.exe' "build -t `"$tag`" $args -f `"$dir/Dockerfile-windows.tmp`" `"$dir`"")
}

function Get-JenkinsUrl($Container) {
    $DOCKER_IP=(Get-EnvOrDefault 'DOCKER_HOST' 'localhost') | %{$_ -replace 'tcp://(.*):[0-9]*','$1'} | Select-Object -First 1
    $port = (docker port "$CONTAINER" 8080 | %{$_ -split ':'})[1]
    return "http://$($DOCKER_IP):$($port)"
}

function Get-JenkinsPassword($Container) {
    $res = docker exec $Container powershell.exe -c 'if(Test-Path "C:\ProgramData\Jenkins\JenkinsHome\secrets\initialAdminPassword") { Get-Content "C:\ProgramData\Jenkins\JenkinsHome\secrets\initialAdminPassword" ; exit 0 } else { exit -1 }'
    if($lastExitCode -eq 0) {
        return $res
    }
    return $null
}

function Run-In-Script-Console($Container, $Script) {
    $jenkinsPassword = Get-JenkinsPassword $Container
    $jenkinsUrl = Get-JenkinsUrl $Container
    if($null -ne $jenkinsPassword) {
        $pair = "admin:$($jenkinsPassword)"
        $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
        $basicAuthValue = "Basic $encodedCreds"
        $Headers = @{ Authorization = $basicAuthValue }

        $crumb = (Invoke-RestMethod -Uri $('{0}{1}' -f $jenkinsUrl, '/crumbIssuer/api/json') -Headers $Headers -TimeoutSec 60 -Method Get -SessionVariable session -UseBasicParsing).crumb
        if ($null -ne $crumb) {
            $Headers += @{ "Jenkins-Crumb" = $crumb }
        }
        $body = @{ script = $Script }
        $res = Invoke-WebRequest -Uri $('{0}{1}' -f $jenkinsUrl, '/scriptText') -Headers $Headers -TimeoutSec 60 -Method Post -WebSession $session -UseBasicParsing -Body $body
        if ($res.StatusCode -eq 200) {
            return $res.Content.replace('Result: ', '')
        }
    }
    return $null    
}

function Test-Url($Container, $Url) {
    $jenkinsPassword = Get-JenkinsPassword $Container
    $jenkinsUrl = Get-JenkinsUrl $Container
    if($null -ne $jenkinsPassword) {
        $pair = "admin:$($jenkinsPassword)"
        $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
        $basicAuthValue = "Basic $encodedCreds"
        $Headers = @{ Authorization = $basicAuthValue }

        $res = Invoke-WebRequest -Uri $('{0}{1}' -f $jenkinsUrl, $Url) -Headers $Headers -TimeoutSec 60 -Method Head -UseBasicParsing
        if($res.StatusCode -eq 200) {
            return $true
        } 
    }
    Write-Error "URL $(Get-JenkinsUrl $Container)$Url failed"
    return $false    
}

function Cleanup($image) {
    docker kill "$image" 2>&1 | Out-Null
    docker rm -fv "$image" 2>&1 | Out-Null
}

function Unzip-Manifest($Container, $Plugin, $Work) {
    return (Run-Program "docker.exe" "run --rm -v `"${Work}:C:\ProgramData\Jenkins\JenkinsHome`" $Container mkdir C:/ProgramData/Jenkins/temp | Out-Null ; Copy-Item C:/ProgramData/Jenkins/JenkinsHome/plugins/$Plugin C:/ProgramData/Jenkins/temp/$Plugin.zip ; Expand-Archive C:/ProgramData/Jenkins/temp/$Plugin.zip -Destinationpath C:/ProgramData/Jenkins/temp ; `$content = Get-Content C:/ProgramData/Jenkins/temp/META-INF/MANIFEST.MF ; Remove-Item -Force -Recurse C:/ProgramData/Jenkins/temp ; Write-Host `$content ; exit 0")
}
