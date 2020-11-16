-- SQLite
CREATE TABLE invoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ReferenceMonth INTEGER NOT NULL,
    ReferenceYear INTEGER NOT NULL,
    Document integer VARCHAR(14) NOT NULL,
    Description VARCHAR(256),
    Amount DECIMAL(16, 2),
    IsActive TINYINT,
    CreatedAt DATETIME,
    DeactivatedAt DATETIME
);