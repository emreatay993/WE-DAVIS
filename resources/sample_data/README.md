# Sample Data

This directory contains bundled `.pld` datasets for manual smoke tests and local development.

- `frequency_sample/`: frequency-domain dataset with two `*full.pld` files and one `*max.pld` header file.
- `time_transient_sample/`: time-domain dataset with one `*full.pld` file and one `*max.pld` header file.

The loader matches `.pld` inputs by filename suffix, so the original sample filenames were preserved.

The empty `we_load_visualizer.log` artifact from the sibling prototype was intentionally not moved here because it does not contain a usable log format example.
