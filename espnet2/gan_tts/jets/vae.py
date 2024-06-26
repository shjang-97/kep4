import torch
import torch.nn as nn
import torch.nn.functional as F

class VectorQuantizer(nn.Module):
    def __init__(self, num_embeddings, embedding_dim, commitment_cost):
        super(VectorQuantizer, self).__init__()
        self.embedding_dim = embedding_dim
        self.num_embeddings = num_embeddings
        self.commitment_cost = commitment_cost

        self.embeddings = nn.Embedding(num_embeddings, embedding_dim)
        self.embeddings.weight.data.uniform_(-1/self.num_embeddings, 1/self.num_embeddings)

    def forward(self, x):
        flat_x = x.view(-1, self.embedding_dim)

        distances = (torch.sum(flat_x**2, dim=1, keepdim=True)
                     + torch.sum(self.embeddings.weight**2, dim=1)
                     - 2 * torch.matmul(flat_x, self.embeddings.weight.t()))

        encoding_indices = torch.argmin(distances, dim=1).unsqueeze(1)
        encodings = torch.zeros(encoding_indices.size(0), self.num_embeddings, device=x.device)
        encodings.scatter_(1, encoding_indices, 1)

        quantized = torch.matmul(encodings, self.embeddings.weight).view(x.shape)

        e_latent_loss = F.mse_loss(quantized.detach(), x)
        q_latent_loss = F.mse_loss(quantized, x.detach())
        loss = q_latent_loss + self.commitment_cost * e_latent_loss

        quantized = x + (quantized - x).detach()

        avg_probs = torch.mean(encodings, dim=0)
        perplexity = torch.exp(-torch.sum(avg_probs * torch.log(avg_probs + 1e-10)))

        return loss, quantized, perplexity

class VQVAE(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_embeddings, embedding_dim, commitment_cost):
        super(VQVAE, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim)
        )
        self.vq_layer = VectorQuantizer(num_embeddings, embedding_dim, commitment_cost)
        self.decoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )

    def forward(self, x):
        batch_size, time_step, mel_bin = x.shape
        x = x.view(batch_size * time_step, mel_bin)  # Flatten to (batch_size * time_step, mel_bin)
        z_e = self.encoder(x)  # (batch_size * time_step, embedding_dim)
        vq_loss, quantized, perplexity = self.vq_layer(z_e)
        
        # 각 time step의 임베딩을 평균하여 시간적 특성을 유지하면서 embedding_dim으로 축소
        quantized = quantized.view(batch_size, time_step, -1)  # Reshape back to (batch_size, time_step, embedding_dim)
        quantized = torch.mean(quantized, dim=1)  # 각 time step의 임베딩을 평균
        quantized = quantized.unsqueeze(1)  # (batch_size, 1, embedding_dim)
        
        x_recon = self.decoder(quantized.view(batch_size, -1))  # Decode
        return vq_loss, quantized, perplexity

    
# /workspace/TTS/espnet/espnet2/gan_tts/jets/vae.py

# # 예제 입력
# batch_size = 16
# time_step = 78  # This can vary
# mel_bin = 80
# input_dim = mel_bin
# hidden_dim = 512
# num_embeddings = 512
# embedding_dim = 256
# commitment_cost = 0.25

# model = VQVAE(input_dim, hidden_dim, num_embeddings, embedding_dim, commitment_cost)
# x = torch.randn(batch_size, time_step, mel_bin)
# vq_loss, quantized, perplexity = model(x)

# print("Quantized output size:", quantized.size())  # Expected: (batch_size, time_step, embedding_dim)
