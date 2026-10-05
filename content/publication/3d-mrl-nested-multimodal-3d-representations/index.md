---
title: "3D-MRL: Nested Multimodal 3D Representations via Matryoshka Representation Learning"
authors:
- marcus-vinicius-lobo-costa
- vitor-pereira-matias
- Jeová Farias
- moacir-antonelli-ponti
date: "2026-08-21T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*The 37th British Machine Vision Conference (BMVC 2026)*"
abstract: "Vision-Language Models align point clouds with image and text embeddings, enabling zero-shot recognition, retrieval, and open-vocabulary understanding of 3D shapes. Existing multimodal 3D pre-training methods produce fixed-dimensional embeddings, requiring separate models for different computational budgets. We propose 3D Matryoshka Representation Learning (3D-MRL), a multimodal 3D pre-training framework based on Matryoshka Representation Learning. 3D-MRL learns nested 3D representations by aligning point clouds with frozen CLIP image and text embeddings while applying contrastive supervision across multiple embedding dimensions. The Matryoshka objective is applied only to the 3D encoder, allowing a single model to produce representations at different dimensionalities without retraining. Experiments on the Objaverse-LVIS, ModelNet40, and ScanNet datasets show that 3D-MRL achieves competitive performance on zero-shot and few-shot 3D recognition tasks. In addition, the learned representations support retrieval across different embedding dimensions within a single model. On Objaverse-LVIS, 3D-MRL improves Top-1 accuracy from 46.8% to 50.9%. Retrieval experiments further show that different embedding dimensions yield varying levels of semantic and geometric specificity."
url_pdf: "https://arxiv.org/pdf/2608.29285"
url_source: "https://arxiv.org/abs/2608.29285"
---

Accepted as a poster at BMVC 2026. Project page: https://usmarcv.github.io/3DMRL_page/.
