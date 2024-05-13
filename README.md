<p align="center">
  <img src="assets/wordart.png" alt="WordArt Image" width="450"/> <!-- Adjust width as needed -->
</p>


## pythonOBIEE

A Python package for working with Oracle Business Intelligence Enterprise Edition (OBIEE) via the Web Services SOAP API.

For now i have only implemented functionality to export analysis. This was all i needed but pull request are welcome if you would like to extend this to do other things.

## Installation

You can install a specific version of `pythonOBIEE` directly from GitHub using the following command:


```bash
pip install git+https://github.com/JustinOstrowsky/pythonOBIEE@v1.0.0#egg=pythonOBIEE
```

## Requires     
`zeep 4.2.0 or later`
`python 3.10 or later`

## Example Usage

### Export reports and save to disk

```py
from getpass import getpass
from pythonOBIEE import build_client, OBIEESession, OBIEEAnalysisExporter, Report

# Get credentials
username = input("Enter your username: ")
password = getpass("Enter your password: ")

# Set output folder
output_folder = "/your/local/path"

# Create our report objects
reports = [
    Report("/shared/Report/Path/Report1", "CSV", output_folder),
    Report("/shared/Report/Path/Report2", "EXCEL2007", output_folder),
]

# WSDL URL
wsdl = "http://your-OBIEE-server/analytics-ws/saw.dll/wsdl/v10"

# Build the client
client = build_client(wsdl)

# Create session
with OBIEESession(client, username, password):
    # Create analysis exporter
    analysis_exporter = OBIEEAnalysisExporter(client)

    # Export reports
    for report in reports:
        # Export and save
        analysis_exporter.export_and_save(report)
```

### Export report to dataframe

While this package does not directly allow you to export to a dataframe, you can get the exported file in memory, which you can then load with Pandas to a dataframe. You most likely want to export as a CSV for this use case.

```py
from getpass import getpass
import pandas as pd
from pythonOBIEE import build_client, OBIEESession, OBIEEAnalysisExporter, Report

# Get credentials
username = input("Enter your username: ")
password = getpass("Enter your password: ")

# Create a Report object
report = Report("/shared/Report/Path/Report1", "CSV")

# WSDL URL
wsdl = "http://your-OBIEE-server/analytics-ws/saw.dll/wsdl/v10"

# Build the client
client = build_client(wsdl)

# Create session
with OBIEESession(client, username, password):
    # Create analysis exporter
    analysis_exporter = OBIEEAnalysisExporter(client)

    # Export report
    # Returns a tuple. The first element is the file-like object, the second element is the file extension (.csv, .xlsx, etc.)
    report_file, file_extension = analysis_exporter.export_to_file_like_object(report)

    df = pd.read_csv(report_file)

    # Print the first few lines of the dataframe
    print(df.head())

```

### Logging

pythonOBIEE supports logging. Setting the logging level to INFO provides useful detail. More detailed information is available at the DEBUG level.
For DEBUG level logging, you will likely want to configure the log level specifically for pythonOBIEE to avoid flooding the console with messages from other modules.

```py
import logging

# Set the general logging level to INFO
logging.basicConfig(level=logging.INFO)

# Set the logging level specifically for the pythonOBIEE module to DEBUG
logging.getLogger("pythonOBIEE").setLevel(logging.DEBUG)

```
