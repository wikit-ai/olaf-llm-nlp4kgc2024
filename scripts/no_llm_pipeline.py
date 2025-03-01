import os

from dotenv import load_dotenv
load_dotenv()

import spacy

from olaf import Pipeline
from olaf.data_container import CandidateTerm
from olaf.commons.spacy_processing_tools import is_not_punct, is_not_stopword
from olaf.pipeline.pipeline_component.candidate_term_enrichment import KnowledgeBasedCTermEnrichment
from olaf.pipeline.pipeline_component.concept_relation_extraction import(
    AgglomerativeClusteringConceptExtraction,
    AgglomerativeClusteringRelationExtraction
)
from olaf.pipeline.pipeline_component.concept_relation_hierarchy import SubsumptionHierarchisation
from olaf.pipeline.pipeline_component.term_extraction import (
    POSTermExtraction,
    TFIDFTermExtraction
)
from olaf.commons.kr_to_rdf_tools import (
    kr_concepts_to_owl_classes, kr_relations_to_owl_obj_props, 
    kr_metarelations_to_owl, kr_relations_to_anonymous_some_parent, concept_lrs_to_owl_individuals
)
from olaf.pipeline.pipeline_component.axiom_extraction import OWLAxiomExtraction
from olaf.repository.corpus_loader import TextCorpusLoader
from olaf.repository.knowledge_source import WordNetKnowledgeResource
from olaf.repository.serialiser import KRJSONSerialiser


def create_pipeline() -> Pipeline:
    """Initialise a pipeline.

    Returns
    -------
    Pipeline
        The new pipeline created.
    """
    spacy_model = spacy.load("en_core_web_lg")
    corpus_loader = TextCorpusLoader(
        # corpus_path=os.path.join(os.getenv('DATA_PATH'), "pizza_description.txt")
        corpus_path=os.path.join(os.getenv('DATA_PATH'), "defect_detection_description.txt")
    )
    pipeline = Pipeline(
        spacy_model=spacy_model,
        corpus_loader=corpus_loader
    )
    return pipeline


def cts_post_processing(cts: set[CandidateTerm]) -> set[CandidateTerm]:
    """Post processing on candidate terms.
    Candidate terms with punctuation, stop words or verbs are removed.

    Parameters
    ----------
    cts: set[CandidateTerm]
        Set of candidate terms to filter.

    Returns
    -------
    set[CandidateTerm]
        The candidate terms validated.    
    """
    existing_cts = []
    new_cts = set()
    for ct in cts:
        keep = True
        if len(ct.corpus_occurrences) > 0:
            for co in ct.corpus_occurrences:
                for token in co:
                    if (not (is_not_punct(token)) or not (is_not_stopword(token)) or (token.pos_ == "VERB")):
                        keep = False
                        break
        else:
            keep = False
        if keep and ct.label not in existing_cts:
            new_cts.add(ct)
            existing_cts.append(ct.label)
    return new_cts


def add_pipeline_components(pipeline: Pipeline) -> Pipeline:
    """Create pipeline without LLM components.

    Parameters
    ----------
    pipeline: Pipeline
        The pipeline into which the components are to be added. 

    Returns
    -------
    Pipeline
        The pipeline updated with new components.
    """
    tfidf_term_extraction = TFIDFTermExtraction(
        cts_post_processing_functions=[cts_post_processing],
        max_term_token_length=3,
        candidate_term_threshold=0.05
    )
    pipeline.add_pipeline_component(tfidf_term_extraction)

    params = {
        
    }
    wn_kr = WordNetKnowledgeResource(
        use_domains=True,
        wordnet_domains_path="wordnet_domains.txt",
        enrichment_domains=set(["engineering", "industry"])
    )
    wn_term_enrichment = KnowledgeBasedCTermEnrichment(wn_kr)
    pipeline.add_pipeline_component(wn_term_enrichment)

    ac_concept_extraction = AgglomerativeClusteringConceptExtraction(
        embedding_model="sentence-transformers/sentence-t5-base",
        distance_threshold=0.1
    )
    pipeline.add_pipeline_component(ac_concept_extraction)

    sub_hierarchisation = SubsumptionHierarchisation(threshold=0.99)

    pipeline.add_pipeline_component(sub_hierarchisation)

    pos_term_extraction = POSTermExtraction(pos_selection=["VERB"])
    pipeline.add_pipeline_component(pos_term_extraction)

    pipeline.add_pipeline_component(wn_term_enrichment)

    ac_relation_extraction = AgglomerativeClusteringRelationExtraction(
        embedding_model="sentence-transformers/sentence-t5-base",
        distance_threshold=0.1
    )
    pipeline.add_pipeline_component(ac_relation_extraction)

    axiom_generators = {    
            kr_concepts_to_owl_classes,
            kr_relations_to_owl_obj_props,
            kr_metarelations_to_owl,
            kr_relations_to_anonymous_some_parent,
            concept_lrs_to_owl_individuals
        }
    owl_axiom_extraction = OWLAxiomExtraction(
        owl_axiom_generators=axiom_generators,
        base_uri="https://github.com/wikit-ai/olaf-llm-nlp4kgc2024/o/example#"
    )
    pipeline.add_pipeline_component(owl_axiom_extraction)

    return pipeline


def main() -> None:
    """LLM pipeline execution."""
    pipeline = create_pipeline()
    pipeline = add_pipeline_components(pipeline)
    pipeline.run()

    kr_serialiser = KRJSONSerialiser()
    kr_serialisation_path = os.path.join(os.getenv("RESULTS_PATH"), "no_llm_pipeline", "no_llm_pipeline_defect_kr.json")
    kr_serialiser.serialise(kr=pipeline.kr, file_path=kr_serialisation_path)

    kr_rdf_graph_path = os.path.join(os.getenv("RESULTS_PATH"), "no_llm_pipeline", "no_llm_pipeline_defect_kr_rdf_graph.ttl")
    pipeline.kr.rdf_graph.serialize(kr_rdf_graph_path, format="ttl")

    print(f"Nb concepts: {len(pipeline.kr.concepts)}")
    print(f"Nb relations: {len(pipeline.kr.relations)}")
    print(f"Nb metarelations: {len(pipeline.kr.metarelations)}")
    print(f"The KR object has been JSON serialised in : {kr_serialisation_path}")
    print(f"The KR RDF graph has been serialised in : {kr_rdf_graph_path}")


if __name__ == "__main__":
    main()
