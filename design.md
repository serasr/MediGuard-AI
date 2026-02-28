# MediGuard Triage Design Document

## Overview

MediGuard Triage is an AI-powered emergency triage assistant that implements the AI-Instigated Human Oversight (AIHO) framework to provide transparent, uncertainty-aware clinical decision support. The system addresses the critical trust gap in clinical AI by embedding uncertainty quantification, explainability, and human oversight mechanisms into its core architecture rather than treating them as add-on features.

The system operates across three deployment modes: cloud-based for large hospitals with reliable connectivity, edge deployment for rural clinics with intermittent internet, and hybrid mode that seamlessly transitions between online and offline operation. This flexibility ensures AI-assisted triage reaches underserved populations while maintaining consistent performance standards.

## Architecture

### High-Level Architecture

The system follows a microservices architecture with clear separation between the AI inference engine, clinical decision support layer, user interface, and data management components. This modular design enables independent scaling, testing, and deployment of different system components.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web/Mobile    │    │   Voice Input   │    │   Admin Panel   │
│   Interface     │    │   Processing    │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │              API Gateway & Auth                     │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │           Clinical Decision Support Layer           │
         │  • Triage Orchestrator                             │
         │  • Explanation Generator                           │
         │  • Override Handler                                │
         │  • Uncertainty Quantifier                          │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │              AI Inference Engine                    │
         │  • Ensemble Triage Model                           │
         │  • Bayesian Uncertainty Estimation                 │
         │  • Clinical NLP Pipeline                           │
         │  • Confidence Calibration                          │
         └─────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────┐
         │              Data Management Layer                  │
         │  • Patient Data Store                              │
         │  • Decision Audit Log                              │
         │  • Model Version Control                           │
         │  • Sync & Backup Service                           │
         └─────────────────────────────────────────────────────┘
```

### Deployment Architecture

**Cloud Deployment**: Full-featured deployment on cloud infrastructure with real-time model updates, centralized logging, and horizontal scaling capabilities.

**Edge Deployment**: Lightweight deployment on local hardware (tablets, mini-PCs) with core triage functionality, local data storage, and periodic sync capabilities.

**Hybrid Mode**: Intelligent switching between cloud and edge modes based on connectivity, with seamless user experience regardless of deployment mode.

## Components and Interfaces

### AI Inference Engine

**Ensemble Triage Model**: Combines gradient-boosted decision trees for structured vital signs data with transformer-based models for unstructured symptom descriptions. The ensemble approach provides robustness against individual model failures and improves overall accuracy.

**Bayesian Uncertainty Estimation**: Implements Monte Carlo dropout and deep ensembles to quantify both epistemic uncertainty (model uncertainty) and aleatoric uncertainty (data uncertainty). This dual uncertainty quantification enables the system to distinguish between cases where more data would help versus cases where the model itself is uncertain.

**Clinical NLP Pipeline**: Processes free-text symptom descriptions using domain-adapted BERT models fine-tuned on clinical text. Extracts structured clinical concepts and maps them to standardized medical terminologies (ICD-10, SNOMED CT).

**Confidence Calibration**: Uses Platt scaling and temperature scaling to ensure confidence scores accurately reflect prediction reliability. Regular calibration validation ensures confidence scores remain meaningful as the model evolves.

### Clinical Decision Support Layer

**Triage Orchestrator**: Coordinates between different AI models, applies business rules, and manages the decision workflow. Implements the core AIHO framework logic for determining when human oversight is required.

**Explanation Generator**: Converts model outputs into plain-language explanations using SHAP values and clinical rule templates. References specific clinical guidelines (ICMR, AHA/ESC) and highlights the key factors influencing each decision.

**Override Handler**: Manages clinician overrides, collects feedback, and identifies patterns in override behavior. Implements active learning strategies to prioritize cases for model retraining based on override frequency and clinical importance.

**Uncertainty Quantifier**: Analyzes model confidence scores and clinical context to determine appropriate uncertainty thresholds. Dynamically adjusts thresholds based on clinical setting (rural vs urban), time of day, and historical override patterns.

### User Interface Components

**Triage Workflow Interface**: Streamlined interface optimized for speed with progressive disclosure of information. Core triage decision visible immediately, with expandable sections for detailed explanations and clinical reasoning.

**Voice Input Module**: Multi-language speech recognition supporting English, Hindi, Bengali, and Tamil. Includes medical vocabulary enhancement and noise filtering for clinical environments.

**Mobile-Responsive Design**: Optimized for tablets and smartphones commonly used in Indian healthcare settings. Touch-friendly controls and readable fonts for various lighting conditions.

**Admin Dashboard**: Real-time monitoring of system performance, override rates, and clinical outcomes. Configurable alerts and reporting capabilities for quality assurance and regulatory compliance.

## Data Models

### Patient Data Model
```typescript
interface PatientData {
  patientId: string;
  timestamp: Date;
  demographics: {
    age: number;
    gender: 'male' | 'female' | 'other';
    weight?: number;
    height?: number;
  };
  vitalSigns: {
    bloodPressure?: { systolic: number; diastolic: number };
    heartRate?: number;
    respiratoryRate?: number;
    temperature?: number;
    oxygenSaturation?: number;
    painScore?: number; // 1-10 scale
  };
  symptoms: {
    chiefComplaint: string;
    symptomDescription: string;
    duration: string;
    severity: 'mild' | 'moderate' | 'severe';
    associatedSymptoms: string[];
  };
  medicalHistory?: {
    chronicConditions: string[];
    currentMedications: string[];
    allergies: string[];
    recentHospitalizations: boolean;
  };
}
```

### Triage Decision Model
```typescript
interface TriageDecision {
  decisionId: string;
  patientId: string;
  timestamp: Date;
  recommendation: 'emergent' | 'urgent' | 'non-urgent';
  confidenceScore: number; // 0-100
  uncertaintyFlag: boolean;
  clinicalReasoning: {
    primaryFactors: string[];
    guidelineReferences: string[];
    riskAssessment: string;
    recommendedActions: string[];
  };
  modelMetadata: {
    modelVersion: string;
    ensembleWeights: Record<string, number>;
    uncertaintyComponents: {
      epistemicUncertainty: number;
      aleatoricUncertainty: number;
    };
  };
  clinicalOverride?: {
    overrideDecision: 'emergent' | 'urgent' | 'non-urgent';
    clinicianId: string;
    reasoning: string;
    timestamp: Date;
  };
}
```

### System Configuration Model
```typescript
interface SystemConfig {
  deploymentMode: 'cloud' | 'edge' | 'hybrid';
  uncertaintyThresholds: {
    emergentThreshold: number;
    urgentThreshold: number;
    nonUrgentThreshold: number;
  };
  clinicalGuidelines: {
    primaryGuideline: 'ICMR' | 'AHA' | 'ESC' | 'custom';
    customRules: ClinicalRule[];
  };
  modelSettings: {
    ensembleWeights: Record<string, number>;
    calibrationParameters: CalibrationParams;
    retrainingTriggers: RetrainingConfig;
  };
  userInterface: {
    language: 'en' | 'hi' | 'bn' | 'ta';
    voiceInputEnabled: boolean;
    explanationDetail: 'basic' | 'detailed' | 'expert';
  };
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, I'll now identify and consolidate the testable properties while eliminating redundancy:

**Property Reflection:**
- Properties 1.2 and 2.1 both test that decisions include required information - these can be combined into a comprehensive decision completeness property
- Properties 2.2 and 1.4 both test guideline references in explanations - these can be consolidated
- Properties 3.5 and 4.3 both test logging functionality - these can be combined into comprehensive audit logging
- Properties 6.1 and fail-safe behavior can be consolidated with error handling properties
- Properties related to sync (2.5) and retraining triggers (3.4, 8.1) can be grouped as system adaptation properties

### Core Correctness Properties

**Property 1: Response Time Performance**
*For any* valid patient data input, the system should generate a triage decision within 3 seconds
**Validates: Requirements 1.1**

**Property 2: Decision Completeness**
*For any* triage decision generated, the output should include a confidence score (0-100%), specific clinical factors, and plain-language reasoning with guideline references
**Validates: Requirements 1.2, 1.4, 2.1, 2.2**

**Property 3: Uncertainty-Based Human Oversight**
*For any* triage decision with confidence score below 70%, the system should generate an uncertainty flag requiring human review
**Validates: Requirements 1.3**

**Property 4: Override Capability**
*For any* triage decision, healthcare workers should be able to override the recommendation and the system should prompt for reasoning
**Validates: Requirements 3.1, 3.2**

**Property 5: Pattern-Based Learning**
*For any* detected override pattern, similar future cases should be flagged for human review
**Validates: Requirements 3.3**

**Property 6: Automatic Retraining Trigger**
*For any* 30-day period where override rate exceeds 15%, the system should trigger automatic model retraining
**Validates: Requirements 3.4**

**Property 7: Comprehensive Audit Logging**
*For any* triage decision, override, or system interaction, complete audit trails should be maintained with timestamps and relevant metadata
**Validates: Requirements 3.5, 4.3**

**Property 8: Performance Monitoring and Alerting**
*For any* detected system performance degradation or model drift, automated alerts should be generated to administrators
**Validates: Requirements 4.2**

**Property 9: Data Anonymization**
*For any* report generation or model training process, patient data should be anonymized while preserving clinical and performance information
**Validates: Requirements 4.4, 6.5**

**Property 10: Workflow Efficiency**
*For any* complete triage workflow, the process should be completable in under 5 clicks and less than 2 minutes
**Validates: Requirements 5.1**

**Property 11: Color-Coded Interface**
*For any* triage result display, the interface should use the correct color coding (red for emergent, yellow for urgent, green for non-urgent)
**Validates: Requirements 5.2**

**Property 12: Automatic Security Logout**
*For any* system session idle for more than 10 minutes, automatic logout should occur
**Validates: Requirements 5.4**

**Property 13: Fail-Safe Error Handling**
*For any* system error condition, the system should default to flagging cases for human review rather than providing unreliable recommendations
**Validates: Requirements 6.1**

**Property 14: Data Synchronization**
*For any* offline decisions made, when connectivity is restored, all decisions and logs should automatically sync to cloud storage
**Validates: Requirements 2.5**

**Property 15: Feedback Integration**
*For any* clinical override data collected, the information should be incorporated into model retraining pipelines
**Validates: Requirements 8.1**

**Property 16: A/B Testing Validation**
*For any* model update, A/B testing should be implemented to validate improvements before full deployment
**Validates: Requirements 8.3**

**Property 17: Model Performance Maintenance**
*For any* model retraining process, the resulting model should maintain above 90% agreement with senior clinician gold standards
**Validates: Requirements 8.5**

## Error Handling

The system implements a comprehensive error handling strategy based on the principle of failing safely. All error conditions default to escalating cases for human review rather than providing potentially unreliable automated recommendations.

### Error Categories and Responses

**Model Inference Errors**: When the AI model fails to generate predictions due to corrupted input data, model loading failures, or computational errors, the system immediately flags the case as requiring urgent human review and logs the error for investigation.

**Data Validation Errors**: Invalid or incomplete patient data triggers data validation warnings, prompts for data correction, and provides guidance on minimum required information for reliable triage assessment.

**Connectivity Errors**: Network failures trigger seamless transition to offline mode, with local model inference and data queuing for later synchronization when connectivity is restored.

**Authentication and Authorization Errors**: Security-related errors result in immediate session termination, audit logging, and administrator notification to prevent unauthorized access.

**Performance Degradation**: When response times exceed acceptable thresholds or model confidence drops below baseline levels, the system generates alerts and may temporarily increase uncertainty thresholds to ensure more cases receive human review.

### Error Recovery Mechanisms

**Graceful Degradation**: The system maintains core triage functionality even when non-critical components fail, ensuring patient care is never completely disrupted by technical issues.

**Automatic Retry Logic**: Transient errors trigger automatic retry with exponential backoff, while persistent errors escalate to human operators.

**Fallback Procedures**: When AI models are unavailable, the system provides structured triage checklists based on established clinical protocols to guide manual decision-making.

## Testing Strategy

The testing approach combines unit testing for specific functionality with property-based testing for universal correctness guarantees, ensuring comprehensive validation of both individual components and system-wide behaviors.

### Unit Testing Approach

Unit tests focus on specific examples, edge cases, and integration points between components. Key areas include:

- **Model Integration Tests**: Verify that AI models load correctly, process various input formats, and return properly structured outputs
- **API Endpoint Tests**: Validate REST API functionality, authentication, and error responses
- **Data Validation Tests**: Test input sanitization, validation rules, and error handling for malformed data
- **UI Component Tests**: Verify interface elements render correctly and handle user interactions appropriately

### Property-Based Testing Approach

Property-based testing validates universal properties that should hold across all valid inputs using **Hypothesis** for Python components and **fast-check** for JavaScript/TypeScript components. Each property-based test runs a minimum of 100 iterations to ensure statistical confidence in the results.

**Key Property Test Categories**:

- **Performance Properties**: Response time guarantees, resource usage constraints, and scalability characteristics
- **Safety Properties**: Fail-safe behavior, uncertainty quantification accuracy, and human oversight triggers
- **Correctness Properties**: Decision completeness, explanation quality, and clinical guideline compliance
- **Security Properties**: Data encryption, access control, and audit trail completeness

Each property-based test is tagged with explicit references to the corresponding correctness property in this design document using the format: **Feature: mediguard-triage, Property {number}: {property_text}**

### Integration and End-to-End Testing

**Shadow Mode Testing**: Deploy the system in parallel with existing triage processes to validate real-world performance without affecting patient care.

**Clinical Validation Studies**: Structured evaluation against senior clinician gold standards to measure triage accuracy, sensitivity for emergent cases, and clinical utility.

**Load Testing**: Simulate high patient volumes to validate auto-scaling capabilities and performance under stress.

**Security Testing**: Penetration testing, vulnerability assessments, and compliance validation for healthcare data protection requirements.

### Continuous Testing and Monitoring

**Model Performance Monitoring**: Continuous validation of model accuracy, calibration, and drift detection using production data.

**A/B Testing Framework**: Systematic evaluation of model improvements and feature changes before full deployment.

**Regression Testing**: Automated test suites that run with every code change to prevent introduction of bugs or performance degradation.

The testing strategy ensures that MediGuard Triage meets the highest standards for clinical AI systems, with particular emphasis on safety, reliability, and trustworthiness that are essential for healthcare applications.