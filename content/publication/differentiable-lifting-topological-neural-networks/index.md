---
title: "Differentiable Lifting for Topological Neural Networks"
authors:
- Jorge Luiz Franco
- Gabriel Duarte
- Alexander Nikitin
- moacir-antonelli-ponti
- Diego Mesquita
- Amauri Souza
date: "2026-01-26T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*The Fourteenth International Conference on Learning Representations (ICLR 2026)*"
abstract: "Topological neural networks (TNNs) enable leveraging higher-order structures on graphs (e.g., cycles and cliques) to boost the expressive power of message-passing neural networks. In turn, however, these structures are typically identified a priori through an unsupervised graph lifting operation. Notwithstanding, this choice is crucial and may have a drastic impact on a TNN's performance on downstream tasks. To circumvent this issue, we propose ∂lift (DiffLift), a general framework for learning graph liftings to hypergraphs and cellular, simplicial, and combinatorial complexes in an end-to-end fashion. In particular, our approach leverages learned vertex-level latent representations to identify and parameterize distributions over candidate higher-order cells for inclusion. This results in a scalable model which can be readily integrated into any TNN. Our experiments show that ∂lift outperforms existing lifting methods on multiple benchmarks for graph and node classification across different TNN architectures, with TNN+ ∂lift combinations surpassing standard GNN baselines. Notably, our approach leads to gains of up to 45% over static liftings, including both connectivity- and feature-based ones."
url_pdf: "https://openreview.net/pdf?id=eC89CbINIw"
url_code: "https://github.com/JorgeLuizFranco/difflifting"
---

This paper was also a NeurIPS paper https://neurips.cc/virtual/2025/loc/san-diego/123646.