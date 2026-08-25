# SpikeTrack official-resource attribution notes

Scope: official-release attribution and raw-result comparison only. Access date: 2026-08-25.

## Author-controlled chain

1. The pinned official GitHub README at commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` links Google Drive folder `1G9DhjfhmiRz_9JxxlbHbOnuYZBAmhLOG` as both Models and Raw Results, and links `facaiwawa/SpikeTrack` on Hugging Face as Models.
2. The public Drive root is named `spiketrack`. Its direct children are `model_weight` (`1FvPk3EiIBdp-AUIPVkF9WuwjLdrX67yx`), `raw_results` (`1HNd8EdpHLf3Ly1leuDVQDOBsDg3uaSsq`), `spike_firing_rate_excel` (`1wtcbq6Ny1SgdUw4w1x3cAEbugt8z_4Bi`), and `training_logs` (`17l_rfBIRm7_ZMnOpniz34qvNuA7zzycs`).
3. The `raw_results` folder publicly lists six variant-named ZIPs. The prior file ID `1QAST-IzBr2rhAteZq_vc0GZszinIOxbD` is displayed as `spiketrack_s256_t1.zip`; therefore its release variant is `S256_T1_CONFIRMED` independently of prediction accuracy.
4. The `model_weight` folder publicly lists `spiketrack_s256_t1.pth.tar` and `spiketrack_s256_t3.pth.tar`. The README-linked Hugging Face repository exposes exact LFS SHA-256 OIDs for the same two filenames and byte sizes.

## Metadata method and boundary

- Drive hierarchy, file IDs, display names, MIME types, byte sizes and timestamps were read from the public folder pages and their public listing payloads. The first raw ZIP's HTTP `Last-Modified` header independently aligned to the same second after server rounding.
- Five missing raw ZIPs were downloaded for text-only inspection; the exact prior S256-T1 ZIP was reused. New transfer was 88,340,664 bytes (84.248222 MiB), below the 250 MiB cap; every file was below 100 MiB.
- All 24,528 non-directory archive members across the six ZIPs are `.txt`; image/video member count is zero. No benchmark image dataset or checkpoint was downloaded.
- ZIPs remain outside the repository. Only hashes, complete member lists, comparison tables and metadata are preserved here.

## Scientific interpretation

`RAW_MAPPING_RESOLVED` means the official release archive identity is mapped to its author-declared filename/folder variant. It does not turn the unresolved local-versus-release numerical mismatch into a reproduction pass. All mapping decisions here exclude accuracy-based inference.
