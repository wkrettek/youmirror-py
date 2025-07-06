# agents.md

This file provides agents with guidance when working in this project.

## Code Style Guidelines
- Use type hints frequently
    - Use modern `dict` `list` instead of `Dict` `List`
    - Use descriptive variable names
    - Use checks when accessing dictionary keys or doing actions that may fail
    - Break out exception handlers into specific exceptions when relevant
    - Document complex functions with docstrings

## Workflow
- Work like a scientist. Think step by step and seek evidence before declaring success
- Be clear and concise in your writing, without flowery language
- Create a PLAN.md file to plan and track your work
    - Example
    ```
    # <Issue title>
    ## Description
    <The work requires that I do X and achieve Y>
    ## Steps
    ### Step 1: <thing to do>
    - [ ] <Task 1>
        - [ ] <Subtask 1>
    - [ ] <Task 2>
    ### Step 2: <next thing>
    - [ ] <Task 1>
    ...
    ### Notes
    ```
    - Update the PLAN.md as you complete tasks
