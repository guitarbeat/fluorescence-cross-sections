# Fluorescence Cross-Sections Viewer

This project provides a Streamlit web application for visualizing and exploring fluorescence cross-section data for various fluorophores and lasers.

## Features

- View excitation and emission spectra.
- Explore two-photon cross-section data.
- Manage lists of lasers and fluorophores.
- Visualize data using interactive plots (Plotly, Matplotlib).
- (Potentially) Integrate with FPbase and Google Sheets for data retrieval.

## Setup

This project uses Python and requires a virtual environment for managing dependencies.

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd fluorescence-cross-sections
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    The required packages and their specific versions are listed in `requirements.txt`. Install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Testing

Install the dependencies listed in `requirements.txt` and run the test suite with:

```bash
pip install -r requirements.txt
pytest
```

## Running the Application

Once the setup is complete, you can run the Streamlit application:

```bash
streamlit run app.py
```

This will start a local web server, and the application should open automatically in your default web browser.

## Project Structure

- `app.py`: Main Streamlit application script.
- `requirements.txt`: Pinned Python dependencies.
- `Procfile`: Configuration for deployment platforms (e.g., Heroku).
- `.gitignore`: Specifies intentionally untracked files that Git should ignore.
- `data/`: Contains data files (CSV, TXT, DAT) for fluorophores, lasers, etc.
- `src/`: Source code modules:
    - `api/`: External API interactions (FPbase, Google).
    - `assets/`: Static files (images).
    - `components/`: Reusable Streamlit UI components.
    - `config/`: Application configuration.
    - `plots/`: Plotting functions.
    - `state/`: Session state management.
    - `utils/`: Helper functions.

## Data Sources

The application utilizes data stored locally in the `data/` directory, potentially supplemented by external sources via the `src/api/` modules.

