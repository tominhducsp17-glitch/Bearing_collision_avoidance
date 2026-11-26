"""Fixed-step integrators (assumptions.md B-15)."""


def rk4_step(f, t, x, dt):
    """Classical RK4 step for x_dot = f(t, x). Inputs that must be held constant over the
    step (controller outputs, disturbance rand) are captured inside `f` by the caller."""
    k1 = f(t, x)
    k2 = f(t + dt / 2, x + dt / 2 * k1)
    k3 = f(t + dt / 2, x + dt / 2 * k2)
    k4 = f(t + dt, x + dt * k3)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
