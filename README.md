
---

# [Wikipedia Article Comparison](https://wikipedia.com/): **Xi Jinping vs. Vladimir Putin**

> ## **Project Overview**

This project compares the [Wikipedia article on Xi Jinping](https://en.wikipedia.org/wiki/Xi_Jinping) and the [Wikipedia article on Vladimir Putin](https://en.wikipedia.org/wiki/Vladimir_Putin) across **20 years** to uncover and analyze differences in portrayal, sentiment, and biases. By exploring their biographical content, we aim to objectively measure public perception differences of each leader.

Presentation Slides: [View Here](https://docs.google.com/presentation/d/1wSAak6iymiAiT6gbfA9WztMHbwIN8lsB3Q6jBDtRzlA/edit?usp=sharing)

---

> ## **Repository Structure**


```plaintext
├── 📁 data
│   ├── sections_grouping.json
│   ├── wikiarticles_opinion_mining_results.feather
├── 📁 notebooks
│   ├── visualising_findings.ipynb
│   ├── nlp_modelling.ipynb
│   ├── basic_visualisation.ipynb
│   ├── embeddings.ipynb
│   ├── requirements.txt
│   └── download_convert_xml.ipynb
├── 📁 modules
│   ├── wiki_parser.py
│   ├── xml_to_dataframe.py
│   ├── download_wiki_revisions.py
│   ├── nlp.py
│   └── preprocess_articles.py
├── 📁 results                           
│   ├── Prophet_Forecast_Putin.png
│   ├── political_lean_policy.svg
│   └── revision_trends.svg
└── requirements.txt    
└── README.md
```

- **data**: Contains processed data files, e.g., `wikiarticles_opinion_mining_results.feather`.
- **notebooks**: Jupyter notebooks for visualization, NLP modeling, and pre-processing.
- **modules**: Python scripts for data parsing, processing, and NLP tasks.
- **results**: Saved visualizations and analysis plots for the project.

---

> ## **Repository Components**

### **📁 notebooks**


This directory contains all Jupyter notebooks developed for the project:

- **`visualising_findings.ipynb`**  
 Contains the visual analysis based on *nlp_df* and *df* data frames created in `nlp_modelling.ipynb`. This notebook includes all visualizations, with outputs saved in the results folder.
  
- **`basic_visualisation.ipynb`** 
Generates plots for seasonal decomposition and revision frequency analysis.

- **`nlp_modelling.ipynb`** 
 Focuses on opinion mining by evaluating bias, emotional sentiment, and political leaning through various NLP techniques.

- **`embeddings.ipynb`**   
Analyzes word embeddings using GloVe to calculate and visualize document similarity over time between Wikipedia articles on Vladimir Putin and Xi Jinping.

- **`pre_processing.ipynb`**  
 Preprocesses and structures data from Wikipedia articles on Xi Jinping and Vladimir Putin by extracting and categorizing sections from their XML files. The data is organized into structured data frames and saved in formats like `wikiarticles_opinion_mining_results.feather`, utilizing functions from the `modules` folder.

- **`download_convert_xml.ipynb`**  
  Facilitates downloading and processing of Wikipedia article revisions for Vladimir Putin and Xi Jinping (additional terminal-based paging commands were used but are not included here).

### **📁 modules**

This folder contains all files used for parsing and pre-processing data:

- ```download_wiki_revisions.py``` and ```xml_to_dataframe.py```  
Created by [@Bernie Hogan](https://github.com/berniehogan) and shared with us for research purposes. These scripts were instrumental in the early stages of the project, though *xml_to_dataframe.py* was used minimally.

- ```claude_wiki_parser.py```  
  Initially used with Claude for file parsing; however, it encountered significant issues with parsing consistency due to structural shifts in XML formatting around the mid-2010s. While this approach had limitations, it provided valuable insights for further refinement.

- ```wiki_parser.py```  
  This script was developed in-house, building upon ideas from previous code to improve handling and adapt to structural variations in the XML data. It ultimately served as the primary tool for parsing.

- ```embeddings_nlp.py```  
  Used for text processing tasks, including tokenization, stopword removal, and generating TF-IDF-weighted embeddings to support subsequent NLP analysis.

### **📁 data**

The data folder provides a condensed version of the complete data files utilized in the project, originally exceeding 5 GB and therefore not fully uploaded. Key files include:

* ```wikiarticles_opinion_mining_results.feather```:  
  Contains post-processed data with the final monthly revision of Wikipedia articles on Xi Jinping and Vladimir Putin. This dataset includes various columns that represent the results from NLP modeling, such as bias scores, political leaning indicators, and different emotion scores.

**Data Snapshot:**

| title   | text   | file_id | month | year | article_name   | category             | date       | bias_score | bias_class | ... | fear_emotion | joy_emotion | negative_emotion | positive_emotion | sadness_emotion | surprise_emotion | trust_emotion | left_lean | center_lean | right_lean |
|---------|--------|---------|-------|------|----------------|----------------------|------------|------------|------------|-----|--------------|-------------|------------------|------------------|-----------------|-----------------|---------------|-----------|-------------|------------|
| 240988  | Quotations One of Putin's favorite sports is the martial ... | 17911161  | 06    | 2005 | Vladimir Putin   | Communications        | 2005-06-01 | 0.530233   | Non-biased | ... | 0.013889      | 0.027778    | 0.013889         | 0.062500         | 0.013889       | 0.020833        | 0.041667      | 0.517628  | 0.261512   | 0.220860   |
| 85055   | Early years and KGB career 30T23::45Z Krawndawg Mistranslation...? wiki... | 209344256 | 04    | 2008 | Vladimir Putin   | Career Progression    | 2008-04-01 | -0.705010  | Biased     | ... | 0.010309      | 0.012371    | 0.020619         | 0.053608         | 0.008247       | 0.012371        | 0.043299      | 0.020095  | 0.969789   | 0.010116   |

* ```sections_groupping.json```:  
  Contains categorized titles and sections related to Vladimir Putin and Xi Jinping, organized with support from manual review and language models, such as Claude and Mistral. These models helped analyze text, identify patterns, and structure topics to ensure a well-organized categorization spanning the last 20 years.

* ```wikiarticles_seg_data.feather``` ([link to file](https://drive.google.com/file/d/1a4-HzPrVOqPmL7O6qYAdbVJBKlEE_6tu/view?usp=drive_link)) (Not in repository):  
  This file includes a comprehensive dataframe of all parsed and segmented revisions. Unlike the opinion-mining dataset, it contains all revisions without monthly limits, allowing for detailed analysis across time. At 535.4 MB, it doesn’t include columns from NLP modeling but does retain text with section groupings.

**Data Snapshot:**

| title                  | text                                                    | file_id     | month | year | article_name   | category             |
|------------------------|---------------------------------------------------------|-------------|-------|------|----------------|----------------------|
| Political career       | , ]] In , Putin joined the KGB and trained at ...       | 1248941326  | 10    | 2024 | Vladimir Putin | Career Progression   |
| Political future       | Under the Putin administration, the Russian eco...      | 197413934   | 03    | 2008 | Vladimir Putin | Leadership Tenures   |


--- 

> ## **Analysis & Methodology**

This project includes several analytical methods to explore Wikipedia’s representation of Xi Jinping and Vladimir Putin:

### **1. Document Cosine Similarity with Word Embeddings**

  - **Method**: Using GloVe embeddings, we calculated cosine similarity between document sections to assess semantic overlap.
  - **Purpose**: To reveal common or diverging thematic emphasis in articles.
  - **Output**: Cosine similarity scores to illustrate content overlap across topics.
  - **References**: Pennington, J., Socher, R., & Manning, C.D. (2014). GloVe: Global Vectors for Word Representation. Stanford University. Available at: [GloVe](https://nlp.stanford.edu/projects/glove/.).

**Visualization Example**<br>

<img src="readme images/image-2.png" alt="Document Cosine Similarity" width="800"/>


### **2. Bias Analysis**

  - **Method**: Using DistilBERT and the MBIC Dataset, bias scores were derived for sections in each article.
  - **Purpose**: To compare biased and unbiased sections in Xi Jinping’s and Vladimir Putin’s articles.
  - **Output**: Bias classification per section, visualized in plots.
  - **References**: Raza, S., Reji, D. J., & Ding, C. (2022). Dbias: Detecting biases and ensuring fairness in news articles. International Journal of Data Science and Analytics, 1-21. Springer.[Paper Link] (https://link.springer.com/article/10.1007/s41060-022-00359-4)

**Visualization Example**<br>

<img src="readme images/image.png" alt="Bias Distribution" width="800"/>


### **3. Emotion Analysis**

  - **Method**: NRC Emotion Lexicon identified sentiment and emotions in each section.
  - **Purpose**: Quantifies emotional tones (e.g., trust, anger) across articles.
  - **Output**: Visuals highlighting emotional undertones for biographical, political, and personal sections.
  - **References**: Mohammad, S., & Turney, P. (2010). Emotions evoked by common words and phrases: Using Mechanical Turk to create an emotion lexicon. Proceedings of the NAACL HLT 2010 Workshop on Computational Approaches to Analysis and Generation of Emotion in Text, pp. 26–34. Association for Computational Linguistics., [NRC Emotion Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm).

**Visualization Example**<br>

<img src="readme images/image-3.png" alt="Emotion Analysis" width="800"/>

### **4. Political Lean Analysis**

  - **Method**: BERT-based model predicts ideological slants, trained on news articles for left, center, and right leaning biases.
  - **Purpose**: To detect ideological biases in sections, accounting for adversarial media.
  - **Output**: Scores for ideological lean, classified per article section.
  - **References**: Baly, R., Da San Martino, G., Glass, J., & Nakov, P. (2020). We can detect your bias: Predicting the political ideology of news articles. Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 4982–4991. Association for Computational Linguistics. [Paper Link](https://aclanthology.org/2020.emnlp-main.404/).

**Visualization Example**<br>

<img src="readme images/image-4.png" alt="Political Lean Analysis" width="800"/>

### **5. Revision Analysis**

  - **Method**: Analyzed revision frequency and content adjustments over time.
  - **Purpose**: Examines editorial patterns and content updates for historical context.
  - **Output**: Graphs and statistical trends across years for each article.

**Visualization Example**<br>

<img src="readme images/image-1.png" alt="Revision Trends" width="800"/>

---

> ## **Discussion**

Through a multi-dimensional approach, this project presents an objective comparison of Wikipedia articles on Xi Jinping and Vladimir Putin. From semantic similarity and bias detection to political lean and emotional analysis, this analysis sheds light on editorial nuances that shape public perception.

For more details, see our [full presentation](https://docs.google.com/presentation/d/1wSAak6iymiAiT6gbfA9WztMHbwIN8lsB3Q6jBDtRzlA/edit?usp=sharing).