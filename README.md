# Technical Lesson: SQL Subqueries

A subquery, also known as a nested query or inner query, is an SQL query that is embedded within another SQL query. The primary purpose of a subquery is to enable complex data retrieval by using the results of one query as the input for another. This technique allows for sophisticated data manipulation and filtering, which can be particularly useful in scenarios where direct queries may not suffice.

Key Features of Subqueries:

* Nested within Other Queries: Subqueries are written inside the main query, usually enclosed in parentheses.
* Single or Multiple Results: Depending on the context, a subquery can return a single value, a list of values, or even a full table of results.
* Use Cases: Subqueries are versatile and can be used in various SQL clauses, including `SELECT`, `FROM`, `WHERE`, `HAVING`, and `JOIN`. This flexibility makes them indispensable for tasks such as filtering data, chaining aggregates, and making complex comparisons.

As a software engineer working for a model toy company, you often deal with vast amounts of data that need to be analyzed, filtered, and aggregated in different ways. Subqueries can help streamline this process, enabling you to perform operations that would otherwise require multiple steps or intermediate tables. In particular, you will use subqueries to determine the employees from the United States, to find all of the employees from offices with at least 5 employees, change aggregates to find multiple payment averages, and use the employee number in the employees table and the matching sales reprepresentative employee number in the customers table.

## Set Up

* Fork and Clone the GitHub Repo
* Install dependencies and enter the virtual environment:
    * `pipenv install`
    * `pipenv shell`

## Instructions

We will be using the CRM database with the familiar schema.

![Northwinds database ERM diagram](/assets/erm-data-orders.png)

### Step 1: Connecting to the Data

```python
import sqlite3
import pandas as pd
conn = sqlite3.Connection('data.sqlite')
```

### Step 2: Substituting JOIN with Subqueries

Let's start with a query of employees from the United States. Using your current knowledge, you could solve this using a join.

```python
q = """
SELECT lastName, firstName, officeCode
FROM employees
JOIN offices
    USING(officeCode)
WHERE country = "USA"
;"""

print(pd.read_sql(q, conn))
```

Query of Employees:

| # | lastName  | firstName | officeCode |
|---|-----------|-----------|-------------|
| 0 | Bow       | Anthony   | 1           |
| 1 | Firrelli  | Jeff      | 1           |
| 2 | Jennings  | Leslie    | 1           |
| 3 | Murphy    | Diane     | 1           |
| 4 | Patterson | Mary      | 1           |
| 5 | Thompson  | Leslie    | 1           |
| 6 | Firrelli  | Julie     | 2           |
| 7 | Patterson | Steve     | 2           |
| 8 | Tseng     | Foon Yue  | 3           |
| 9 | Vanauf    | George    | 3           |

### Step 3: Subquery

Another approach would be to use a subquery. Here's what it would look like:

```python
q = """
SELECT lastName, firstName, officeCode
FROM employees
WHERE officeCode IN (SELECT officeCode
                     FROM offices 
                     WHERE country = "USA")
;
"""
print(pd.read_sql(q, conn))
```

| # | lastName   | firstName | officeCode |
|---|------------|-----------|-------------|
| 0 | Murphy     | Diane     | 1           |
| 1 | Patterson  | Mary      | 1           |
| 2 | Firrelli   | Jeff      | 1           |
| 3 | Bow        | Anthony   | 1           |
| 4 | Jennings   | Leslie    | 1           |
| 5 | Thompson   | Leslie    | 1           |
| 6 | Firrelli   | Julie     | 2           |
| 7 | Patterson  | Steve     | 2           |
| 8 | Tseng      | Foon Yue  | 3           |
| 9 | Vanauf     | George    | 3           |

There it is, a query within a query! This can be very helpful and also allow you to break down problems into constituent parts. Often queries can be formulated in multiple ways as with the above example. Other times, using a subquery might be essential. For example, what if you wanted to find all of the employees from offices with at least 5 employees?

### Step 4: Subqueries for Filtering Based on an Aggregation

Think for a minute about how you might write such a query.

Now that you've had a minute to think it over, you might see some of the challenges with this query. On the one hand, we are looking to filter based on an aggregate condition: the number of employees per office. You know how to do this using the GROUP BY and HAVING clauses, but the data we wish to retrieve is not aggregate data. We only wish to filter based on the aggregate, not retrieve aggregate data. As such, this is a natural place to use a subquery.

```python
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
print(pd.read_sql(q, conn))
```

| #  | lastName   | firstName | officeCode |
|----|------------|-----------|-------------|
| 0  | Murphy     | Diane     | 1           |
| 1  | Patterson  | Mary      | 1           |
| 2  | Firrelli   | Jeff      | 1           |
| 3  | Bondur     | Gerard    | 4           |
| 4  | Bow        | Anthony   | 1           |
| 5  | Jennings   | Leslie    | 1           |
| 6  | Thompson   | Leslie    | 1           |
| 7  | Bondur     | Loui      | 4           |
| 8  | Hernandez  | Gerard    | 4           |
| 9  | Castillo   | Pamela    | 4           |
| 10 | Gerard     | Martin    | 4           |

### Step 5: Chaining Aggregates

You can chain queries like this in many fashions. For example, maybe you want to find the average of individual customers' average payments:

(It might be more interesting to investigate the standard deviation of customer's average payments, but standard deviation is not natively supported in SQLite as it is in other SQL versions like PostgreSQL.)

```python
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
print(pd.read_sql(q, conn))
```

| # | averagePayment |
|---|----------------|
| 0 | 31489.754582   |

### Step 6: Foreign Key Reference

You can also run subqueries that reference keys with different names between different tables. For example you can use the employee number in the employees table and the matching sales rep employee number in the customers table.

```python
q = """
SELECT lastName, firstName, employeeNumber
FROM employees
WHERE employeeNumber IN (SELECT salesRepEmployeeNumber
                     FROM customers 
                     WHERE country = "USA")
;
"""
print(pd.read_sql(q, conn))
```

Subquery with reference keys:

| # | lastName  | firstName | employeeNumber |
|---|-----------|-----------|----------------|
| 0 | Jennings  | Leslie    | 1165           |
| 1 | Thompson  | Leslie    | 1166           |
| 2 | Firrelli  | Julie     | 1188           |
| 3 | Patterson | Steve     | 1216           |
| 4 | Tseng     | Foon Yue  | 1286           |
| 5 | Vanauf    | George    | 1323           |

Consider how this query is returning different information than the ones above. It is looking at customers in the USA and the employee that represents them, not employees in the USA.

```python
# Remember to close the connection when you are done
conn.close()
```

## Considerations

Subqueries in SQL provide flexibility for handling complex queries, but they also present challenges, particularly regarding performance and readability.

When substituting `JOINs` with subqueries, there can be performance overhead, and the logic might become harder to understand. Filtering based on aggregation using subqueries can be resource-intensive, especially if the subquery returns a large dataset. Chaining aggregates through subqueries adds complexity and can lead to performance bottlenecks. Additionally, using subqueries with foreign key references requires careful management of referential integrity to ensure accurate results.

To address these challenges, it’s important to weigh the trade-offs and consider alternative approaches, such as using `JOINs` or derived tables, depending on the specific use case.
