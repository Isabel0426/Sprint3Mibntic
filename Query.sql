-- SQLite

USE app_web_flask;

CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  email_verified_at CURRENT_TIMESTAMP NULL,
  created_at CURRENT_TIMESTAMP,
  updated_at CURRENT_TIMESTAMP
);

CREATE TABLE mail_register(
  user INTEGER NOT NULL,
  comments TEXT NULL,
  created_at CURRENT_TIMESTAMP,
  updated_at CURRENT_TIMESTAMP,
  FOREIGN KEY(user) REFERENCES users(id)
);