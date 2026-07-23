$ProjectPath = "./vendors/pythonnet-stub-generator/csharp/PythonNetStubTool/PythonNetStubGenerator.Tool.csproj"
$SearchPath = "./data/dlls"
$DestPath = "./typings"

$dlls = Get-ChildItem -Path $SearchPath -Filter "*.dll" -Recurse |
        Where-Object { $_.FullName -notlike "*uiaccess.dll" }
        ForEach-Object { $_.FullName }

Write-Host "Found $($dlls.Count) DLL files" -ForegroundColor Green

if ($dlls.Count -eq 0) {
    Write-Host "No .NET DLLs found. Exiting." -ForegroundColor Red
    exit 1
}

$dllsString = $dlls -join ","
Write-Host "Generating stubs for $($dlls.Count) assemblies..." -ForegroundColor Yellow

$command = "dotnet run --project $ProjectPath --search-paths `"$SearchPath`" --target-dlls `"$dllsString`" --dest-path $DestPath"

Invoke-Expression $command
