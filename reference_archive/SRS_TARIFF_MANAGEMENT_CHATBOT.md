# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
# TARIFF MANAGEMENT CHATBOT

## 1. INTRODUCTION

### 1.1 PURPOSE
This Software Requirements Specification (SRS) document defines the functional and non-functional requirements for a Tariff Management Chatbot, designed to assist procurement and compliance professionals in managing tariff-related processes. The chatbot calculates tariff impacts, infers product details and HTS codes using search APIs, suggests cost-saving material compositions, and provides actionable insights through a conversational interface. This document outlines requirements for a 4-week Proof of Concept (POC), prioritizing core functionalities.

### 1.2 SCOPE
The Tariff Management Chatbot will provide:
- **Tariff Impact Calculation**: Compute tariffs and landed costs based on HS/HTS codes and material prices.
- **Product Detail Search and HTS Code Inference**: Retrieve product information via Bing/Google SERP APIs, infer material composition, and assign HTS codes.
- **Material Proportion Suggestions**: Recommend alternative material compositions to reduce tariffs while maintaining quality.
- **What-If Scenario Simulation**: Project cost impacts of tariff rate or sourcing country changes.
- **Tariff Lookup and Classification Assistance**: Retrieve tariff rates and suggest HS/HTS codes using AI.
- **Alternative Sourcing Suggestions**: Propose countries with favorable tariffs.
- **Alerts & Notifications**: Notify users of tariff changes for specific HS/HTS codes.
- **Custom Reporting & Visualization**: Generate downloadable reports and charts for tariff exposure.
- **Deferred Feature**: Order and shipment tracking.

The POC will fully implement high-priority features (Tariff Impact Calculation, Product Detail Search, Material Proportion Suggestions, Tariff Lookup, What-If Scenarios) and partially implement medium-priority features (Alternative Sourcing, Alerts, Reporting).

### 1.3 REFERENCES
- **United States International Trade Commission (USITC) HTS**: https://hts.usitc.gov/, https://dataweb.usitc.gov/
- **WTO Tariff Data**: https://ta.wto.org/, https://www.wto.org/english/tratop_e/tariffs_e/tariff_data_e.htm
- **UN Comtrade**: https://comtrade.un.org/data/
- **WCO HS Nomenclature**: http://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx
- **Data.gov HTS**: https://catalog.data.gov/dataset?q=harmonized+tariff+schedule
- **Avalara Tariff Content**: https://www.avalara.com/us/en/products/integrations/cross-border-tariff-codes.html

### 1.4 DEFINITIONS, ACRONYMS, AND ABBREVIATIONS
- **HS Code**: Harmonized System code, a 6-digit standardized code for classifying goods.
- **HTS Code**: Harmonized Tariff Schedule code, a 10-digit US-specific code.
- **Landed Cost**: Total cost including material price, tariff, taxes, and shipping.
- **POC**: Proof of Concept, a 4-week prototype.
- **SERP**: Search Engine Results Page, used for product detail retrieval.
- **FTA**: Free Trade Agreement.
- **MPF**: Merchandise Processing Fee (US).

### 1.5 ASSUMPTIONS AND CONSTRAINTS
**Assumptions:**
- Users provide HS/HTS codes, product descriptions, or company names for searches.
- Bing/Google SERP APIs return accurate product details.
- Material properties are approximated from trade data or public sources.
- Tariff datasets are accessible and reliable.

**Constraints:**
- 4-week POC limits scope to high- and medium-priority features.
- Product detail accuracy depends on public web data.
- Order tracking is deferred to post-POC phase.

## 2. OVERALL DESCRIPTION

### 2.1 PRODUCT OVERVIEW
The Tariff Management Chatbot is a web-based conversational AI tool that integrates with tariff databases (e.g., USITC, WTO, UN Comtrade) and Bing/Google SERP APIs to calculate tariffs, infer product details and HTS codes, and optimize material compositions. It supports trade professionals by providing cost analysis, compliance assistance, and strategic sourcing insights through an intuitive dialogue.

### 2.2 MAJOR CAPABILITIES
- **Tariff Impact Calculation**: Computes tariffs and landed costs using validated data sources.
- **Product Analysis**: Retrieves product details via SERP APIs, infers material composition, and assigns HTS codes.
- **Material Optimization**: Suggests cost-saving material changes with minimal quality impact.
- **Scenario Simulation**: Enables exploration of hypothetical cost scenarios.
- **Compliance Support**: Provides AI-driven tariff lookups and HTS code suggestions.
- **Sourcing Insights**: Recommends countries with lower tariffs.
- **Proactive Updates**: Alerts users to tariff changes.
- **Reporting**: Generates exportable reports and visualizations.

### 2.3 USER CATEGORIES
- **Procurement Managers**: Use tariff calculations and material/sourcing suggestions for cost optimization.
- **Compliance Officers**: Rely on accurate HTS code classification and tariff alerts.
- **Business Analysts**: Leverage reports and simulations for strategic decisions.

### 2.4 DEVELOPMENT CONSTRAINTS
- **Duration**: 4-week POC.
- **Data Access**: Relies on public APIs (USITC, WTO) and SERP APIs (Bing/Google).
- **Performance Scope**: Supports up to 100 concurrent users.
- **Interface**: Rule-based or simple AI-driven chatbot responses.

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 TARIFF IMPACT CALCULATION (FR-01)
**Functionality**: The chatbot calculates tariffs and landed costs based on HS/HTS codes, material prices, and country of origin.

**Primary Workflow**: Users provide an HS/HTS code, material costs, and country. The chatbot retrieves tariff rates and computes landed costs.

**Inputs**: HS/HTS code (6- or 10-digit), material prices (user-provided or estimated), country of origin, shipping cost (optional).

**Outputs**: Tariff amount, estimated taxes (e.g., MPF), total landed cost.

**Data Source**: USITC HTS (https://dataweb.usitc.gov/), WTO Tariff Data (https://ta.wto.org/).

**Priority**: High

**Acceptance Criteria**:
- Calculate tariff within 2 seconds for valid inputs.
- Display results in chatbot (e.g., "Tariff: $0.70, Landed Cost: $11.00").
- Prompt for valid inputs if errors occur (e.g., "Please enter a valid HTS code").

### 3.2 PRODUCT DETAIL SEARCH AND HTS CODE INFERENCE (FR-02)
**Functionality**: The chatbot accepts product descriptions and company names, retrieves details via Bing/Google SERP APIs, infers material composition, and assigns HTS codes.

**Primary Workflow**: Users input a product description (e.g., "nitrile gloves") and company name (e.g., "McKesson"). The chatbot searches public listings, extracts material details (e.g., "100% nitrile"), maps to an HTS code, and retrieves tariff rates.

**Advanced Workflow**: For composite products, the chatbot breaks down materials (e.g., "70% nitrile, 30% rubber") and calculates tariffs for each component using HTS codes.

**Inputs**: Product description, company name, country of origin.

**Outputs**: Material composition, assigned HTS code, tariff rate, justification.

**Data Source**: Bing/Google SERP APIs, WCO HS Nomenclature, UN Comtrade.

**Priority**: High

**Acceptance Criteria**:
- Retrieve product details within 5 seconds.
- Infer material composition with >80% accuracy.
- Assign HTS code and display in chatbot (e.g., "HTS 4015.19.0510, tariff: 3.0%").

### 3.3 MATERIAL PROPORTION SUGGESTIONS (FR-03)
**Functionality**: The chatbot suggests alternative material compositions to reduce tariffs while maintaining quality.

**Primary Workflow**: Users provide an HS/HTS code or product description. The chatbot identifies high-tariff materials and suggests lower-tariff alternatives based on trade data. Quality is assessed using approximated material properties (e.g., durability, strength).

**Inputs**: HS/HTS code, product/material description, current material proportions (e.g., "100% cotton").

**Outputs**: Suggested proportions (e.g., "50% polyester saves $0.50"), tariff savings, quality impact (e.g., "95% durability retained").

**Data Source**: UN Comtrade for material trade data, WCO HS Nomenclature for material classification.

**Priority**: High

**Acceptance Criteria**:
- Suggest 3 alternative compositions within 5 seconds.
- Ensure quality impact <10% (e.g., strength, durability).
- Display savings and quality impact in chatbot.

### 3.4 WHAT-IF SCENARIO SIMULATION (FR-04)
**Functionality**: The chatbot simulates cost impacts of tariff rate or sourcing country changes.

**Inputs**: HS/HTS code, material prices, current country, new tariff rate or country.

**Outputs**: Comparative cost summary (original vs. simulated).

**Data Source**: WTO Tariff Data, UN Comtrade.

**Priority**: High

**Acceptance Criteria**:
- Support 3 scenario variants.
- Display results in chatbot within 3 seconds.
- Retain results for session duration.

### 3.5 TARIFF LOOKUP AND CLASSIFICATION (FR-05)
**Functionality**: The chatbot retrieves tariff rates by HS/HTS code or product/material description, suggesting matches via AI.

**Inputs**: HS/HTS code or description (e.g., "cotton shirt").

**Outputs**: Tariff rate, suggested HS/HTS codes, reference links.

**Data Source**: WCO HS Nomenclature, Avalara API.

**Priority**: High

**Acceptance Criteria**:
- Return results within 2 seconds.
- Suggest up to 5 HS/HTS codes with >80% match confidence.
- Provide links to USITC/WCO schedules.

### 3.6 ALTERNATIVE SOURCING SUGGESTIONS (FR-06)
**Functionality**: The chatbot recommends countries with lower tariffs for materials/products.

**Inputs**: HS/HTS code, current country.

**Outputs**: Ranked list of 3–5 countries, potential savings, FTA benefits.

**Data Source**: UN Comtrade, WTO Tariff Data for FTA data.

**Priority**: Medium

**Acceptance Criteria**:
- Display insights within 5 seconds.
- Include FTA benefits where applicable.
- Allow sorting by cost in chatbot.

### 3.7 ALERTS & NOTIFICATIONS (FR-07)
**Functionality**: The chatbot registers users for email alerts on tariff changes for specific HS/HTS codes.

**Inputs**: HS/HTS codes, email address.

**Outputs**: Email alerts with tariff change details.

**Data Source**: WTO Tariff Analysis Online, Avalara API.

**Priority**: Medium

**Acceptance Criteria**:
- Notify within 24 hours of tariff changes.
- Support up to 10 subscriptions per user.
- Manage subscriptions via chatbot.

### 3.8 CUSTOM REPORTING & VISUALIZATION (FR-08)
**Functionality**: The chatbot generates downloadable reports and visualizations for tariff exposure.

**Inputs**: HS/HTS code, supplier, region, time period.

**Outputs**: CSV/PDF reports, bar/line charts.

**Data Source**: USITC HTS, UN Comtrade.

**Priority**: Medium

**Acceptance Criteria**:
- Generate output within 10 seconds.
- Support 2 chart types (bar, line).
- Provide export links via chatbot.

### 3.9 ORDER AND SHIPMENT TRACKING (FR-09)
**Functionality**: Tracks shipments and flags tariff-related risks.
**Status**: Deferred for post-POC phase.

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 PERFORMANCE REQUIREMENTS
- **Response Time**: < 3 seconds for tariff calculations, < 5 seconds for product searches.
- **Throughput**: Support 100 concurrent users.
- **Availability**: 99.5% uptime during business hours.

### 4.2 SECURITY REQUIREMENTS
- **Data Protection**: Encrypt sensitive tariff data in transit and at rest.
- **Access Control**: Role-based access for different user types.
- **API Security**: Rate limiting and authentication for external APIs.

### 4.3 USABILITY REQUIREMENTS
- **Interface**: Intuitive conversational interface with clear prompts.
- **Accessibility**: WCAG 2.1 AA compliance.
- **Mobile Support**: Responsive design for mobile devices.

### 4.4 RELIABILITY REQUIREMENTS
- **Error Handling**: Graceful degradation when external APIs are unavailable.
- **Data Validation**: Validate all inputs before processing.
- **Backup**: Daily backups of tariff data and user configurations.

## 5. SYSTEM ARCHITECTURE

### 5.1 HIGH-LEVEL ARCHITECTURE
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   External      │
│   (React/HTML)  │◄──►│   (FastAPI)     │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (ChromaDB)    │
                       └─────────────────┘
```

### 5.2 COMPONENT ARCHITECTURE
- **Frontend Layer**: React/HTML interface with real-time chat
- **API Gateway**: FastAPI backend with CORS support
- **Business Logic**: Python services for tariff calculations
- **Data Layer**: ChromaDB for vector search, SQLite for structured data
- **External Integrations**: SERP APIs, tariff databases, currency conversion

### 5.3 DATA FLOW
1. User inputs product description or HTS code
2. System queries SERP APIs for product details
3. LLM enhances search queries and classifies products
4. Vector database searches for relevant HTS codes
5. Tariff calculation engine computes costs
6. Results presented in conversational format

## 6. TECHNICAL SPECIFICATIONS

### 6.1 TECHNOLOGY STACK
- **Backend**: Python 3.9+, FastAPI, ChromaDB, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, React (optional)
- **AI/ML**: Ollama (llama3.2:3b), Vector embeddings
- **APIs**: Bing/Google SERP, forex-python, USITC, WTO
- **Deployment**: Docker, uvicorn

### 6.2 DATABASE DESIGN
- **ChromaDB**: Vector embeddings for semantic search
- **SQLite**: Structured tariff data, user preferences
- **File Storage**: Excel data, uploaded documents

### 6.3 API SPECIFICATIONS
- **RESTful APIs**: Standard HTTP methods
- **WebSocket**: Real-time chat functionality
- **Rate Limiting**: 100 requests/minute per user
- **Authentication**: API keys for external services

## 7. IMPLEMENTATION PLAN

### 7.1 PHASE 1 (Week 1-2): Core Features
- [x] Basic HTS search with vector database
- [x] LLM integration for query enhancement
- [x] Tariff calculation engine
- [x] Currency conversion
- [x] Basic chat interface

### 7.2 PHASE 2 (Week 3): Advanced Features
- [ ] SERP API integration for product details
- [ ] Material composition inference
- [ ] Alternative sourcing suggestions
- [ ] Scenario simulation
- [ ] Enhanced reporting

### 7.3 PHASE 3 (Week 4): Polish & Testing
- [ ] Alert system implementation
- [ ] Advanced visualizations
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Documentation completion

## 8. TESTING STRATEGY

### 8.1 UNIT TESTING
- Individual component testing
- API endpoint validation
- Data processing accuracy

### 8.2 INTEGRATION TESTING
- End-to-end workflow testing
- External API integration
- Database operations

### 8.3 USER ACCEPTANCE TESTING
- Real-world scenario testing
- Performance under load
- Usability assessment

## 9. DEPLOYMENT & MAINTENANCE

### 9.1 DEPLOYMENT STRATEGY
- Containerized deployment with Docker
- Environment-specific configurations
- Automated CI/CD pipeline

### 9.2 MONITORING & LOGGING
- Application performance monitoring
- Error tracking and alerting
- Usage analytics

### 9.3 MAINTENANCE PLAN
- Regular tariff data updates
- API dependency management
- Security patch updates

## 10. RISK ASSESSMENT

### 10.1 TECHNICAL RISKS
- **External API Dependencies**: Mitigation through fallback data sources
- **LLM Performance**: Backup to rule-based classification
- **Data Accuracy**: Multiple source validation

### 10.2 BUSINESS RISKS
- **Regulatory Changes**: Flexible tariff data structure
- **User Adoption**: Intuitive interface design
- **Competition**: Unique AI-driven insights

## 11. SUCCESS METRICS

### 11.1 PERFORMANCE METRICS
- Response time < 3 seconds
- 99.5% uptime
- 100 concurrent users

### 11.2 ACCURACY METRICS
- >80% HTS code accuracy
- >90% tariff calculation accuracy
- <5% error rate

### 11.3 USER SATISFACTION
- User engagement metrics
- Feature adoption rates
- Support ticket volume

## 12. CONCLUSION

This SRS document provides a comprehensive framework for developing the Tariff Management Chatbot POC. The system will deliver significant value to procurement and compliance professionals by automating tariff calculations, providing intelligent product classification, and offering strategic sourcing insights. The 4-week development timeline ensures rapid delivery while maintaining quality and functionality.

The modular architecture allows for future enhancements and scalability, while the focus on core features ensures a robust foundation for the production system. 