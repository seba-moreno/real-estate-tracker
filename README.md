# Real Estate Tracker

The application enables you to manage your properties, define income and expense concepts, track rental contracts, and record all related collections and payments. It also provides a clear overview of upcoming contract expirations and displays your overall transaction balance directly on the landing page.

## Setup Instructions

1. Clone the repository

   ```bash
   git clone https://github.com/seba-moreno/real-estate-tracker.git
   cd real-state-tracker
   ```

2. Create virtual environment

   ```bash
   python3 -m venv venv
   ```

3. Activate venv:

   ```bash
   source venv/bin/activate # Mac/Linux
   venv\Scripts\activate # Windows
   ```

4. Install dependencies

   ```bash
   pipenv install
   ```

5. Run database migrations (includes initial seed)

   ```bash
   alembic upgrade head
   ```

6. Run the application

   ```bash
   uvicorn app.main:app --reload
   ```

7. On a second terminal, activate virtual environment

   ```bash
   source venv/bin/activate # Mac/Linux
   venv\Scripts\activate # Windows
   ```

8. Run Streamlit app

   ```bash
   streamlit run .\frontend\📊_Home.py
   ```

## Using the Application

1. Register your Properties
   Add each property you own or manage in the Properties section.

2. Create your Concepts
   Define all income and expense concepts that apply to your properties (e.g., rent, utilities, maintenance).

3. Link Concepts to Properties
   In the Properties → Concepts section, assign the appropriate concepts to each property to establish their relationship.

4. Declare Rental Contracts
   Go to the Contracts menu to create and manage the rental contracts associated with each property.

5. Record Transactions
   Log all collections (income) and payments (expenses) in the Transactions section by selecting the corresponding Property–Concept combination.
