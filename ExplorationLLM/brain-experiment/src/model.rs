use burn::{
    config::{self, Config},
    data::{dataloader::batcher::Batcher, dataset::source::huggingface::MNISTItem},
    module::Module,
    nn::{
        conv::{Conv2d, Conv2dConfig},
        loss::CrossEntropyLoss,
        pool::{AdaptiveAvgPool2d, AdaptiveAvgPool2dConfig},
        Dropout, DropoutConfig, Linear, LinearConfig, ReLU,
    },
    record::{CompactRecorder, Recorder},
    tensor::{backend::Backend, Int, Tensor},
    train::ClassificationOutput,
};

use crate::{data::MNISTBatcher, train::TrainingConfig};

#[derive(Module, Debug)]
pub struct Model<B: Backend> {
    conv1: Conv2d<B>,
    conv2: Conv2d<B>,
    pool: AdaptiveAvgPool2d,
    linear1: Linear<B>,
    linear2: Linear<B>,
    dropout: Dropout,
    activation: ReLU,
}

impl<B: Backend> Model<B> {
    pub fn forward(&self, images: Tensor<B, 3>) -> Tensor<B, 2> {
        let [batch_size, height, width] = images.dims();

        let x = images.reshape([batch_size, 1, height, width]);

        let x = self.conv1.forward(x); // [batch_size,  8, _, _]
        let x = self.dropout.forward(x);
        let x = self.conv2.forward(x); // [batch_size, 16, _, _]
        let x = self.dropout.forward(x);
        let x = self.activation.forward(x);

        let x = self.pool.forward(x); // [batch_size, 16, 8, 8]
        let x = x.reshape([batch_size, 16 * 8 * 8]);
        let x = self.linear1.forward(x);
        let x = self.dropout.forward(x);
        let x = self.activation.forward(x);

        self.linear2.forward(x) // [batch_size, num_classes]
    }

    pub fn forward_classification(
        &self,
        images: Tensor<B, 3>,
        targets: Tensor<B, 1, Int>,
    ) -> ClassificationOutput<B> {
        let output = self.forward(images);
        let loss = CrossEntropyLoss::new(None).forward(output.clone(), targets.clone());

        ClassificationOutput::new(loss, output, targets)
    }
}

#[derive(Config, Debug)]
pub struct ModelConfig {
    pub vocab_size: usize,
    /// Maximum Length for Positional Embeddings
    #[config(default = "512")]
    pub max_length: usize,
    /// Number of Sentence Segments
    #[config(default = "2")]
    pub segments_count: usize,
    /// Dimension of Hidden Layer in Transformer Encoder
    #[config(default = "768")]
    pub hidden_sizes: usize,
    /// Number of Hidden Layers
    #[config(default = "12")]
    pub hidden_count: usize,
    /// Numher of Heads in Multi-Headed Attention Layers
    #[config(default = 12)]
    pub heads_count: usize,
    /// Dimension of Intermediate Layers in Positionwise Feedforward Net
    #[config(default = "768 * 4")]
    pub feedforward_sizes: usize,
    /// Probability of Dropout of various Hidden Layers
    #[config(default = "0.1")]
    pub dropout_hidden: f64,
    /// Probability of Dropout of Attention Layers
    #[config(default = "0.1")]
    pub dropout_attention: f64,
}

impl ModelConfig {
    pub fn init<B: Backend>(&self) -> Model<B> {
        Model {
            conv1: Conv2dConfig::new([1, 8], [3, 3]).init(),
            conv2: Conv2dConfig::new([8, 16], [3, 3]).init(),
            pool: AdaptiveAvgPool2dConfig::new([8, 8]).init(),
            activation: ReLU::new(),
            linear1: LinearConfig::new(16 * 8 * 8, self.hidden_sizes).init(),
            linear2: LinearConfig::new(self.hidden_sizes, self.num_classes).init(),
            dropout: DropoutConfig::new(self.dropout).init(),
        }
    }

    pub fn init_with<B: Backend>(&self, record: ModelRecord<B>) -> Model<B> {
        Model {
            conv1: Conv2dConfig::new([1, 8], [3, 3]).init_with(record.conv1),
            conv2: Conv2dConfig::new([8, 16], [3, 3]).init_with(record.conv2),
            pool: AdaptiveAvgPool2dConfig::new([8, 8]).init(),
            activation: ReLU::new(),
            linear1: LinearConfig::new(16 * 8 * 8, self.hidden_sizes).init_with(record.linear1),
            linear2: LinearConfig::new(self.hidden_sizes, self.num_classes)
                .init_with(record.linear2),
            dropout: DropoutConfig::new(self.dropout).init(),
        }
    }
}

pub fn infer<B: Backend>(artifact_dir: &str, device: B::Device, item: MNISTItem) {
    let config = TrainingConfig::load(format!("{artifact_dir}/config.json"))
        .expect("Config should exist for the model");
    let record = CompactRecorder::new()
        .load(format!("{artifact_dir}/model").into())
        .expect("Trained model should exist");

    let model = config.model.init_with::<B>(record).to_device(&device);

    let label = item.label;
    let batcher = MNISTBatcher::new(device);
    let batch = batcher.batch(vec![item]);
    let output = model.forward(batch.images);
    let predicted = output.argmax(1).flatten::<1>(0, 1).into_scalar();

    println!("Predicted {predicted} Expected {label}");
}
