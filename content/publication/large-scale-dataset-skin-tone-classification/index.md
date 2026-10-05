---
title: "Large-Scale Dataset and Benchmark for Skin Tone Classification in the Wild"
authors:
- vitor-pereira-matias
- marcus-vinicius-lobo-costa
- joao-batista-neto
- Tiago Novello de Brito
date: "2026-03-02T00:00:00Z"
publication_types: ["article"]
publication: "*arXiv*, 2026"
abstract: "Deep learning models often inherit biases from their training data. While fairness across gender and ethnicity is well-studied, fine-grained skin tone analysis remains a challenge due to the lack of granular, annotated datasets. Existing methods often rely on the medical 6-tone Fitzpatrick scale, which lacks visual representativeness, or use small, private datasets that prevent reproducibility, or often rely on classic computer vision pipelines, with a few using deep learning. They overlook issues like train-test leakage and dataset imbalance, and are limited by small or unavailable datasets. In this work, we present a comprehensive framework for skin tone fairness. First, we introduce the STW, a large-scale, open-access dataset comprising 42,313 images from 3,564 individuals, labeled using the 10-tone MST scale. Second, we benchmark both Classic Computer Vision (SkinToneCCV) and Deep Learning approaches, demonstrating that classic models provide near-random results, while deep learning reaches nearly annotator accuracy. Finally, we propose SkinToneNet, a fine-tuned ViT that achieves state-of-the-art generalization on out-of-domain data, which enables reliable fairness auditing of public datasets like CelebA and VGGFace2. This work provides state-of-the-art results in skin tone classification and fairness assessment. Code and data available soon"
url_pdf: "https://arxiv.org/abs/2603.02475"
url_source: "https://arxiv.org/abs/2603.02475"
---
