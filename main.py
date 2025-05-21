import sqlite3
import pandas as pd

# Step 1
conn = sqlite3.Connection('data.sqlite')

# Step 2
q = """
SELECT lastName, firstName, officeCode
FROM employees
JOIN offices
    USING(officeCode)
WHERE country = "USA"
;"""
pd.read_sql(q, conn)
# print(pd.read_sql(q, conn))

# Step 3 - subquery
q = """
SELECT lastName, firstName, officeCode
FROM employees
WHERE officeCode IN (SELECT officeCode
                     FROM offices 
                     WHERE country = "USA")
;
"""
pd.read_sql(q, conn)
# print(pd.read_sql(q, conn))

# Step 4 - subquery for filtering based on an aggregation
q = """
SELECT lastName, firstName, officeCode
FROM employees
WHERE officeCode IN (
    SELECT officeCode 
    FROM offices 
    JOIN employees
        USING(officeCode)
    GROUP BY 1
    HAVING COUNT(employeeNumber) >= 5
)
;
"""
pd.read_sql(q, conn)
# print(pd.read_sql(q, conn))

# Step 5 - chaining aggregates
q = """
SELECT AVG(customerAvgPayment) AS averagePayment
FROM (
    SELECT AVG(amount) AS customerAvgPayment
    FROM payments
    JOIN customers
        USING(customerNumber)
    GROUP BY customerNumber
)
;"""
pd.read_sql(q, conn)
# print(pd.read_sql(q, conn))

# Step 6 - foreign key reference
q = """
SELECT lastName, firstName, employeeNumber
FROM employees
WHERE employeeNumber IN (SELECT salesRepEmployeeNumber
                     FROM customers 
                     WHERE country = "USA")
;
"""
pd.read_sql(q, conn)
print(pd.read_sql(q, conn))

conn.close()