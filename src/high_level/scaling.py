"""Formation scaling-rate schedule beta_s(t) (PROJECT_CONTEXT §6.2).

Stage 1: the fixed piecewise schedule of Eq. (63). Stage 2 will replace this object by a
parameter-generation layer that picks beta_s from the environment; anything with a
`beta_s(t)` method works.
"""


class PiecewiseScaling:
    """Eq. (63): beta_s(t) = b_k for t0_k < t <= t1_k (and t = 0 belongs to the first piece);
    0 outside all pieces."""

    def __init__(self, segments):
        self.segments = [(float(a), float(b), float(c)) for a, b, c in segments]

    def beta_s(self, t):
        for k, (t0, t1, b) in enumerate(self.segments):
            if t0 < t <= t1 or (k == 0 and t == t0):
                return b
        return 0.0
