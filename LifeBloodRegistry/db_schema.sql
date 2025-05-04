-- Drop and Recreate Database  
DROP DATABASE IF EXISTS LifeBloodRegistry;
CREATE DATABASE LifeBloodRegistry;
USE LifeBloodRegistry;

-- Create Tables  

-- Blood Banks Table  
CREATE TABLE BloodBanks (
    BloodBankID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL UNIQUE,
    Location VARCHAR(255) NOT NULL,
    ContactNo VARCHAR(20) NOT NULL UNIQUE
);

-- Donor Details Table  
CREATE TABLE DonorDetails (
    DonorID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Age INT NOT NULL CHECK (Age BETWEEN 18 AND 65),
    Gender VARCHAR(50) NOT NULL,
    BloodType VARCHAR(5) NOT NULL CHECK (BloodType IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    ContactNo VARCHAR(20) NOT NULL UNIQUE,
    Address VARCHAR(255) NOT NULL,
    LastDonationDate DATE DEFAULT NULL
);

-- Recipient Details Table  
CREATE TABLE RecipientDetails (
    RecipientID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Age INT NOT NULL CHECK (Age > 0),
    Gender VARCHAR(50) NOT NULL,
    BloodType VARCHAR(5) NOT NULL CHECK (BloodType IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    ContactNo VARCHAR(20) NOT NULL UNIQUE,
    Address VARCHAR(255) NOT NULL,
    RequestDate DATE NOT NULL
);

-- Blood Inventory Table  
CREATE TABLE BloodInventory (
    InventoryID INT PRIMARY KEY AUTO_INCREMENT,
    BloodBankID INT NOT NULL,
    BloodType VARCHAR(5) NOT NULL CHECK (BloodType IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    QuantityAvailable INT NOT NULL CHECK (QuantityAvailable >= 0),
    FOREIGN KEY (BloodBankID) REFERENCES BloodBanks(BloodBankID)
);

-- Blood Units Table  
CREATE TABLE BloodUnits (
    BloodUnitID INT PRIMARY KEY AUTO_INCREMENT,
    BloodType VARCHAR(5) NOT NULL CHECK (BloodType IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    Quantity INT NOT NULL CHECK (Quantity > 0),
    ExpiryDate DATE NOT NULL,
    BloodBankID INT NOT NULL,
    DonorID INT NOT NULL,
    RecipientID INT NOT NULL,
    FOREIGN KEY (BloodBankID) REFERENCES BloodBanks(BloodBankID),
    FOREIGN KEY (DonorID) REFERENCES DonorDetails(DonorID),
    FOREIGN KEY (RecipientID) REFERENCES RecipientDetails(RecipientID)
);

-- Blood Requests Table  
CREATE TABLE BloodRequests (
    RequestID INT PRIMARY KEY AUTO_INCREMENT,
    RecipientID INT NOT NULL,
    BloodType VARCHAR(5) NOT NULL CHECK (BloodType IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    Quantity INT NOT NULL CHECK (Quantity > 0),
    RequestDate DATE NOT NULL,
    Status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (RecipientID) REFERENCES RecipientDetails(RecipientID)
);

-- Blood Request Audit Table  
CREATE TABLE BloodRequestAudit (
    AuditID INT PRIMARY KEY AUTO_INCREMENT,
    RequestID INT NOT NULL,
    RecipientID INT NOT NULL,
    BloodType VARCHAR(5) NOT NULL,
    Quantity INT NOT NULL,
    RequestDate DATE NOT NULL,
    Status VARCHAR(50) NOT NULL,
    FOREIGN KEY (RequestID) REFERENCES BloodRequests(RequestID)
);



-- Triggers  
DELIMITER //

CREATE TRIGGER UpdateBloodInventoryTrigger
AFTER INSERT ON BloodUnits
FOR EACH ROW
BEGIN
    UPDATE BloodInventory
    SET QuantityAvailable = QuantityAvailable + NEW.Quantity
    WHERE BloodBankID = NEW.BloodBankID AND BloodType = NEW.BloodType;
END;
//

CREATE TRIGGER PreventExcessRequest
BEFORE INSERT ON BloodRequests
FOR EACH ROW
BEGIN
    DECLARE available_quantity INT;
    SELECT QuantityAvailable INTO available_quantity
    FROM BloodInventory
    WHERE BloodBankID = (SELECT BloodBankID FROM BloodUnits WHERE BloodType = NEW.BloodType LIMIT 1)
      AND BloodType = NEW.BloodType;

    IF available_quantity < NEW.Quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Requested blood quantity exceeds available inventory.';
    END IF;
END;
//

CREATE TRIGGER AuditBloodRequestTrigger
AFTER INSERT ON BloodRequests
FOR EACH ROW
BEGIN
    INSERT INTO BloodRequestAudit (RequestID, RecipientID, BloodType, Quantity, RequestDate, Status)
    VALUES (NEW.RequestID, NEW.RecipientID, NEW.BloodType, NEW.Quantity, NEW.RequestDate, NEW.Status);
END;
//

DELIMITER ;



-- Views  
CREATE VIEW DonationSummary AS
SELECT d.Name AS DonorName, d.BloodType, d.LastDonationDate, r.Name AS RecipientName, r.BloodType AS RecipientBloodType
FROM DonorDetails d
JOIN BloodUnits bu ON d.DonorID = bu.DonorID
JOIN RecipientDetails r ON bu.RecipientID = r.RecipientID;

CREATE VIEW InventoryStatus AS
SELECT bb.Name AS BloodBankName, i.BloodType, i.QuantityAvailable
FROM BloodBanks bb
JOIN BloodInventory i ON bb.BloodBankID = i.BloodBankID;



--  Stored Procedures, Functions, Cursors

-- Add Donor Procedure
DELIMITER //
CREATE PROCEDURE AddDonor (
    IN p_Name VARCHAR(255),
    IN p_Age INT,
    IN p_Gender VARCHAR(50),
    IN p_BloodType VARCHAR(5),
    IN p_ContactNo VARCHAR(20),
    IN p_Address VARCHAR(255),
    IN p_LastDonationDate DATE
)
BEGIN
    INSERT INTO DonorDetails (Name, Age, Gender, BloodType, ContactNo, Address, LastDonationDate)
    VALUES (p_Name, p_Age, p_Gender, p_BloodType, p_ContactNo, p_Address, p_LastDonationDate);
END;
//

-- Fulfill Request Procedure
CREATE PROCEDURE FulfillBloodRequest (
    IN p_RequestID INT
)
BEGIN
    DECLARE v_BloodType VARCHAR(5);
    DECLARE v_Quantity INT;
    DECLARE v_RecipientID INT;
    DECLARE v_BloodBankID INT;

    SELECT BloodType, Quantity, RecipientID INTO v_BloodType, v_Quantity, v_RecipientID
    FROM BloodRequests WHERE RequestID = p_RequestID;

    SELECT BloodBankID INTO v_BloodBankID
    FROM BloodInventory WHERE BloodType = v_BloodType
    ORDER BY QuantityAvailable DESC LIMIT 1;

    UPDATE BloodInventory
    SET QuantityAvailable = QuantityAvailable - v_Quantity
    WHERE BloodBankID = v_BloodBankID AND BloodType = v_BloodType;

    UPDATE BloodRequests
    SET Status = 'Fulfilled'
    WHERE RequestID = p_RequestID;

    INSERT INTO BloodUnits (BloodType, Quantity, ExpiryDate, BloodBankID, DonorID, RecipientID)
    VALUES (v_BloodType, v_Quantity, CURDATE() + INTERVAL 30 DAY, v_BloodBankID, 1, v_RecipientID);
END;
//

-- Function to Count Donors by Blood Type
CREATE FUNCTION TotalDonorsByType(p_BloodType VARCHAR(5))
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM DonorDetails WHERE BloodType = p_BloodType;
    RETURN total;
END;
//

-- Cursor to Show Donor Contact Info
CREATE PROCEDURE ListAllDonors()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE dName VARCHAR(255);
    DECLARE dContact VARCHAR(20);
    DECLARE donor_cursor CURSOR FOR SELECT Name, ContactNo FROM DonorDetails;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN donor_cursor;
    read_loop: LOOP
        FETCH donor_cursor INTO dName, dContact;
        IF done THEN LEAVE read_loop; END IF;
        SELECT CONCAT('Name: ', dName, ' | Contact: ', dContact) AS DonorInfo;
    END LOOP;
    CLOSE donor_cursor;
END;
//

DELIMITER ;



-- View All Elements
SHOW DATABASES;
USE LifeBloodRegistry;
SHOW TABLES;
DESC DonorDetails;
SHOW FULL TABLES WHERE Table_Type = 'VIEW';
SHOW CREATE VIEW DonationSummary;
SHOW TRIGGERS;
SHOW CREATE TRIGGER UpdateBloodInventoryTrigger;
SHOW PROCEDURE STATUS WHERE Db = 'LifeBloodRegistry';
SHOW FUNCTION STATUS WHERE Db = 'LifeBloodRegistry';
SHOW INDEX FROM DonorDetails;
SELECT * FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_NAME = 'DonorDetails';