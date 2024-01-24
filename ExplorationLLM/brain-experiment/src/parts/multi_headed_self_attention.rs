use burn::{
    module::Module,
    nn::{Dropout, DropoutConfig, Linear, LinearConfig},
    tensor::{backend::Backend, Tensor},
};

use crate::model::ModelConfig;

#[derive(Module, Debug)]
pub struct MultiHeadedSelfAttention<B: Backend, const D: usize> {
    pub proj_q: Linear<B>,
    pub proj_k: Linear<B>,
    pub proj_v: Linear<B>,
    pub dropout: Dropout,
    pub scores: Option<Tensor<B, D>>,
    pub heads_count: usize,
}

impl<B: Backend, const D: usize> MultiHeadedSelfAttention<B, D> {
    pub fn new(config: ModelConfig) -> Self {
        Self {
            proj_q: LinearConfig::new(config.hidden_sizes, config.hidden_sizes).init(),
            proj_k: LinearConfig::new(config.hidden_sizes, config.hidden_sizes).init(),
            proj_v: LinearConfig::new(config.hidden_sizes, config.hidden_sizes).init(),
            dropout: DropoutConfig::new(config.dropout_attention).init(),
            scores: None,
            heads_count: config.heads_count,
        }
    }

    pub fn forward(&self, x: Tensor<B, D>, mask: Tensor<B, D>) -> Tensor<B, D> {
        let (q, k, v) = (
            self.proj_q.forward(x),
            self.proj_k.forward(x),
            self.proj_v.forward(x),
        );
    }
}
