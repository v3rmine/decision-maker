use bert_loader::{load_config_from_json, load_model};
use burn::backend::{wgpu::WgpuDevice, Autodiff, Wgpu};

mod bert_loader;
mod model;

fn main() {
    let device = WgpuDevice::default();
    let config = load_config_from_json("config.json");
    let _model = load_model::<Autodiff<Wgpu>>("model", &device, config);
}
