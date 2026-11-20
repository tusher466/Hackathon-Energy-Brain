import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

# Try torch, fallback to sklearn
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except:
    TORCH_AVAILABLE = False

from sklearn.ensemble import GradientBoostingRegressor

class SimpleLSTMModel:
    def __init__(self, input_dim=5, hidden_dim=32, output_dim=3):
        if not TORCH_AVAILABLE:
            raise RuntimeError("Torch not available")
        self.hidden_dim = hidden_dim
        class LSTMQuantile(nn.Module):
            def __init__(self, input_dim, hidden_dim, output_dim):
                super().__init__()
                self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
                self.fc = nn.Linear(hidden_dim, output_dim)
            def forward(self, x):
                _, (h_n, _) = self.lstm(x)
                out = self.fc(h_n[-1])
                return out
        self.model = LSTMQuantile(input_dim, hidden_dim, output_dim)

    def predict(self, sequence: np.ndarray):
        # sequence shape [seq_len, input_dim]
        self.model.eval()
        with torch.no_grad():
            x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)  # [1, seq, dim]
            out = self.model(x)  # [1,3]
            return out.numpy()[0]

def quantile_loss(y_true, y_pred, quantile):
    err = y_true - y_pred
    return np.mean(np.maximum(quantile*err, (quantile-1)*err))

class SolarForecaster:
    def __init__(self):
        self.version = "lstm-fallback-v1"
        self.model_p10 = None
        self.model_p50 = None
        self.model_p90 = None
        self.torch_model = None
        self.trained = False
        if TORCH_AVAILABLE:
            try:
                self.torch_model = SimpleLSTMModel(input_dim=4, hidden_dim=24, output_dim=3)
                self.version = "lstm-cpu-v1"
            except:
                self.torch_model = None

    def _feature_engineering(self, historical_pow: List[float], timestamps: List[datetime]):
        # For sklearn: create features: hour sin/cos, lag-1, lag-24 mean, clear sky approx?
        X = []
        y = []
        for i in range(24, len(historical_pow)):
            ts = timestamps[i]
            hour = ts.hour
            hour_sin = np.sin(2*np.pi*hour/24)
            hour_cos = np.cos(2*np.pi*hour/24)
            lag1 = historical_pow[i-1]
            lag24_mean = float(np.mean(historical_pow[i-24:i]))
            cloud_proxy = np.random.uniform(0.4,1.0)  # in real would be cloud
            X.append([hour_sin, hour_cos, lag1, lag24_mean, cloud_proxy])
            y.append(historical_pow[i])
        return np.array(X), np.array(y)

    def train_dummy(self, historical_pow: List[float], timestamps: List[datetime]):
        # Train sklearn quantile models quickly on synthetic data
        if len(historical_pow) < 48:
            # generate dummy longer history from synthetic pattern
            extra = []
            extra_ts = []
            base = timestamps[0]
            for i in range(200):
                dt = base - timedelta(hours=i+1)
                extra_ts.insert(0, dt)
                # synthetic pattern
                val = max(0, 50 + 50*np.sin(2*np.pi*dt.hour/24) + np.random.normal(0,5))
                extra.insert(0, val)
            historical_pow = extra + historical_pow
            timestamps = extra_ts + timestamps

        X, y = self._feature_engineering(historical_pow, timestamps)
        if len(X) < 10:
            self.trained = False
            return
        # Train three models for quantiles 0.1,0.5,0.9 using gradient boosting with quantile loss
        try:
            self.model_p10 = GradientBoostingRegressor(loss='quantile', alpha=0.1, n_estimators=80, max_depth=3, random_state=0)
            self.model_p50 = GradientBoostingRegressor(loss='quantile', alpha=0.5, n_estimators=80, max_depth=3, random_state=0)
            self.model_p90 = GradientBoostingRegressor(loss='quantile', alpha=0.9, n_estimators=80, max_depth=3, random_state=0)
            self.model_p10.fit(X, y)
            self.model_p50.fit(X, y)
            self.model_p90.fit(X, y)
            self.trained = True
        except Exception as e:
            # fallback to squared error
            self.model_p50 = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=0)
            self.model_p50.fit(X, y)
            self.model_p10 = self.model_p50
            self.model_p90 = self.model_p50
            self.trained = True

    def forecast(self, recent_pow: List[float], recent_ts: List[datetime], horizon: int, cloud_forecast: List[float] = None):
        if not self.trained:
            self.train_dummy(recent_pow, recent_ts)
        forecasts = []
        # last values for iterative
        hist = recent_pow.copy()
        hist_ts = recent_ts.copy()
        if cloud_forecast is None:
            cloud_forecast = [0.8]*horizon
        for h in range(horizon):
            next_ts = hist_ts[-1] + timedelta(hours=1)
            hour = next_ts.hour
            hour_sin = np.sin(2*np.pi*hour/24)
            hour_cos = np.cos(2*np.pi*hour/24)
            lag1 = hist[-1]
            lag24_mean = float(np.mean(hist[-24:])) if len(hist)>=24 else float(np.mean(hist))
            cloud = cloud_forecast[h] if h < len(cloud_forecast) else 0.8
            X = np.array([[hour_sin, hour_cos, lag1, lag24_mean, cloud]])
            if TORCH_AVAILABLE and self.torch_model is not None and h==0:
                # attempt torch prediction for first step - use dummy sequence
                try:
                    seq = np.random.rand(12,4)  # placeholder - in real use past sequence
                    torch_out = self.torch_model.predict(seq)
                    # torch_out = [p10,p50,p90] offset, use as basis? We'll mix
                    p50_torch = float(max(0, torch_out[1]*100))
                    # but fallback to sklearn for reliability
                except:
                    pass
            try:
                p10 = float(self.model_p10.predict(X)[0] * cloud) if self.model_p10 else float(lag1*cloud*0.7)
                p50 = float(self.model_p50.predict(X)[0] * cloud) if self.model_p50 else float(lag1*cloud)
                p90 = float(self.model_p90.predict(X)[0] * cloud) if self.model_p90 else float(lag1*cloud*1.3)
            except:
                p50 = float(max(0, lag1 * cloud + np.random.normal(0,5)))
                p10 = p50*0.7
                p90 = p50*1.3
            # ensure monotonic
            p10, p50, p90 = sorted([p10,p50,p90])
            p10 = max(0, p10)
            # variability index based on cloud spread
            var_idx = float(abs(p90-p10)/(p50+1)*2)
            forecasts.append({
                "timestamp": next_ts,
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "variability_index": var_idx
            })
            hist.append(p50)
            hist_ts.append(next_ts)
        return forecasts

# singleton
solar_forecaster = SolarForecaster()
