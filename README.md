The Budget Tracker is a user-friendly application that allows you to create and manage multiple bank accounts, record transactions (income, expenses, and transfers), and get an overview of your financial activities through a clean and interactive dashboard.

## Features

- **User Authentication**: Secure user registration and login system.
- **Dashboard**: A central hub to view your recent transactions and account balances at a glance.
- **Account Management**:
    - Create multiple accounts (e.g., checking, savings, wallet).
    - View a list of all your accounts with their current balances.
    - Rename and delete accounts.
- **Transaction Management**:
    - Add income, expense, and transfer transactions.
    - View a detailed history of all transactions.
    - Edit and delete transactions, with automatic balance recalculation.
- **Dynamic Interface**: Many actions are handled asynchronously using AJAX, providing a smooth and fast user experience.

## Technologies Used

- **Backend**:
    - Django
- **Database**:
    - PostgreSQL (with `psycopg2-binary`)
- **Frontend**:
    - HTML5
    - CSS3
    - JavaScript
- **Deployment**:
    - [Gunicorn](https://gunicorn.org/)
    - [Whitenoise](http://whitenoise.evans.io/en/stable/)

## Usage

- Navigate to `/signup` to create a new account.
- Log in through the `/` (signin) page.
- Use the dashboard to get an overview of your finances.
- Go to the "Accounts" page to manage your bank accounts.
- Add new transactions directly from the dashboard.
