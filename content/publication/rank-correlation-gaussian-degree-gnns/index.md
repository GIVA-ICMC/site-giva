---
title: "Rank Correlation Meets Gaussian Degree Normalization in GNNs for Image Classification"
authors:
- Rafael Mendonça Duarte
- Gabriel Maia Brito
- lucas-pascotti-valem
date: "2026-09-29T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*39th Conference on Graphics, Patterns and Images (SIBGRAPI 2026)*"
abstract: "Semi-supervised learning is increasingly important for image classification, where labeled samples are scarce but unlabeled data is abundant. Graph Neural Networks (GNNs) are well suited to this setting, propagating label information from a few labeled instances across a graph that encodes how samples relate to one another. Their application to visual data, however, is challenging due to several factors, with two being the focus of this work. First, images often lack an explicit relational structure, so the graph is typically computed from feature similarity, most commonly through k-nearest neighbor (kNN) strategies. Second, many GNNs normalize message passing using the node degree, which counts a node's neighbors and, in unweighted similarity graphs, treats all of them as equally relevant, ignoring meaningful differences between them. In this paper, we propose D-GRaNDe, which combines two recent rank-based approaches. It builds the input graph with the Density-Guided Correlation Graph (DGCG) that computes edges from the rank correlation between image similarity rankings. Message passing is then normalized with the Gaussian Rank-based Neighborhood Degree (GRaNDe), which combines a node's neighbor count with the Gaussian-weighted distances to those neighbors. We evaluate D-GRaNDe against different graph constructions and several centrality-based degree measures across three datasets using only 10% of labeled data. In most cases, D-GRaNDe outperforms both of its individual components and several traditional and recent baselines for semi-supervised image classification."
url_pdf: "http://sibgrapi.sid.inpe.br/col/sid.inpe.br/sibgrapi/2026/09.04.04.10/doc/duarte-64-inpe.pdf"
url_code: "https://dgrande.lucasvalem.com"
---
