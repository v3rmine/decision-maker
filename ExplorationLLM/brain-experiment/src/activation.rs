use burn::tensor::{backend::Backend, Tensor};

/// Implementation of the gelu activation function by Hugging Face
/// Source: <https://github.com/dhlee347/pytorchic-bert/blob/master/models.py#L36>
/// Source: <https://github.com/huggingface/transformers/blob/main/src/transformers/activations.py>
pub fn gelu<const D: usize, B: Backend>(x: Tensor<B, D>) -> Tensor<B, D> {
    x * 0.5 * (x / f64::sqrt(2.0)).erf().add_scalar(1.0)
}
