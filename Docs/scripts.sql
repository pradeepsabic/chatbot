create database Chatbot
GO

CREATE TABLE ChatbotQueries (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Query NVARCHAR(1000),
    Intent NVARCHAR(100),
    Timestamp DATETIME
);

