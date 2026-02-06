#!/bin/bash
set -e

# --- Variables (edit or load from .env) ---
DB_NAME="trading_journal"
DB_USER="journal_user"
DB_PASS="StrongPassword123"
SQL_FILE="/initdb/schema.sql"

# --- Update system ---
sudo dnf update -y

# --- Install PostgreSQL server ---
# AL2023 provides PostgreSQL via dnf modules (choose version, e.g. 15)
sudo dnf install -y postgresql-server postgresql-contrib

# --- Initialize database cluster ---
sudo postgresql-setup --initdb

# --- Enable and start PostgreSQL service ---
sudo systemctl enable postgresql
sudo systemctl start postgresql

# --- Create user and database ---
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# --- Import schema/tables from SQL file ---
if [ -f "$SQL_FILE" ]; then
  echo "📥 Importing database schema from $SQL_FILE..."
  sudo -u postgres psql -d ${DB_NAME} -f "$SQL_FILE"
else
  echo "⚠️ SQL file $SQL_FILE not found, skipping import."
fi

echo "✅ PostgreSQL installed, database '${DB_NAME}' and user '${DB_USER}' created."
