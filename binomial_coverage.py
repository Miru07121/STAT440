"""Compare binomial interval coverage using synthetic Bernoulli samples only."""
import argparse
import json
import math
import random
from numbers import Integral, Real
from statistics import NormalDist


def wilson_interval(successes, n, confidence=.95):
    if any(isinstance(v, bool) or not isinstance(v, Integral) for v in (successes, n)):
        raise ValueError('successes and n must be integer counts')
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError('Require n > 0 and 0 <= successes <= n')
    if (isinstance(confidence, bool) or not isinstance(confidence, Real)
            or not math.isfinite(confidence) or not 0 < confidence < 1):
        raise ValueError('confidence must be between 0 and 1')
    # Lower-tail form avoids rounding (1 + confidence) / 2 to exactly 1.
    z = -NormalDist().inv_cdf((1 - confidence) / 2)
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    # Exact boundary endpoints avoid floating-point cancellation affecting coverage.
    low = 0.0 if successes == 0 else max(0.0, center - half)
    high = 1.0 if successes == n else min(1.0, center + half)
    return low, high


def simulate(n=20, probability=.1, repetitions=1000, seed=440):
    """Estimate 95% interval coverage with a local, repeatable random stream."""
    for name, value in [('n', n), ('repetitions', repetitions)]:
        if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
            raise ValueError(f'{name} must be a positive integer')
    if (isinstance(probability, bool) or not isinstance(probability, Real)
            or not math.isfinite(probability) or not 0 <= probability <= 1):
        raise ValueError('probability must be finite and between 0 and 1')
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise ValueError('seed must be an integer')
    rng = random.Random(int(seed))
    covered = {'wilson': 0, 'wald': 0}
    widths = {'wilson': 0.0, 'wald': 0.0}
    z = NormalDist().inv_cdf(.975)
    for _ in range(repetitions):
        successes = sum(rng.random() < probability for _ in range(n))
        p = successes / n
        half = z * math.sqrt(p * (1 - p) / n)
        intervals = {'wilson': wilson_interval(successes, n), 'wald': (p - half, p + half)}
        for method, (low, high) in intervals.items():
            covered[method] += low <= probability <= high
            widths[method] += high - low
    return {
        'data_type': 'SYNTHETIC Bernoulli simulation; no observed study data',
        'n': n, 'probability': probability, 'repetitions': repetitions, 'seed': seed,
        'nominal_coverage': .95,
        'methods': {method: {
            'covered_repetitions': covered[method],
            'coverage': covered[method] / repetitions,
            'mean_width': widths[method] / repetitions,
            'coverage_mc_se': math.sqrt((covered[method] / repetitions)
                * (1 - covered[method] / repetitions) / repetitions),
        } for method in covered},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, default=20)
    parser.add_argument('--probability', type=float, default=.1)
    parser.add_argument('--repetitions', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=440)
    args = parser.parse_args()
    try:
        result = simulate(args.n, args.probability, args.repetitions, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
