import torch
import torch.nn as nn
import math


class Transformer(nn.Module):
    def __init__(self, num_encoder_layers, num_decoder_layers, d_model, num_heads, dim_feedforward, dropout):
        super(Transformer, self).__init__()
        self.encoder = TransformerEncoder(num_encoder_layers, d_model, num_heads, dim_feedforward, dropout)
        self.decoder = TransformerDecoder(num_decoder_layers, d_model, num_heads, dim_feedforward, dropout)

    def forward(self, src, tgt):
        memory = self.encoder(src)
        output = self.decoder(tgt, memory)
        return output


class TransformerEncoder(nn.Module):
    def __init__(self, num_layers, d_model, num_heads, dim_feedforward, dropout):
        super(TransformerEncoder, self).__init__()
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, dim_feedforward, dropout)
            for _ in range(num_layers)
        ])

    def forward(self, src):
        for layer in self.encoder_layers:
            src = layer(src)
        return src


class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, dim_feedforward, dropout):
        super(TransformerEncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Linear(dim_feedforward, d_model)
        )
        self.dropout = nn.Dropout(dropout)
        self.layer_norm1 = nn.LayerNorm(d_model)
        self.layer_norm2 = nn.LayerNorm(d_model)

    def forward(self, src):
        src2 = self.self_attn(src, src, src)
        src = src + self.dropout(src2)
        src = self.layer_norm1(src)
        src2 = self.feed_forward(src)
        src = src + self.dropout(src2)
        src = self.layer_norm2(src)
        return src


class TransformerDecoder(nn.Module):
    def __init__(self, num_layers, d_model, num_heads, dim_feedforward, dropout):
        super(TransformerDecoder, self).__init__()
        self.decoder_layers = nn.ModuleList([
            TransformerDecoderLayer(d_model, num_heads, dim_feedforward, dropout)
            for _ in range(num_layers)
        ])

    def forward(self, tgt, memory):
        for layer in self.decoder_layers:
            tgt = layer(tgt, memory)
        return tgt


class TransformerDecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, dim_feedforward, dropout):
        super(TransformerDecoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.multi_head_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Linear(dim_feedforward, d_model)
        )
        self.dropout = nn.Dropout(dropout)
        self.layer_norm1 = nn.LayerNorm(d_model)
        self.layer_norm2 = nn.LayerNorm(d_model)
        self.layer_norm3 = nn.LayerNorm(d_model)

    def forward(self, tgt, memory):
        tgt2 = self.self_attn(tgt, tgt, tgt)
        tgt = tgt + self.dropout(tgt2)
        tgt = self.layer_norm1(tgt)
        tgt2 = self.multi_head_attn(tgt, memory, memory)
        tgt = tgt + self.dropout(tgt2)
        tgt = self.layer_norm2(tgt)
        tgt2 = self.feed_forward(tgt)
        tgt = tgt + self.dropout(tgt2)
        tgt = self.layer_norm3(tgt)
        return tgt


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads, dropout):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        self.dropout = dropout

        self.query_linear = nn.Linear(d_model, d_model)
        self.key_linear = nn.Linear(d_model, d_model)
        self.value_linear = nn.Linear(d_model, d_model)

        self.dropout_layer = nn.Dropout(dropout)
        self.output_linear = nn.Linear(d_model, d_model)

    def forward(self, query, key, value):
        batch_size = query.size(0)

        query = self.query_linear(query).view(
            batch_size, -1, self.num_heads, self.d_model // self.num_heads
        ).transpose(1, 2)

        key = self.key_linear(key).view(
            batch_size, -1, self.num_heads, self.d_model // self.num_heads
        ).transpose(1, 2)

        value = self.value_linear(value).view(
            batch_size, -1, self.num_heads, self.d_model // self.num_heads
        ).transpose(1, 2)

        attention_scores = torch.matmul(query, key.transpose(-1, -2)) / math.sqrt(self.d_model // self.num_heads)
        attention_weights = nn.functional.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout_layer(attention_weights)

        output = torch.matmul(attention_weights, value).transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.output_linear(output)

        return output


def main():
    # Set up device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Model parameters
    d_model = 512
    num_heads = 8
    dropout = 0.1
    num_encoder_layers = 6
    num_decoder_layers = 6
    dim_feedforward = 2048
    
    # Create sample data
    batch_size = 2
    seq_length = 10
    
    # Create random input tensors
    src = torch.randn(batch_size, seq_length, d_model).to(device)
    tgt = torch.randn(batch_size, seq_length, d_model).to(device)
    
    print(f"Input shapes - src: {src.shape}, tgt: {tgt.shape}")
    
    # Test MultiHeadAttention
    print("\n--- Testing MultiHeadAttention ---")
    attention = MultiHeadAttention(d_model, num_heads, dropout).to(device)
    attention_output = attention(src, src, src)
    print(f"Attention output shape: {attention_output.shape}")
    
    # Test TransformerDecoderLayer
    print("\n--- Testing TransformerDecoderLayer ---")
    decoder_layer = TransformerDecoderLayer(d_model, num_heads, dim_feedforward, dropout).to(device)
    decoder_output = decoder_layer(tgt, src)
    print(f"Decoder output shape: {decoder_output.shape}")
    
    # Test TransformerDecoder
    print("\n--- Testing TransformerDecoder ---")
    decoder = TransformerDecoder(num_decoder_layers, d_model, num_heads, dim_feedforward, dropout).to(device)
    decoder_output = decoder(tgt, src)
    print(f"Full decoder output shape: {decoder_output.shape}")
    
    # Test Transformer
    print("\n--- Testing Full Transformer ---")
    transformer = Transformer(num_encoder_layers, num_decoder_layers, d_model, num_heads, dim_feedforward, dropout).to(device)
    
    transformer_output = transformer(src, tgt)
    print(f"Transformer output shape: {transformer_output.shape}")
    
    print("\n--- All tests completed successfully! ---")


if __name__ == "__main__":
    main()
