---
title: "Region-Aware CLS Token Augmentation for Fine-Grained Image Retrieval"
authors:
- Ian de Holanda Cavalcanti Bezerra
- Vivek Trivedy
- lucas-pascotti-valem
- Longin Jan Latecki
date: "2026-09-29T00:00:00Z"
publication_types: ["paper-conference"]
publication: "*39th Conference on Graphics, Patterns and Images (SIBGRAPI 2026)*"
abstract: "Image retrieval methods often rely on a single global semantic descriptor extracted from an image, e.g., the [CLS] token in vision transformers. However, trying to squeeze all the semantic information of an image into a single descriptor can hurt downstream retrieval performance, especially for fine-grained retrieval tasks. In this work, we augment the semantic tokens in the newer visual transformers, the global [CLS] token and the four register tokens, with a carefully selected collection of spatial tokens, aiming to capture the spatial region representation that characterizes the contents captured in each of the semantic tokens. We leverage the DINOv2-reg model, which includes register tokens that emergently learn object and part-based representations. For each cue token ([CLS] and each register token), we find a buddy image patch token and extract an N × N patch region to produce a set of localized ROI tokens. Our approach automatically captures important regions of interest without any external bounding boxes or saliency modules, purely by matching semantic tokens with their spatial representation regions. Furthermore, we incorporate these tokens into a multi-vector retrieval framework inspired by ColBERT, enabling fine-grained matching via a per-token alignment mechanism while avoiding the large storage cost of keeping all patch embeddings. Through extensive experiments, we find that (1) register tokens encode useful fine-grained details that can complement the [CLS] token; (2) automatically pooled ROI tokens further improve fine-grained discrimination; and (3) multi-vector retrieval with a small set of tokens improves over a DINOv2-reg single-vector baseline while remaining tractable for large-scale search."
url_pdf: "http://sibgrapi.sid.inpe.br/col/sid.inpe.br/sibgrapi/2026/09.04.04.05/doc/bezerra-44-inpe.pdf"
url_code: "https://github.com/IdhcbIan/Augmenting-CLS-with-ROI-tokens"
---
