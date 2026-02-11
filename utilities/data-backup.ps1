# backup-complete.ps1
$date = Get-Date -Format "yyyy-MM-dd"
$backupDir = "C:\odoo-bar\backups"

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}

Write-Host "Backing up database..."
# This gets your DATA from the postgres container
docker exec odoo_bar_db pg_dump -U odoo my_bar | Out-File -Encoding UTF8 "$backupDir\my_bar_$date.sql"

Write-Host "Backing up Odoo files..."
# This gets uploaded files, product images, etc.
docker cp odoo_bar:/var/lib/odoo/filestore "$backupDir\filestore_$date"

Write-Host "Creating archive..."
Compress-Archive -Path "$backupDir\my_bar_$date.sql", "$backupDir\filestore_$date" -DestinationPath "$backupDir\complete_$date.zip" -Force

# Cleanup
Remove-Item "$backupDir\my_bar_$date.sql"
Remove-Item -Recurse "$backupDir\filestore_$date"

Write-Host "✓ Backup complete: complete_$date.zip"