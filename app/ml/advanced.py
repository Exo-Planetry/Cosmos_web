"""Research-grade architecture components. These classes are not claimed as trained production models."""
try:
 import torch
 import torch.nn as nn
except Exception:
 torch=None; nn=object

if torch:
 class LightCurveCNNTransformer(nn.Module):
  def __init__(self,channels=1,embed=64,heads=4,layers=2):
   super().__init__(); self.proj=nn.Conv1d(channels,embed,7,padding=3); self.encoder=nn.TransformerEncoder(nn.TransformerEncoderLayer(embed,heads,batch_first=True),layers); self.head=nn.Sequential(nn.LayerNorm(embed),nn.Linear(embed,1))
  def forward(self,x): return self.head(self.encoder(self.proj(x).transpose(1,2)).mean(1))
 class SpectralAutoencoder(nn.Module):
  def __init__(self,n_features=256,latent=32):
   super().__init__(); self.encoder=nn.Sequential(nn.Linear(n_features,128),nn.GELU(),nn.Linear(128,latent)); self.decoder=nn.Sequential(nn.Linear(latent,128),nn.GELU(),nn.Linear(128,n_features))
  def forward(self,x): return self.decoder(self.encoder(x))
 class MultimodalModel(nn.Module):
  def __init__(self,dim=32):
   super().__init__(); self.head=nn.Sequential(nn.Linear(dim*3,64),nn.GELU(),nn.Linear(64,1))
  def forward(self,transit,spectrum,tabular): return self.head(torch.cat([transit,spectrum,tabular],dim=-1))
else:
 class LightCurveCNNTransformer: pass
 class SpectralAutoencoder: pass
 class MultimodalModel: pass

class PhysicsInformedObjective:
 def __init__(self,physics_weight=0.2): self.physics_weight=physics_weight
 def loss(self,data_loss,physics_residual): return float(data_loss)+self.physics_weight*float(physics_residual)
