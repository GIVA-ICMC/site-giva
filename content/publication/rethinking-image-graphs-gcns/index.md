---
title: "Rethinking Image Graphs for GCNs: Beyond Similarity with Diversity"
authors:
- Diego Giaretta de Paulo
- lucas-pascotti-valem
date: "2026-09-29T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*39th Conference on Graphics, Patterns and Images (SIBGRAPI 2026)*"
abstract: "The growing volume of available images demands effective classification methods. Even with the powerful representations provided by foundation models, annotating data for specific tasks remains costly, which makes semi-supervised learning an attractive direction. Graph Convolutional Networks (GCNs) are well suited to this setting, as they exploit relationships between labeled and unlabeled samples to learn from limited supervision. Applying GCNs to images, however, requires a graph to be constructed from the data, and the common strategies connect each image only to its most similar neighbors. We hypothesize that relying on similarity alone favors redundant, homogeneous neighborhoods, while diversity favors complementary samples and can therefore improve classification effectiveness. To address this, we propose BRID-G (Better Results with Influence Diversification for Graphs), a graph-construction strategy inspired by the original BRID method for data retrieval. Our approach aims to select diverse, non-redundant neighbors through notions of influence and dominance, treating proximity between samples as mutual influence to discard those redundant with the previously selected neighbors. The selected neighbors are then refined with reciprocity and rank-correlation filtering. We evaluate BRID-G on three datasets, four feature extractors, and two GCN models. It surpasses the k-NN baseline in all configurations, by up to 11%, and matches or exceeds the reciprocal k-NN baseline in most settings, with its advantage growing as labels become scarcer."
url_pdf: "http://sibgrapi.sid.inpe.br/col/sid.inpe.br/sibgrapi/2026/09.04.03.59/doc/giaretta-53-inpe.pdf"
url_code: "https://bridg.lucasvalem.com"
---
