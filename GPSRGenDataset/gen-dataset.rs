#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! duct = "0.13"
//! ```

use std::{
    env::var,
    error::Error,
    fs::{self, read_dir},
};

extern crate duct;
use duct::cmd;

fn main() -> Result<(), Box<dyn Error>> {
    let generation_count = var("GEN_COUNT").unwrap_or("1000".into());
    let gpsrcmdgen_image =
        var("GPSR_CMDGEN_IMAGE").unwrap_or("ghcr.io/joxcat/gpsrcmdgen-gpsr:v2023.2".into());
    let outfile = var("OUT_FILE").unwrap_or("raw-dataset.csv".into());

    // Create the mount folder with the current user perms for the docker mount
    cmd!("mkdir", "-p", "raw_data").run()?;
    cmd!(
        "sh",
        "-c",
        format!(
            r#"docker run --rm -it \
                -u $(id -u):$(id -g) \
                -v $PWD/raw_data:/data \
                {gpsrcmdgen_image} \
                --bulk {generation_count}"#
        )
    )
    .run()?;

    let mut dataset = "id,prompt\n".to_string();
    let mut count = 0;
    for entry in read_dir("raw_data/GPSR Examples").unwrap().flatten() {
        let path = entry.path();
        let basename = path
            .with_extension("")
            .file_name()
            .unwrap()
            .to_str()
            .unwrap()
            .to_string();

        if path.is_file() && basename.contains(" - ") {
            let prompt = basename.split(" - ").collect::<Vec<_>>()[1];
            dataset.push_str(&format!("{count},\"{prompt}\"\n"));
            count += 1;
        }
    }
    cmd!("rm", "-rf", "raw_data").run()?;
    fs::write(outfile, dataset)?;

    Ok(())
}
