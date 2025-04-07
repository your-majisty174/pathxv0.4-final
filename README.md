# PathX - Logistics Optimization Platform

PathX is a comprehensive logistics optimization platform designed to streamline and optimize delivery routes, warehouse operations, and supply chain management.

## Project Structure

```
pathx/
├── data/           # Raw and processed data files
├── notebooks/      # Jupyter notebooks for analysis and experimentation
├── src/            # Source code
│   ├── api/        # API endpoints and services
│   ├── models/     # Machine learning and optimization models
│   ├── dashboard/  # Web dashboard components
│   └── utils/      # Utility functions and helpers
├── tests/          # Test files
├── requirements.txt # Project dependencies
└── README.md       # Project documentation
```

## Features

- Route optimization using advanced algorithms
- Real-time tracking and monitoring
- Data-driven decision making
- Interactive dashboard for visualization
- API integration capabilities
- Machine learning models for demand forecasting

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pathx.git
cd pathx
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the API server:

```bash
cd src/api
uvicorn main:app --reload
```

2. Launch the dashboard:

```bash
cd src/dashboard
streamlit run app.py
```

## Development

- Run tests:

```bash
pytest tests/
```

- Format code:

```bash
black src/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
