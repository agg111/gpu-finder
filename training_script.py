#!/usr/bin/env python3
"""
Simple PyTorch training script for GPU Finder.
This script is embedded in EC2 user data and runs automatically.
"""
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
import json
from datetime import datetime
import sys

# Get model and workload from command line arguments
model_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
workload = sys.argv[2] if len(sys.argv) > 2 else "unknown"

print("=" * 60)
print("🚀 GPU Finder Training Job")
print(f"Model: {model_name}")
print(f"Workload: {workload}")
print(f"Started: {datetime.now().isoformat()}")
print("=" * 60)

# Tiny dataset (100 samples, 2 features)
print("\n📦 Creating synthetic dataset...")
X = torch.randn(100, 2)
y = (X[:, 0] * 2 + X[:, 1] * -3 + 0.5).unsqueeze(1)
print(f"   Dataset shape: X={X.shape}, y={y.shape}")

# Model: single-layer linear regression
print("\n🧠 Initializing model...")
model = nn.Linear(2, 1)
loss_fn = nn.MSELoss()
opt = torch.optim.SGD(model.parameters(), lr=0.1)
print(f"   Model: {model}")

# Training loop
print("\n🏋️  Training...")
for epoch in range(50):
    opt.zero_grad()
    pred = model(X)
    loss = loss_fn(pred, y)
    loss.backward()
    opt.step()
    if epoch % 10 == 0:
        print(f"   Epoch {epoch:02d}: loss = {loss.item():.4f}")

print("\n✅ Training completed!")

# Print final weights
weights = list(model.parameters())
print(f"   Final weights: w={weights[0].data.tolist()}, b={weights[1].data.item():.4f}")

# Save results
results = {
    "status": "success",
    "model": model_name,
    "workload": workload,
    "final_loss": loss.item(),
    "weights": {
        "w": weights[0].data.tolist(),
        "b": weights[1].data.item()
    },
    "completed_at": datetime.now().isoformat()
}

with open("/home/ec2-user/training_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n💾 Results saved to training_results.json")
print("=" * 60)
