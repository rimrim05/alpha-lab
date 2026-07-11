"""Covariance estimators for the Estimator Lab. Each: cov(R) -> Sigma,
R = (n_days x p) daily return window (not necessarily demeaned).
See PLAN.md for pre-registration; JSE per research/hunt2026/specs/pca_minvar_jse
and factor_lab bias_correction_demo.py (psi-hat form), generalized to k>1."""
import numpy as np
from sklearn.covariance import ledoit_wolf

TAU = 0.01  # floor on psi^2 (weak-factor guard, factor_lab convention)
IDIO_FLOOR = 1e-8


def sample_cov(R):
    return np.cov(R, rowvar=False, ddof=1)


def _pca_parts(R, k, jse):
    """Shared PCA/JSE machinery: returns (V, lam, D) with Sigma = V lam V' + diag(D)."""
    Y = (R - R.mean(axis=0)).T  # (p x n), demeaned per name
    p, n = Y.shape
    U, sv, _ = np.linalg.svd(Y, full_matrices=False)
    H, sig = U[:, :k], sv[:k]
    lam = sig**2 / n
    resid = Y - H @ (H.T @ Y)
    D = np.maximum((resid**2).sum(axis=1) / n, IDIO_FLOOR)
    if not jse:
        return H, lam, D
    # JSE: rotate each h_i toward equal-weight q with psi_i^2 = max(tau, 1 - p*delta2/sig_i^2)
    delta2 = (resid**2).sum() / ((p - k) * n)
    q = np.full(p, 1.0 / np.sqrt(p))
    V = np.empty_like(H)
    for i in range(k):
        h = H[:, i]
        if h.sum() < 0:  # SVD sign is arbitrary
            h = -h
        psi2 = max(TAU, 1.0 - p * delta2 / sig[i] ** 2)
        hq = float(h @ q)
        c = np.clip(hq / np.sqrt(psi2), -1.0, 1.0)
        r = h - hq * q
        rn = np.linalg.norm(r)
        V[:, i] = q if rn < 1e-12 else c * q + np.sqrt(max(0.0, 1.0 - c**2)) * (r / rn)
    return V, lam, D


def pca_cov(R, k, jse=False):
    V, lam, D = _pca_parts(R, k, jse)
    return (V * lam) @ V.T + np.diag(D)


def lw_cov(R):
    # sklearn is installed (1.9.0); shrinks to scaled identity, which is (d)
    return ledoit_wolf(R - R.mean(axis=0), assume_centered=True)[0]


def mp_cov(R):
    """Marchenko-Pastur clipping: eigenvalues below lam+ replaced by their mean."""
    S = sample_cov(R)
    n, p = R.shape
    w, Q = np.linalg.eigh(S)
    lam_plus = w.mean() * (1.0 + np.sqrt(p / n)) ** 2
    noise = w < lam_plus
    if noise.any():
        w = w.copy()
        w[noise] = w[noise].mean()  # trace-preserving
    return (Q * np.maximum(w, IDIO_FLOOR)) @ Q.T


ESTIMATORS = {
    "sample": sample_cov,
    "pca1": lambda R: pca_cov(R, 1),
    "pca3": lambda R: pca_cov(R, 3),
    "pca5": lambda R: pca_cov(R, 5),
    "jse1": lambda R: pca_cov(R, 1, jse=True),
    "jse3": lambda R: pca_cov(R, 3, jse=True),
    "jse5": lambda R: pca_cov(R, 5, jse=True),
    "lw": lw_cov,
    "mp": mp_cov,
}


if __name__ == "__main__":
    # self-check: shapes, symmetry, PSD (up to pinv tolerance), JSE narrows angle to q
    rng = np.random.default_rng(0)
    n, p, k = 252, 120, 3
    B = rng.normal(1.0, 0.5, (p, k))
    F = rng.normal(0, 0.01, (n, k)) * [3, 2, 1]
    R = F @ B.T + rng.normal(0, 0.01, (n, p))
    for name, fn in ESTIMATORS.items():
        S = fn(R)
        assert S.shape == (p, p), name
        assert np.allclose(S, S.T, atol=1e-10), name
        wmin = np.linalg.eigvalsh(S).min()
        assert wmin > -1e-10, (name, wmin)
    q = np.full(p, 1.0 / np.sqrt(p))
    H, _, _ = _pca_parts(R, k, jse=False)
    V, _, _ = _pca_parts(R, k, jse=True)
    for i in range(k):
        h = H[:, i] if H[:, i].sum() >= 0 else -H[:, i]
        assert abs(V[:, i] @ q) >= abs(h @ q) - 1e-12, i  # rotated toward q
        assert np.allclose(np.linalg.norm(V[:, i]), 1.0)
    # MP keeps trace
    assert np.isclose(np.trace(mp_cov(R)), np.trace(sample_cov(R)), rtol=1e-6)
    print("self-check OK")
