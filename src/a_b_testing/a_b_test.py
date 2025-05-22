import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from dataclasses import dataclass
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest

from src.logging import logging
from src.exception import CustomException


@dataclass
class A_B_Test_Config:
    output_dir: str = os.path.join('data', 'a_b_test')
    db_path: str = 'ridewise.db'
    target_promo_id: str = 'P001'


class A_B_Test:
    def __init__(self, config: A_B_Test_Config = A_B_Test_Config()):
        self.config = config
        os.makedirs(self.config.output_dir, exist_ok=True)
        logging.info("Initialized A/B Test class with config: %s", self.config)

    def a_b_testing(self):
        try:
            # Connect to DB
            conn = sqlite3.connect(self.config.db_path)
            logging.info("Connected to database: %s", self.config.db_path)

            # Read promotions and sessions tables
            promotions = pd.read_sql_query("SELECT * FROM promotions", conn)
            sessions = pd.read_sql_query("SELECT * FROM sessions", conn)
            logging.info("Loaded promotions and sessions tables")

            # Focus on specific promo
            promo = promotions[promotions["promo_id"] == self.config.target_promo_id].iloc[0]
            test_groups = eval(promo["ab_test_groups"])
            allocations = eval(promo["test_allocation"])

            sessions['session_time'] = pd.to_datetime(sessions['session_time'], errors='coerce')
            sessions['session_time'] = pd.to_datetime(sessions['session_time'], errors='coerce', utc=True)
            start_date = pd.to_datetime(promo['start_date'], errors='coerce', utc=True)
            end_date = pd.to_datetime(promo['end_date'], errors='coerce', utc=True)
            city_scope = promo['city_scope']

            # Filter sessions in promo scope and time
            sessions_filtered = sessions[
                (sessions['city'] == city_scope) &
                (sessions['session_time'] >= start_date) &
                (sessions['session_time'] <= end_date)
            ].copy()
            logging.info("Filtered sessions for city %s between %s and %s", city_scope, start_date, end_date)

            # Assign A/B group
            np.random.seed(42)
            sessions_filtered['ab_group'] = np.random.choice(test_groups, size=len(sessions_filtered), p=allocations)
            logging.info("Randomly assigned users to A/B groups: %s", test_groups)

            # Save assigned sessions
            assigned_sessions_path = os.path.join(self.config.output_dir, 'ab_assigned_sessions.csv')
            sessions_filtered.to_csv(assigned_sessions_path, index=False)
            logging.info("Saved assigned sessions to %s", assigned_sessions_path)

            # Conversion summary
            conversion_summary = sessions_filtered.groupby('ab_group')['converted'].agg(['mean', 'count'])
            conversion_summary.rename(columns={'mean': 'conversion_rate', 'count': 'sample_size'}, inplace=True)
            logging.info("Generated conversion summary:\n%s", conversion_summary)

            summary_path = os.path.join(self.config.output_dir, 'conversion_summary.csv')
            conversion_summary.to_csv(summary_path)
            logging.info("Saved conversion summary to %s", summary_path)

            report_path = os.path.join(self.config.output_dir, 'ab_test_results.txt')
            with open(report_path, 'w') as f:

                # A. Chi-squared test
                contingency_table = pd.crosstab(sessions_filtered['ab_group'], sessions_filtered['converted'])
                chi2, p, dof, expected = chi2_contingency(contingency_table)
                f.write(f"Chi-squared Test:\nChi2 Statistic: {chi2:.4f}, p-value: {p:.4f}, Degrees of Freedom: {dof}\n\n")
                logging.info("Chi-squared test p-value: %.4f", p)

                # B. Z-test Control vs Variant
                group_data = sessions_filtered.groupby('ab_group')['converted'].agg(['sum', 'count'])

                for variant in [g for g in test_groups if g != 'Control']:
                    success = group_data.loc[['Control', variant], 'sum'].values
                    nobs = group_data.loc[['Control', variant], 'count'].values
                    zstat, pval = proportions_ztest(success, nobs)
                    f.write(f"Z-test Control vs {variant}:\nZ-statistic: {zstat:.4f}, p-value: {pval:.4f}\n\n")
                    logging.info("Z-test Control vs %s: p-value = %.4f", variant, pval)

                # Recommendation
                best_group = conversion_summary['conversion_rate'].idxmax()
                lift = (
                    conversion_summary.loc[best_group, 'conversion_rate'] -
                    conversion_summary.loc['Control', 'conversion_rate']
                )
                recommendation = f"{best_group} showed a lift of {lift:.2%} over Control. Consider rollout if statistically significant."
                f.write(f"Recommendation:\n{recommendation}\n")
                logging.info("Recommendation: %s", recommendation)

        except Exception as e:
            logging.error("Error occurred during A/B testing: %s", e)
            raise CustomException(sys, e)
if __name__ == "__main__":
    a_b_test = A_B_Test()
    a_b_test.a_b_testing()