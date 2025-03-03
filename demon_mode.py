def detect_anomaly(scores, window=20):
    if len(scores) < window:
        return 0.001, -0.001  # Lowered for testnet trades
    mean, std = np.mean(scores[-window:]), np.std(scores[-window:])
    z = (scores[-1] - mean) / std if std > 0 else 0
    return (0.005, -0.005) if abs(z) > 2 else (0.001, -0.001)  # Lowered for testnet
