$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('C:\Users\dofek\OneDrive\Desktop\ULTRON.lnk')
$Shortcut.TargetPath = 'D:\Downloads\Ultron-Echo-main\Ultron-Echo-main\.venv\Scripts\pythonw.exe'
$Shortcut.Arguments = '"D:\Downloads\Ultron-Echo-main\Ultron-Echo-main\main.py"'
$Shortcut.WorkingDirectory = 'D:\Downloads\Ultron-Echo-main\Ultron-Echo-main'
$Shortcut.WindowStyle = 7
$Shortcut.Description = 'Launch ULTRON'
if ('D:\Downloads\Ultron-Echo-main\Ultron-Echo-main\assets\Ultron_Lite_Logo.ico') { $Shortcut.IconLocation = 'D:\Downloads\Ultron-Echo-main\Ultron-Echo-main\assets\Ultron_Lite_Logo.ico,0' }
$Shortcut.Save()