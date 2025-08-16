"""
AI Features Database Models
New tables to store AI-generated features from the data framework
"""

from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.database import Base


class ProblemEmbedding(Base):
    """Store semantic embeddings for problems"""
    __tablename__ = 'problem_embeddings'
    
    problem_id = Column(String(50), ForeignKey('problems.id'), primary_key=True)
    
    # Embedding vectors (128-dimensional)
    title_embedding = Column(JSON, nullable=False)  # Title embedding vector
    description_embedding = Column(JSON, nullable=False)  # Description embedding vector
    combined_embedding = Column(JSON, nullable=False)  # Full problem embedding
    
    # Metadata
    embedding_model = Column(String(50), default='dsatrain_v1')
    embedding_dimension = Column(Integer, default=128)
    
    # Quality metrics
    embedding_quality_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("Problem", backref="embedding")
    
    __table_args__ = (
        Index('idx_embedding_quality', 'embedding_quality_score'),
    )


class ProblemDifficultyVector(Base):
    """Store multi-dimensional difficulty analysis"""
    __tablename__ = 'problem_difficulty_vectors'
    
    problem_id = Column(String(50), ForeignKey('problems.id'), primary_key=True)
    
    # 5-dimensional difficulty vector
    algorithmic_complexity = Column(Float, nullable=False)      # 0.0-1.0
    implementation_difficulty = Column(Float, nullable=False)   # 0.0-1.0  
    mathematical_content = Column(Float, nullable=False)        # 0.0-1.0
    data_structure_usage = Column(Float, nullable=False)        # 0.0-1.0
    optimization_required = Column(Float, nullable=False)       # 0.0-1.0
    
    # Computed metrics
    overall_difficulty = Column(Float, nullable=False)  # Average of dimensions
    difficulty_confidence = Column(Float, default=0.8)  # Confidence in assessment
    
    # Vector metadata
    vector_version = Column(String(20), default='v1.0')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("Problem", backref="difficulty_vector")
    
    __table_args__ = (
        Index('idx_overall_difficulty', 'overall_difficulty'),
        Index('idx_algo_complexity', 'algorithmic_complexity'),
    )


class ConceptNode(Base):
    """Store concept graph nodes"""
    __tablename__ = 'concept_nodes'
    
    id = Column(String(50), primary_key=True)  # e.g., "dynamic_programming"
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Hierarchy and difficulty
    difficulty_level = Column(Integer, default=1)  # Computed from prerequisites
    problem_count = Column(Integer, default=0)     # Problems tagged with this concept
    
    # Graph metadata
    graph_version = Column(String(20), default='v1.0')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_concept_difficulty', 'difficulty_level'),
    )


class ConceptPrerequisite(Base):
    """Store prerequisite relationships between concepts"""
    __tablename__ = 'concept_prerequisites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_id = Column(String(50), ForeignKey('concept_nodes.id'), nullable=False)
    prerequisite_id = Column(String(50), ForeignKey('concept_nodes.id'), nullable=False)
    
    # Relationship strength
    importance = Column(Float, default=1.0)  # How important this prerequisite is
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    concept = relationship("ConceptNode", foreign_keys=[concept_id], backref="prerequisites")
    prerequisite = relationship("ConceptNode", foreign_keys=[prerequisite_id], backref="dependents")
    
    __table_args__ = (
        Index('idx_concept_prereq', 'concept_id', 'prerequisite_id'),
    )


class ProblemConceptMapping(Base):
    """Map problems to concepts"""
    __tablename__ = 'problem_concept_mapping'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False)
    concept_id = Column(String(50), ForeignKey('concept_nodes.id'), nullable=False)
    
    # Mapping strength
    relevance_score = Column(Float, default=1.0)  # How relevant this concept is to the problem
    is_primary_concept = Column(Boolean, default=False)  # Is this the main concept?
    
    # Source of mapping
    mapping_source = Column(String(50), default='automated')  # automated/manual/expert
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    problem = relationship("Problem", backref="concept_mappings")
    concept = relationship("ConceptNode", backref="problem_mappings")
    
    __table_args__ = (
        Index('idx_problem_concept', 'problem_id', 'concept_id'),
        Index('idx_primary_concepts', 'problem_id', 'is_primary_concept'),
    )


class GoogleInterviewFeatures(Base):
    """Store Google interview relevance features"""
    __tablename__ = 'google_interview_features'
    
    problem_id = Column(String(50), ForeignKey('problems.id'), primary_key=True)
    
    # Feature scores (0.0-1.0)
    base_google_relevance = Column(Float, nullable=False)
    frequency_score = Column(Float, nullable=False)
    difficulty_appropriateness = Column(Float, nullable=False)
    concept_coverage = Column(Float, nullable=False)
    implementation_complexity = Column(Float, nullable=False)
    
    # Final computed score
    final_interview_probability = Column(Float, nullable=False)
    
    # Feature weights used in calculation
    feature_weights = Column(JSON, nullable=False)
    
    # Metadata
    features_version = Column(String(20), default='v1.0')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("Problem", backref="google_features")
    
    __table_args__ = (
        Index('idx_interview_probability', 'final_interview_probability'),
        Index('idx_google_relevance', 'base_google_relevance'),
    )


class ProblemQualityScore(Base):
    """Store comprehensive quality scores from quality engine"""
    __tablename__ = 'problem_quality_scores'
    
    problem_id = Column(String(50), ForeignKey('problems.id'), primary_key=True)
    
    # Content quality dimensions
    completeness_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)
    specificity_score = Column(Float, nullable=False)
    educational_value_score = Column(Float, nullable=False)
    
    # Overall content quality
    content_quality_overall = Column(Float, nullable=False)
    
    # Google relevance dimensions
    topic_relevance = Column(Float, nullable=False)
    difficulty_appropriateness = Column(Float, nullable=False)
    frequency_score = Column(Float, nullable=False)
    company_alignment = Column(Float, nullable=False)
    
    # Overall Google relevance
    google_relevance_overall = Column(Float, nullable=False)
    
    # Final combined score
    overall_quality_score = Column(Float, nullable=False)
    
    # Recommendation
    recommendation = Column(String(30), nullable=False)  # highly_recommended/recommended/etc.
    
    # Quality engine metadata
    scoring_model_version = Column(String(20), default='v1.0')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("Problem", backref="quality_scores")
    
    __table_args__ = (
        Index('idx_overall_quality', 'overall_quality_score'),
        Index('idx_recommendation', 'recommendation'),
        Index('idx_google_relevance_overall', 'google_relevance_overall'),
    )


class BehavioralCompetency(Base):
    """Store behavioral competency framework"""
    __tablename__ = 'behavioral_competencies'
    
    id = Column(String(50), primary_key=True)  # e.g., "googleyness"
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Competency hierarchy
    parent_competency_id = Column(String(50), ForeignKey('behavioral_competencies.id'))
    competency_level = Column(Integer, default=1)  # 1=top level, 2=sub-competency, etc.
    
    # Assessment criteria
    assessment_criteria = Column(JSON)  # Structured criteria for evaluation
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("BehavioralCompetency", remote_side=[id], backref="sub_competencies")
    
    __table_args__ = (
        Index('idx_competency_level', 'competency_level'),
    )


class BehavioralQuestion(Base):
    """Store structured behavioral questions"""
    __tablename__ = 'behavioral_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    
    # Categorization
    competency_id = Column(String(50), ForeignKey('behavioral_competencies.id'), nullable=False)
    question_type = Column(String(30), default='behavioral')  # behavioral/situational/technical
    difficulty_level = Column(String(20), default='medium')   # easy/medium/hard
    
    # Source information
    source_document = Column(String(100))  # Original document source
    source_type = Column(String(30))       # university/google_official/synthetic
    
    # Assessment metadata
    expected_response_time = Column(Integer)  # Expected response time in minutes
    follow_up_questions = Column(JSON)        # List of follow-up questions
    evaluation_criteria = Column(JSON)        # STAR method criteria
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    competency = relationship("BehavioralCompetency", backref="questions")
    
    __table_args__ = (
        Index('idx_competency_difficulty', 'competency_id', 'difficulty_level'),
    )


class ConversationTemplate(Base):
    """Store AI conversation templates for interviews"""
    __tablename__ = 'conversation_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    competency_id = Column(String(50), ForeignKey('behavioral_competencies.id'), nullable=False)
    
    # Template structure
    template_name = Column(String(100), nullable=False)
    opening_questions = Column(JSON, nullable=False)
    follow_up_prompts = Column(JSON, nullable=False)
    probing_questions = Column(JSON, nullable=False)
    evaluation_criteria = Column(JSON, nullable=False)
    
    # Template metadata
    template_type = Column(String(30), default='standard')  # standard/advanced/screening
    estimated_duration = Column(Integer)  # Duration in minutes
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    competency = relationship("BehavioralCompetency", backref="conversation_templates")
    
    __table_args__ = (
        Index('idx_competency_template', 'competency_id', 'template_type'),
    )


class DataPipelineStatus(Base):
    """Track data pipeline status and quality"""
    __tablename__ = 'data_pipeline_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Pipeline information
    pipeline_component = Column(String(50), nullable=False)  # unified_data/ai_features/quality_scoring
    status = Column(String(20), nullable=False)              # healthy/degraded/failed
    
    # Metrics
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    
    # Status details
    status_message = Column(Text)
    error_details = Column(JSON)
    
    # Processing metadata
    pipeline_version = Column(String(20))
    execution_time_seconds = Column(Float)
    
    # Timestamps
    last_updated = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_pipeline_status', 'pipeline_component', 'status'),
        Index('idx_pipeline_updated', 'last_updated'),
    )
