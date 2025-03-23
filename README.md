# rc-DACFOI

A semantic search web application for identifying research faculty at the University of Virginia whose work aligns with the UVA Data Analytics Center’s (DAC) domain expertise.

This initiative is part of a broader effort by the DAC to enhance and streamline faculty outreach, especially toward those with active NIH funding and research interests aligned with data science, analytics, and computational methods.

## Key Features
- Semantic Search: Leverages OpenAI embeddings and cosine similarity to match natural language queries to relevant faculty profiles.
- NIH Funding Filters: Restrict searches to faculty with NIH-funded projects using metadata from external grant repositories.
- Dynamic Query Support: Natural language input can be filtered by school, department, NIH activity code, and other parameters.
- Automated Pipelines: Periodically scrapes and processes UVA faculty profile data and research project metadata.
- Efficient Vector Indexing: Uses FAISS for fast similarity search across faculty profile embeddings.

## Embedding System
The system generates vector embeddings for each faculty profile using OpenAI’s text-embedding-ada-002 model. To support large texts, it:
- Tokenizes and chunks large inputs
- Embeds each chunk independently
- Averages the resulting vectors (mean pooling) for a robust representation

## Search Filters
- Search Query: Used for semantic matching (Include natural language description of research)
- Limit: Number of results to return
- School: UVA school (e.g. School of Engineering and Applied Sciences)
- Department: UVA school-specific departments
- Activity Code: Code describing NIH grant type
- Agency IC Admin: NIH institute responsible for managing a funded project

## Set Up
To launch a local instance of the web application, in a local directory run the following commands:

NOTE: You must use Python 3.12.x to run `setup.py` in step 3

1. `git clone https://github.com/galitz-matt/rc-DACFOI.git`
2. `cd rc-DACFOI`
3. `python setup.py` (You will be prompted for an OpenAI API key)
4. `source venv/bin/activate` or `./venv/Scripts/Activate.ps1` (Linux/MacOS or Windows respectively)
5. `python -m backend.app`
6. Flask launched the local development server, open the URL provided in a browser.

### Example Output
(venv) matt@Matthews-MacBook-Pro rc-DACFOI % python -m backend.app
 * Serving Flask app 'backend.core'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit

## Scope of Contributions
- System Architecture: Designed the full architecture of the application, including embedding pipeline, storage system, and search query logic.
- Backend Development: Implemented all backend services in the `backend` directory.
- Containerization: Wrote the Dockerfile and associated config files to enable reproducible, containerized deployment.
- Database Design: Defined and implemented the database schema to support faculty metadata storage, indexing, and query filtering.
