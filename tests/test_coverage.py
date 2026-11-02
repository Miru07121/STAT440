import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
from binomial_coverage import simulate, wilson_interval


class CoverageTests(unittest.TestCase):
    def test_reference_interval(self):
        low, high = wilson_interval(5, 10)
        self.assertAlmostEqual(low, .236593090512564, places=12)
        self.assertAlmostEqual(high, .763406909487436, places=12)

    def test_boundaries_and_symmetry(self):
        self.assertAlmostEqual(wilson_interval(0, 20)[0], 0)
        self.assertAlmostEqual(wilson_interval(20, 20)[1], 1)
        for k in range(21):
            low, high = wilson_interval(k, 20)
            opposite = wilson_interval(20 - k, 20)
            self.assertAlmostEqual(low, 1 - opposite[1])
            self.assertTrue(0 <= low <= high <= 1)

    def test_repeatability_and_global_rng_unchanged(self):
        state = random.getstate()
        first = simulate(repetitions=50)
        self.assertEqual(first, simulate(repetitions=50))
        self.assertEqual(random.getstate(), state)

    def test_deterministic_probability_boundaries(self):
        for p in [0, 1]:
            result = simulate(probability=p, repetitions=10)
            self.assertEqual(result['methods']['wald']['coverage'], 1)
            self.assertEqual(result['methods']['wald']['mean_width'], 0)
            self.assertAlmostEqual(result['methods']['wilson']['coverage'], 1)

    def test_invalid_simulation_parameters(self):
        for kwargs in [{'n': 0}, {'n': True}, {'repetitions': -1},
                       {'probability': -0.1}, {'probability': float('nan')},
                       {'probability': 1.1}, {'seed': 1.5}]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    simulate(**kwargs)

    def test_invalid_interval_parameters(self):
        for args in [(1, 0), (-1, 10), (11, 10), (.5, 10),
                     (1, 10, 0), (1, 10, 1), (1, 10, float('nan'))]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    wilson_interval(*args)

    def test_cli_outputs_json_and_rejects_bad_input(self):
        script = str(Path(__file__).resolve().parents[1] / 'binomial_coverage.py')
        result = subprocess.run([sys.executable, script, '--repetitions', '10'],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['repetitions'], 10)
        result = subprocess.run([sys.executable, script, '--n', '0'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('positive integer', result.stderr)


if __name__ == '__main__':
    unittest.main()
