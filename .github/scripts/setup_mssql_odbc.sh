#!/usr/bin/env bash

set -xve
#Repurposed from https://github.com/Yarden-zamir/install-mssql-odbc

VERSION_ID="$(awk -F= '$1=="VERSION_ID"{gsub(/"/, "", $2); print $2}' /etc/os-release)"
PKG_NAME="packages-microsoft-prod.deb"

FILE_MANIFEST_URL="https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/FILE_MANIFEST"
FILE_MANIFEST="hashes.txt"

curl -sSL -o "${FILE_MANIFEST}" "${FILE_MANIFEST_URL}"

expected_hash=$(grep "${PKG_NAME}" "${FILE_MANIFEST}" | cut -d',' -f2)

curl -sSL -O "https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/${PKG_NAME}"
printf "%s *packages-microsoft-prod.deb\n" "${expected_hash}" | sha256sum -c -

# Add the Microsoft GPG key since the deb package does not do it automatically
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor --batch -o /usr/share/keyrings/microsoft-prod.gpg

sudo dpkg -i packages-microsoft-prod.deb
#rm packages-microsoft-prod.deb

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
