#!/usr/bin/env python3
"""Behavioural checks for equity metric, distributions and dilution mappings."""
from dataclasses import replace
from math import isclose
import unittest

from terminal_multiple import TerminalCase, distributions_future_value, mature_ps, central_valuation


class TerminalMappingTests(unittest.TestCase):
    def test_fixed_family_weights(self):
        self.assertAlmostEqual(central_valuation(100), 100)
        self.assertAlmostEqual(central_valuation(200), 200)
        self.assertAlmostEqual(central_valuation(120) - central_valuation(100), 20)

    def test_separate_cash_and_interest_definition(self):
        # Core NI60 excludes5 of cash interest;100 cash is a company total.
        case = TerminalCase('P/E', 60, 10, 20, 2, .10, 1, 100, 'Separate')
        self.assertAlmostEqual(case.terminal_equity_value, 1300)
        self.assertAlmostEqual(case.supported_price, 131 / 1.1**2)
        self.assertAlmostEqual(case.implied_total(case.supported_price), 60)
        self.assertGreater(replace(case, terminal_cash=200).supported_price, case.supported_price)
        self.assertLess(replace(case, terminal_cash=-100).supported_price, case.supported_price)
        # Same equity value can be expressed as an all-in P/E, with no second cash add.
        included = TerminalCase('P/E', 65, 10, 1300/65, 2, .10, 1)
        self.assertAlmostEqual(case.supported_price, included.supported_price)
        with self.assertRaisesRegex(ValueError, 'must not be added again'):
            replace(included, terminal_cash=100)

    def test_common_date_aggregate_and_per_share_dilution(self):
        case = TerminalCase('P/E', 60, 10*1.02**4, 20, 4, .12, 0, 100, 'Separate')
        aggregate_pv = case.terminal_equity_value / case.factor
        prior_holder_equivalent = case.supported_price * 10
        self.assertAlmostEqual(aggregate_pv / prior_holder_equivalent, 1.02**4)

    def test_pe_forward_inverse_and_return(self):
        # Year-two EPS=6 at 20x, plus 1 distribution FV; 121/1.1^2=100.
        case = TerminalCase("P/E", 60, 10, 20, 2, .10, 1)
        self.assertAlmostEqual(case.supported_price, 100)
        self.assertAlmostEqual(case.implied_total(100), 60)
        self.assertAlmostEqual(case.expected_cagr(100), .10)

    def test_ps_equivalence_and_margin(self):
        ps = TerminalCase("P/S", 300, 10, mature_ps(20, .20), 2, .10, 1)
        pe = TerminalCase("P/E", 60, 10, 20, 2, .10, 1)
        self.assertAlmostEqual(ps.supported_price, pe.supported_price)
        self.assertAlmostEqual(ps.implied_total(100), 300)
        self.assertLess(replace(ps, exit_multiple=mature_ps(20, .10)).supported_price, ps.supported_price)

    def test_pb_roe_and_equity_capital(self):
        pb = TerminalCase("P/B", 600, 10, 2, 2, .10, 1)
        pe = TerminalCase("P/E", 600 * .10, 10, 20, 2, .10, 1)
        self.assertAlmostEqual(pb.supported_price, pe.supported_price)
        self.assertAlmostEqual(pb.implied_total(100), 600)
        # External capital is accompanied by new shares, not free investor value.
        recap = replace(pb, terminal_total=1200, terminal_shares=20)
        self.assertAlmostEqual(recap.supported_price, pb.supported_price)

    def test_dilution_hurdle_and_time(self):
        case = TerminalCase("P/E", 60, 10, 20, 2, .10, 1)
        self.assertLess(replace(case, terminal_shares=12).supported_price, case.supported_price)
        self.assertGreater(replace(case, terminal_shares=12).implied_total(100), case.implied_total(100))
        self.assertLess(replace(case, required_return=.15).supported_price, case.supported_price)
        self.assertLess(replace(case, horizon=5).supported_price, case.supported_price)
        for metric in ("P/E", "P/S", "P/B", "P/TBV"):
            variant = replace(case, metric=metric)
            self.assertTrue(isclose(variant.implied_total(variant.supported_price), variant.terminal_total))

    def test_distribution_timing_and_no_double_count(self):
        self.assertAlmostEqual(distributions_future_value([(1, 2), (2, 2)], 2, .10), 4.2)
        self.assertEqual(distributions_future_value([(1, 2), (2, 2)], 2, 0), 4)
        case = TerminalCase("P/E", 60, 10, 20, 2, .10, 130)
        self.assertEqual(case.implied_total(100), 0)
        self.assertGreater(case.expected_cagr(100), .10)

    def test_invalid_inputs(self):
        case = TerminalCase("P/E", 60, 10, 20, 2, .10, 1)
        for values in ({"metric": "EV/Sales"}, {"terminal_total": -1}, {"terminal_shares": 0},
                       {"exit_multiple": 0}, {"horizon": 0}, {"required_return": float("nan")},
                       {"distributions_fv": -1}, {"terminal_cash": float('nan')},
                       {"cash_treatment": 'Unknown'}, {"terminal_cash": 100},
                       {"terminal_cash": -2000, "cash_treatment": 'Separate'}):
            with self.assertRaises(ValueError):
                replace(case, **values)
        with self.assertRaises(ValueError):
            distributions_future_value([(3, 1)], 2, 0)
        with self.assertRaises(ValueError):
            mature_ps(20, 0)


if __name__ == "__main__":
    unittest.main()
