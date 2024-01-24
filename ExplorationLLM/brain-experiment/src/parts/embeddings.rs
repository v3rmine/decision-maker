use burn::{
    module::Module,
    nn::{Dropout, DropoutConfig, Embedding, EmbeddingConfig},
    tensor::{backend::Backend, Int, Tensor},
};

use crate::model::ModelConfig;

use super::LayerNorm;

#[derive(Module, Debug)]
pub struct Embeddings<B: Backend> {
    /// token embedding
    pub token_embed: Embedding<B>,
    /// position embedding
    pub position_embed: Embedding<B>,
    /// segment(token type) embedding
    pub segment_embed: Embedding<B>,
    pub norm: LayerNorm<B, 3>,
    pub dropout: Dropout,
}

impl<B: Backend> Embeddings<B> {
    pub fn new(config: ModelConfig) -> Self {
        Self {
            token_embed: EmbeddingConfig::new(config.vocab_size, config.hidden_sizes).init(),
            position_embed: EmbeddingConfig::new(config.max_length, config.hidden_sizes).init(),
            segment_embed: EmbeddingConfig::new(config.segments_count, config.hidden_sizes).init(),
            norm: LayerNorm::new(config, None),
            dropout: DropoutConfig::new(config.dropout_hidden).init(),
        }
    }

    pub fn forward(&self, x: Tensor<B, 2, Int>, seg: Tensor<B, 2, Int>) -> Tensor<B, 3> {
        let seq_len = x.dims()[1];
        let pos = Tensor::arange_device(0..seq_len, &x.device());
        let pos = pos.unsqueeze_dim(0).repeat(1, x.dims()[0]);
        let e = self.token_embed.forward(x)
            + self.position_embed.forward(pos)
            + self.segment_embed.forward(seg);

        self.dropout.forward(self.norm.forward(e))
    }
}
