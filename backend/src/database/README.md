# Database setup for macOS

## Download mysql from the official site
https://dev.mysql.com/doc/refman/8.4/en/macos-installation.html

## Add mysql to Path
- navigate to your .zshrc file
- add this line: `export PATH=/usr/local/mysql/bin:$PATH`

## Run mysql locally
`mysql -u user -p password`

## Mysql settings:
##' Add the user from the .env file with this SQL command:
`CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';`
`GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';`
`FLUSH PRIVILEGES;`

### Crate an empty databse called `hem_tracker`
`CREATE DATABASE hem_tracker;`
