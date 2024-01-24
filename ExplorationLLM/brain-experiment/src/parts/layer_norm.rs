use burn::{
    module::Module,
    tensor::{backend::Backend, Tensor},
};

use crate::model::ModelConfig;

#[derive(Module, Debug)]
pub struct LayerNorm<B: Backend, const D: usize> {
    pub gamma: Tensor<B, D>,
    pub beta: Tensor<B, D>,
    pub variance_epsilon: f64,
}

impl<B: Backend, const D: usize> LayerNorm<B, D> {
    pub fn new(config: ModelConfig, variance_epsilon: Option<f64>) -> Self {
        Self {
            gamma: Tensor::ones(vec![config.hidden_sizes]),
            beta: Tensor::zeros(vec![config.hidden_sizes]),
            variance_epsilon: variance_epsilon.unwrap_or(1e-12),
        }
    }

    pub fn forward(&self, x: Tensor<B, D>) -> Tensor<B, D> {
        let last_dim = *x.dims().last().unwrap();
        let u = x.mean_dim(last_dim);
        let s = (x - u).powf(2.0).mean_dim(last_dim);
        let x = (x - u) / (s + self.variance_epsilon).sqrt();
        return self.gamma.mul(x).add(self.beta);
    }
}
