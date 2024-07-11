# olaf-llm-nlp4kgc2024
LLM experiments for ontology learning with OLAF for NLP4KGC 2024

# Installation

```bash
git clone https://github.com/wikit-ai/olaf-llm-nlp4kgc2024.git
cd olaf-llm-nlp4kgc2024
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

Running the different scripts requires the followwing environment variables you can set in a `.env` file:

```Bash
OPENAI_API_KEY=your-openai-api-key
MISTRAL_API_KEY=your-mistral-api-key
DATA_PATH=/path/to/your/local/data/folder/
RESULTS_PATH=/path/to/your/local/results/folder/
JAVA_EXE=/path/to/your/local/java/folder/java.exe
ROBOT_JAR=C:/path/to/your/local/obo/robot/cli/tool/folder/robot.jar
```

# Data

The first text used to learn the ontology is created based on the Pizza Ontology labels ([Pizza Ontology tutorial](https://github.com/owlcs/pizza-ontology/tree/master)). 

The labels are extracted and grouped together in the ``data/pizza_onto_labels.txt`` file. 

A prompt is constructed to ask GPT-4 to create a text based on these labels. 

The script used is ``scripts/pizza_description_creation.py`` and can be ran with the following command:

```bash
python scripts/pizza_description_creation.py
```

The text obtained is stored in the ``data/pizza_description.txt`` file.


The second text used to learn the ontology is the description of the [C10-DET dataset](https://www.kaggle.com/datasets/lirick/gc10-det). 

The text is available in the ``data/defect_detection_description.txt`` file.

An ontology is manually built from this text and available in the ``data/defect_onto_ground_truth.ttl`` file.

# Scripts

## LLM : text to OWL

Scripts to create an OWL ontology based on the ontologies textual description with an LLM.

For OpenAI model: 
```bash
python scripts/llm_text_to_owl_openai.py
```
Results are stored in `results/llm_text_to_owl/llm_owl_<pizza/defect>_onto_openai.ttl`

For Mistral model: 
```bash
python scripts/llm_text_to_owl_mistral.py
```
Results are stored in `results/llm_text_to_owl/llm_owl_<pizza/defect>_onto_mistral.ttl`

## LLM pipeline

Script to create an OWL ontology based on the ontologies textual description with a pipeline made up with LLM components.

For OpenAI model:
```bash
python scripts/llm_pipeline_openai.py
```
Results are stored in `results/llm_pipeline/llm_pipeline_<pizza/defect>_kr_rgf_graph_openai.ttl` and `results/llm_pipeline/llm_pipeline_<pizza/defect>_kr_openai.json`.

For Mistral model:
```bash
python scripts/llm_pipeline_mistral.py
```
Results are stored in `results/llm_pipeline/llm_pipeline_<pizza/defect>_kr_rgf_graph_mistral.ttl` and `results/llm_pipeline/llm_pipeline_<pizza/defect>_kr_mistral.json`.

## No LLM pipeline 

Script to create an OWL ontology based on the ontologies textual description with a pipeline made up without LLM components.

```bash
python scripts/no_llm_pipeline.py
```

Results are stored in `results/no_llm_pipeline/no_llm_pipeline_<pizza/defect>_kr_rgf_graph.ttl` and `results/no_llm_pipeline/no_llm_pipeline_<pizza/defect>_kr.json`.

## Pipeline components

The `scripts/pipeline_components_analysis.ipynb` notebook compare available techniques in OLAF for each ontology learning pipeline component.
The pizza ontology use case is used with the OpenAI model. 

Results are stored in `results/components_analysis/`.

# Results

All results are stored in the folder corresponding to the ontology learning technique used. 

Results analysis are available in the `results/<pizza/defect>results_analysis.ipynb` notebook.

The folder `results/components_analysis` contains materials to discuss the performances of pipeline components.
