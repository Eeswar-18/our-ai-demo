"""
Simulated business environment for our-ai-demo V0.
Provides a deterministic demo business with customers, payments, subscriptions, and plans.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from app.core.config import get_settings


class Simulator:
    """Manages the simulated business environment."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.settings = get_settings()
        if db_path is None:
            # Default to data/demo.db in the project root
            self.db_path = Path(__file__).parent.parent.parent / "data" / "demo.db"
            # Ensure the data directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
            # If it's not an in-memory database, ensure the directory exists
            if str(db_path) != ":memory:":
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the database
        self._init_db()
        # Load demo data
        self._load_demo_data()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn

    def _execute_and_close(self, conn: sqlite3.Connection):
        """Commit and close a connection."""
        conn.commit()
        conn.close()

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Create customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create plans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    features TEXT  -- JSON string of features
                )
            """)
            # Create subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    plan_id INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'canceled')),
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (plan_id) REFERENCES plans (id)
                )
            """)
            # Create payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    transaction_id TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'pending')),
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def _load_demo_data(self):
        """Load demo data if the tables are empty."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Check if we already have data
            try:
                cursor.execute("SELECT COUNT(*) FROM customers")
                if cursor.fetchone()[0] > 0:
                    return  # Data already loaded
            except sqlite3.OperationalError:
                # If the table doesn't exist, we need to load the data
                pass

            # Insert demo customers
            customers = [
                (1, "John Doe", "john.doe@example.com"),
                (2, "Jane Smith", "jane.smith@example.com"),
                (3, "Bob Johnson", "bob.johnson@example.com"),
            ]
            cursor.executemany(
                "INSERT OR IGNORE INTO customers (id, name, email) VALUES (?, ?, ?)",
                customers,
            )

            # Insert demo plans
            plans = [
                (1, "Basic", 9.99, '{"feature1": true, "feature2": false}'),
                (2, "Pro", 19.99, '{"feature1": true, "feature2": true, "feature3": true}'),
                (3, "Enterprise", 49.99, '{"feature1": true, "feature2": true, "feature3": true, "feature4": true, "feature5": true}'),
            ]
            cursor.executemany(
                "INSERT OR IGNORE INTO plans (id, name, price, features) VALUES (?, ?, ?, ?)",
                plans,
            )

            # Insert demo subscriptions
            subscriptions = [
                (1, 1, 1, "active", "2026-01-01 00:00:00", None),  # John Doe on Basic
                (2, 2, 2, "inactive", "2026-01-01 00:00:00", None),  # Jane Smith on Pro (inactive)
                (3, 3, 3, "active", "2026-01-01 00:00:00", None),  # Bob Johnson on Enterprise
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO subscriptions
                (id, customer_id, plan_id, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                subscriptions,
            )

            # Insert demo payments
            payments = [
                (1, 1, "txn_123456", 9.99, "success", "2026-01-01 00:00:00"),
                (2, 2, "txn_789012", 19.99, "failed", "2026-01-01 00:00:00"),
                (3, 3, "txn_345678", 49.99, "success", "2026-01-01 00:00:00"),
                (4, 1, "txn_901234", 9.99, "success", "2026-01-15 00:00:00"),  # Second payment for John
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO payments
                (id, customer_id, transaction_id, amount, status, payment_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payments,
            )

            conn.commit()
        finally:
            conn.close()

    # --- Customer methods ---
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a customer by email."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM customers WHERE email = ?", (email,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get a customer by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM customers WHERE id = ?", (customer_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # --- Payment methods ---
    def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a payment by transaction ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM payments WHERE transaction_id = ?", (transaction_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_payments_by_customer_id(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get all payments for a customer."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM payments WHERE customer_id = ? ORDER BY payment_date DESC",
                (customer_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # --- Subscription methods ---
    def get_active_subscription_by_customer_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get the active subscription for a customer."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT s.*, p.name as plan_name, p.price as plan_price
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.id
                WHERE s.customer_id = ? AND s.status = 'active'
                """,
                (customer_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_subscription_by_customer_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get any subscription for a customer (most recent)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT s.*, p.name as plan_name, p.price as plan_price
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.id
                WHERE s.customer_id = ?
                ORDER BY s.start_date DESC
                LIMIT 1
                """,
                (customer_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # --- Plan methods ---
    def get_plan_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get a plan by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM plans WHERE id = ?", (plan_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # --- Action methods ---
    def reactivate_subscription(self, customer_id: int) -> bool:
        """Reactivate the subscription for a customer.
        Returns True if successful, False if no subscription to reactivate.
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE subscriptions
                SET status = 'active', end_date = NULL
                WHERE customer_id = ? AND status = 'inactive'
                """,
                (customer_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # For demo purposes, we can also simulate a failed reactivation
    # but we'll keep it deterministic for now.