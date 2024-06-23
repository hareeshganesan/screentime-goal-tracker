# Screen Time Goal Tracker

## Purpose

This tracker helps iPhone and Mac users set and visualise screen time goals. It provides insights into daily screen time trends, unnecessary app usage, and pickup frequency, allowing users to set and track goals.

Key features include:
- Daily screen time and pickup trends visualization
- Unnecessary screen time tracking (where users specify which apps are the unnecessary ones they're targeting)
- Goal achievement display
- Detailed app usage breakdown
- Suggestions for alternative activities when screen time goals are exceeded

## Prerequisites

- macOS with Screen Time enabled
- Python 3.7+
- Access to the macOS Screen Time database (requires appropriate permissions)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/hareeshganesan/screen-time-goal-tracker.git
   cd screen-time-goal-tracker
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running Locally

1. Ensure you have the necessary permissions to access the Screen Time database on your Mac.

2. Run the Streamlit app:
   ```
   streamlit run screentime_app.py
   ```

3. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

## Development

To contribute to the Screen Time Goal Tracker or customize it for your needs, follow these steps:

1. Fork the repository on GitHub.

2. Clone your forked repository:
   ```
   git clone https://github.com/your-username/screen-time-goal-tracker.git
   ```

3. Create a new branch for your feature or bug fix:
   ```
   git checkout -b feature/your-feature-name
   ```

4. Make your changes to the code. The main files you'll be working with are:
   - `screentime_app.py`: Contains the Streamlit app logic and UI components
   - `screentime.py`: Handles database querying and data processing

5. Test your changes locally by running the app:
   ```
   streamlit run screentime_app.py
   ```

6. Commit your changes:
   ```
   git add .
   git commit -m "Add your commit message here"
   ```

7. Push your changes to your fork:
   ```
   git push origin feature/your-feature-name
   ```

8. Create a pull request on the original repository to propose your changes.

## Customization

You can customize the app by modifying the following:

- Adjust the list of `unnecessary_apps` in `screentime_app.py` to fit your personal goals.
- Modify the color thresholds and intensity in the `get_color` and `get_color_intensity` functions.
- Add or remove visualizations by editing the main function in `screentime_app.py`.

## Troubleshooting

- If you encounter permission errors, ensure you have the necessary rights to access the Screen Time database. You may need to run the script with `sudo` or adjust file permissions.
- If the database file is not found, verify that Screen Time is enabled on your Mac and that the file path is correct for your system.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
