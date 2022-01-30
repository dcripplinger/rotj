pyinstaller "src\rotj.py" -y
Copy-Item -Path "data" -Destination "dist\rotj\" -recurse -Force
Remove-Item "dist\rotj\data\state\*.json"
