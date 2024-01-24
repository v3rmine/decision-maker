macro_rules! exports {
    ($($mod:ident),*) => {
        $(
            mod $mod;
            pub use $mod::*;
        )*
    };
}

exports!(
    block,
    embeddings,
    layer_norm,
    multi_headed_self_attention,
    position_wise_forward,
    transformer
);
