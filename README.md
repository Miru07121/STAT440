# Statistics experiments

A small, standalone statistics example in this repository: compare the empirical
coverage of Wilson and Wald intervals for a binomial proportion. It uses only
synthetic Bernoulli samples and Python's standard library. This is an independent
learning exercise, not a claim about course assignments or completed coursework.

## Run

Requires Python 3.11 or later. No dependencies or external data downloads:

```bash
python binomial_coverage.py
python binomial_coverage.py --n 50 --probability 0.1 --repetitions 5000 --seed 440
python -m unittest discover -s tests -v
```

The command prints JSON; redirect it to a file if desired. It writes no files by
default. The seed uses a local random generator, leaving the caller's global
random state unchanged. Repeat a command in the same Python environment to
reproduce the same simulation.

## Experiment and interpretation

Each repetition draws `n` independent Bernoulli outcomes at the supplied true
probability, constructs two nominal 95% intervals, and checks whether each
contains that probability. Coverage is the fraction of repetitions containing
the true value. It is not the probability that a fixed, realized interval contains
a random parameter.

| Output | Meaning |
|---|---|
| `covered_repetitions` | Number of intervals containing the true probability |
| `coverage` | Covered repetitions divided by total repetitions |
| `mean_width` | Mean upper endpoint minus lower endpoint |
| `coverage_mc_se` | Estimated Monte Carlo standard error of the coverage fraction |

The Wald interval is `p_hat ± z * sqrt(p_hat * (1 - p_hat) / n)` and is left
unclipped, so endpoints may fall outside [0, 1]. The Wilson interval uses the
score-interval formula and stays within [0, 1]. Both use the standard-normal
97.5th percentile. Test cases check reference values, boundary counts, symmetry,
repeatability, invalid parameters, and command-line behavior.

Try small and large sample sizes and probabilities near 0, 0.5, and 1. Nominal
95% coverage does not guarantee exactly 95% empirical coverage. The binomial
sampling distribution is discrete, and a finite simulation adds Monte Carlo
noise. Width and coverage should be considered together. At probabilities 0 and
1 the Wald interval collapses to a point; high coverage there is not evidence of
good behavior near the boundaries. Estimated Monte Carlo error is zero when all
or no simulated intervals cover, which does not establish exact general coverage.

Runtime scales with `n × repetitions`; start with the defaults before increasing
both. The simulation does not model clustering, dependence, selection bias, or
real survey design.
