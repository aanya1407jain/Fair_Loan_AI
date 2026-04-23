"""
Synthetic Indian Demographic Data Generator
Generates realistic loan applicant data with Indian demographics.
Includes intentional bias patterns to test audit tools.
"""

import numpy as np
import pandas as pd
from typing import Optional


# Indian city tiers with approximate economic profiles
TIER1_CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"]
TIER2_CITIES = ["Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Bhopal", "Indore", "Nagpur"]
TIER3_CITIES = ["Agra", "Varanasi", "Meerut", "Kanpur", "Patna", "Ranchi", "Guwahati"]

GENDER_OPTIONS = ["Male", "Female", "Other"]
RELIGION_OPTIONS = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"]
EDUCATION_OPTIONS = ["Below 10th", "10th Pass", "12th Pass", "Graduate", "Post-Graduate", "Professional"]
EMPLOYMENT_OPTIONS = ["Salaried", "Self-Employed", "Business", "Farmer", "Daily-Wage", "Unemployed"]


def generate_synthetic_data(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic loan application data with Indian demographics.
    Introduces realistic (but auditable) bias patterns.
    """
    rng = np.random.default_rng(seed)

    # ── Demographics ──────────────────────────────────────────────
    gender = rng.choice(GENDER_OPTIONS, n_samples, p=[0.58, 0.40, 0.02])

    city_tier = rng.choice([1, 2, 3], n_samples, p=[0.35, 0.40, 0.25])
    city = np.where(
        city_tier == 1,
        rng.choice(TIER1_CITIES, n_samples),
        np.where(city_tier == 2, rng.choice(TIER2_CITIES, n_samples), rng.choice(TIER3_CITIES, n_samples))
    )

    age = rng.integers(21, 65, n_samples)
    religion = rng.choice(RELIGION_OPTIONS, n_samples, p=[0.75, 0.14, 0.06, 0.02, 0.01, 0.01, 0.01])

    education = rng.choice(
        EDUCATION_OPTIONS, n_samples,
        p=[0.10, 0.15, 0.20, 0.30, 0.15, 0.10]
    )

    employment = rng.choice(
        EMPLOYMENT_OPTIONS, n_samples,
        p=[0.35, 0.20, 0.15, 0.12, 0.10, 0.08]
    )

    # ── Financial features ────────────────────────────────────────
    # Base income varies by city tier and gender (realistic inequality)
    base_income = (
        (city_tier == 1) * rng.normal(65000, 25000, n_samples) +
        (city_tier == 2) * rng.normal(38000, 15000, n_samples) +
        (city_tier == 3) * rng.normal(22000, 10000, n_samples)
    )
    # Gender income gap (reflects real India data)
    income_multiplier = np.where(gender == "Male", 1.0, np.where(gender == "Female", 0.78, 0.85))
    monthly_income = np.clip(base_income * income_multiplier, 8000, 500000).astype(int)

    loan_amount = rng.integers(50000, 5000000, n_samples)
    loan_tenure_months = rng.choice([12, 24, 36, 48, 60, 84, 120], n_samples)

    existing_loans = rng.integers(0, 5, n_samples)
    credit_history_years = np.clip(rng.normal(6, 4, n_samples), 0, 30)
    num_late_payments = rng.integers(0, 10, n_samples)

    debt_to_income = np.clip(
        (loan_amount / 12) / monthly_income * rng.uniform(0.3, 0.9, n_samples),
        0.05, 2.5
    )

    # Credit score (300–900 CIBIL range)
    base_score = (
        550 +
        (credit_history_years * 8) -
        (num_late_payments * 15) -
        (existing_loans * 12) +
        (monthly_income / 5000) * 5 +
        rng.normal(0, 40, n_samples)
    )
    # Add bias: tier-3 city applicants get slightly lower scores
    base_score -= (city_tier == 3) * rng.uniform(10, 40, n_samples)
    cibil_score = np.clip(base_score, 300, 900).astype(int)

    collateral_value = np.where(
        rng.random(n_samples) < 0.6,
        rng.integers(100000, 10000000, n_samples),
        0
    )

    # ── Ground-truth label (what a "fair" model should predict) ────
    fair_approval_prob = (
        0.35 * (cibil_score - 300) / 600 +
        0.25 * np.clip(1 - debt_to_income, 0, 1) +
        0.20 * (monthly_income / 200000) +
        0.10 * (credit_history_years / 30) +
        0.10 * (collateral_value > 0).astype(float)
    )
    fair_approved = (fair_approval_prob + rng.normal(0, 0.05, n_samples) > 0.55).astype(int)

    # ── Biased model prediction (what a typical model outputs) ────
    # Adds discrimination on gender, religion, city tier
    biased_prob = fair_approval_prob.copy()
    biased_prob[gender == "Female"] -= rng.uniform(0.05, 0.12, (gender == "Female").sum())
    biased_prob[religion == "Muslim"] -= rng.uniform(0.04, 0.10, (religion == "Muslim").sum())
    biased_prob[city_tier == 3] -= rng.uniform(0.06, 0.14, (city_tier == 3).sum())
    biased_approved = (biased_prob + rng.normal(0, 0.05, n_samples) > 0.55).astype(int)

    biased_score = np.clip(biased_prob * 100, 0, 100)

    df = pd.DataFrame({
        "applicant_id": [f"APP{i:06d}" for i in range(n_samples)],
        "gender": gender,
        "age": age,
        "religion": religion,
        "city": city,
        "city_tier": city_tier,
        "education": education,
        "employment_type": employment,
        "monthly_income": monthly_income,
        "loan_amount": loan_amount,
        "loan_tenure_months": loan_tenure_months,
        "cibil_score": cibil_score,
        "existing_loans": existing_loans,
        "credit_history_years": credit_history_years.round(1),
        "num_late_payments": num_late_payments,
        "debt_to_income_ratio": debt_to_income.round(3),
        "collateral_value": collateral_value,
        "fair_approved": fair_approved,
        "model_approved": biased_approved,
        "model_score": biased_score.round(2),
    })

    return df


if __name__ == "__main__":
    df = generate_synthetic_data(1000)
    print(df.head())
    print(f"\nApproval rate: {df['model_approved'].mean():.2%}")
    print(f"Gender breakdown:\n{df.groupby('gender')['model_approved'].mean()}")
