# Marketing Impact Simulator

A Streamlit application that simulates the impact of inefficient marketing spend on business ROIC (Return on Invested Capital) using Monte Carlo simulation.

## Features

- ROIC simulation based on user-defined business metrics
- Visualization of marketing spend inefficiency impact
- Monte Carlo simulation for robust analysis
- Clean, iOS-inspired user interface

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run src/app.py
```

## Project Structure

- `src/app.py`: Main Streamlit application
- `src/simulation/`: Core simulation logic
- `src/ui/`: UI components and styling
- `tests/`: Test suite 