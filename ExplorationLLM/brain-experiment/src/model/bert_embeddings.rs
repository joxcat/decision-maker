use burn::{
    config::Config,
    module::Module,
    nn::{Dropout, DropoutConfig, Embedding, EmbeddingConfig, LayerNorm, LayerNormConfig},
    tensor::{backend::Backend, Data, Float, Int, Shape, Tensor},
};

#[derive(Debug, Clone)]
pub struct BertEmbeddingsInferenceBatch<B: Backend> {
    pub tokens: Tensor<B, 2, Int>, // Tokenized text
    pub mask_attn: Option<Tensor<B, 2>>,
}

#[derive(Config)]
pub struct BertEmbeddingsConfig {
    pub vocab_size: usize,
    pub max_position_embeddings: usize,
    pub type_vocab_size: usize,
    pub hidden_size: usize,
    pub hidden_dropout_prob: f64,
    pub layer_norm_eps: f64,
}

#[derive(Module, Debug)]
pub struct BertEmbeddings<B: Backend> {
    word_embeddings: Embedding<B>,
    position_embeddings: Embedding<B>,
    token_type_embeddings: Embedding<B>,
    layer_norm: LayerNorm<B>,
    dropout: Dropout,
    max_position_embeddings: usize,
}

impl BertEmbeddingsConfig {
    /// Initializes BertEmbeddings with default weights
    pub fn init<B: Backend>(&self) -> BertEmbeddings<B> {
        let word_embeddings = EmbeddingConfig::new(self.vocab_size, self.hidden_size).init();
        let position_embeddings =
            EmbeddingConfig::new(self.max_position_embeddings, self.hidden_size).init();
        let token_type_embeddings =
            EmbeddingConfig::new(self.type_vocab_size, self.hidden_size).init();
        let layer_norm_config = LayerNormConfig::new(self.hidden_size);
        let layer_norm_config = layer_norm_config.with_epsilon(self.layer_norm_eps);
        let layer_norm = layer_norm_config.init();
        let dropout = DropoutConfig::new(self.hidden_dropout_prob).init();

        BertEmbeddings {
            word_embeddings,
            position_embeddings,
            token_type_embeddings,
            layer_norm,
            dropout,
            max_position_embeddings: self.max_position_embeddings,
        }
    }

    /// Initializes BertEmbeddings with provided weights
    pub fn init_with<B: Backend>(&self, record: BertEmbeddingsRecord<B>) -> BertEmbeddings<B> {
        let word_embeddings = EmbeddingConfig::new(self.vocab_size, self.hidden_size)
            .init_with(record.word_embeddings);
        let position_embeddings =
            EmbeddingConfig::new(self.max_position_embeddings, self.hidden_size)
                .init_with(record.position_embeddings);
        let token_type_embeddings = EmbeddingConfig::new(self.type_vocab_size, self.hidden_size)
            .init_with(record.token_type_embeddings);
        let layer_norm_config = LayerNormConfig::new(self.hidden_size);
        let layer_norm_config = layer_norm_config.with_epsilon(self.layer_norm_eps);
        let layer_norm = layer_norm_config.init_with(record.layer_norm);

        let dropout = DropoutConfig::new(self.hidden_dropout_prob).init();

        BertEmbeddings {
            word_embeddings,
            position_embeddings,
            token_type_embeddings,
            layer_norm,
            dropout,
            max_position_embeddings: self.max_position_embeddings,
        }
    }
}

impl<B: Backend> BertEmbeddings<B> {
    pub fn forward(&self, item: BertEmbeddingsInferenceBatch<B>) -> Tensor<B, 3, Float> {
        // Extract tokens from the batch
        let input_shape = &item.tokens.shape();
        let input_ids = item.tokens;

        // Embed tokens
        let inputs_embeds = self.word_embeddings.forward(input_ids);
        let mut embeddings = inputs_embeds;

        let device = embeddings.device();

        let token_type_ids =
            Tensor::<B, 2, Int>::zeros(input_shape.clone()).to_device(&device.clone()); // Assuming you have a zeros method
        let token_type_embeddings = self.token_type_embeddings.forward(token_type_ids);

        embeddings = embeddings + token_type_embeddings;

        // Position embeddings
        // Assuming position_ids is a range from 0 to seq_length
        let seq_length = input_shape.dims[1];
        let position_values: Vec<i32> = (0..self.max_position_embeddings)
            .map(|x| x as i32) // Convert each usize to Int
            .collect::<Vec<_>>()[0..seq_length]
            .to_vec();

        let shape = Shape::new([1, seq_length]);
        let data = Data::new(position_values, shape);
        let mut position_ids_tensor = Tensor::<B, 2, Int>::from_ints(data);
        position_ids_tensor = position_ids_tensor.to_device(&device.clone());

        let position_embeddings = self.position_embeddings.forward(position_ids_tensor);
        embeddings = embeddings + position_embeddings;

        // Layer normalization and dropout
        let embeddings = self.layer_norm.forward(embeddings);
        let embeddings = self.dropout.forward(embeddings);

        embeddings
    }
}
