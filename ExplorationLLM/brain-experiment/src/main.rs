use std::path::Path;

use burn::{
    backend::{
        wgpu::{AutoGraphicsApi, WgpuDevice},
        Autodiff, Wgpu,
    },
    data::dataset::{source::huggingface::MNISTDataset, Dataset},
    optim::AdamConfig,
};
use model::{infer, ModelConfig};
use train::TrainingConfig;

mod activation;
mod data;
mod model;
mod parts;
mod train;
mod utils;

type Backend = Wgpu<AutoGraphicsApi, f32, i32>;
type AutodiffBackend = Autodiff<Backend>;

fn main() {
    let device = WgpuDevice::default();

    if Path::new("model").exists() {
        infer::<Backend>("model", device, MNISTDataset::train().get(1).unwrap())
    } else {
        train::train::<AutodiffBackend>(
            "model",
            TrainingConfig::new(ModelConfig::new(10, 512), AdamConfig::new()),
            device,
        );
    }
}
