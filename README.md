# Tool for Testing Camunda 8 SaaS Connections

Camunda internal project: https://jira.camunda.com/browse/ACADEMY-3286

## Purpose

You need to ensure that you can connect to Camunda 8 SaaS as a prerequisite for a Camunda 8 training for developers.
This tool provides a script that will verify the connection.

## Prerequisites

Any Windows, Linux, Mac computers.

## How to Use

1. Download the project
2. Ask Camunda training organizers for the envVars.txt file
3. Place the envVars.txt in the folder root.
4. From the root directory of this project:
5. Run the script:
   - **Windows**: Open PowerShell and run `./testConnection.ps1`
   - **Mac/Unix**: Open the terminal and run `chmod u+x testConnection.sh && ./testConnection.sh`
6. Review the result for success or failure.

## Connection Result

The script will test your connection to Camunda 8 SaaS and provide one of the following outcomes:

- **Success**: If a valid response is received from Camunda 8 SaaS, the script will print `***** CONNECTION SUCCESSFUL *****`.
  This confirms a successful connection.
  You'll be able to do the training exercises.
- **Failure**: If the connection cannot be established, the script will print `***** CONNECTION FAILED *****`.
  Potential causes of failure include:

  - Invalid access token or authorization issues.
  - Network or endpoint connectivity problems.

  In case of failure, please contact your training manager with the error details.

## Script Dependencies

These scripts are designed for ease of use without requiring additional software installation.
They use built-in functions that are standard in Unix and Windows systems.

## Tested Environments

These tools have been tested in these environments:

- Macbook Pro Sonoma 14.7
- Windows Server 2022 Datacenter Version 21H2
- Ubuntu 22
- Amazon Linux AWS
- Red Hat

## Troubleshooting

Known issues:

- **For Windows systems**, if you encounter the error: _"Execution of scripts is disabled on this system"_, open a command-line terminal (cmd.exe) and run:
  ```bash
  powershell -ExecutionPolicy Bypass -File testConnection.ps1
  ```

If you have a new issue, please just create it in the github repository
