# MilQual - Military Quality PCB Tracker

A Django application for tracking PCBs through a multi-stage quality testing workflow.

## Features

- Multi-level user groups with specific permissions
- PCB tracking through testing workflow
- Module assembly from verified PCBs
- File attachments (.xlsx reports)
- Quality assurance verification steps
- Manager sign-off functionality

## User Groups and Permissions

- `pcb_testing` - Test individual PCBs

- `Environmental_tester_lvl1` - Perform environmental testing
- `Manager_lvl1` / `Manager_lvl2` - Review and sign off completed modules
- `Admin` - Full system access

## Workflow

1. Board testers test individual PCBs and upload .xlsx reports
2. QA verifies the test results and approves
3. Assemblers create modules from approved PCBs
4. Functional testers test the modules and upload reports
5. QA verifies functional test results
6. Environmental testers perform environmental testing
7. Functional testers perform final functional tests
8. QA verifies final results
9. Managers sign off on completed modules

## Setup

1. Make sure Docker and Docker Compose are installed
2. Clone the repository
3. Run `docker-compose up --build` to start the application
4. Access the application at `http://localhost:8000`
5. Access the admin at `http://localhost:8000/admin`

## Development

To run migrations after initial setup:
```bash
docker-compose exec web python manage.py migrate
```

To create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will automatically create all necessary user groups and assign permissions.