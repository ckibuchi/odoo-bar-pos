# 1. Install Docker
# 2. Copy your docker-compose.yml
# 3. Copy your custom module to addons/
# 4. Start containers
docker-compose up -d db

# 5. Wait for postgres to start
timeout /t 10

# 6. Restore database
docker exec -i odoo_bar_db psql -U odoo -c "CREATE DATABASE my_bar;"
Get-Content backups\my_bar_2026-01-31.sql | docker exec -i odoo_bar_db psql -U odoo my_bar

# 7. Restore files
docker cp backups\filestore odoo_bar:/var/lib/odoo/filestore/my_bar

# 8. Start Odoo
docker-compose up -d odoo