# Talent Tracking

This is a simple database-backed web app. It's for tracking data about individuals through a frequent survey. 
This need could probably be met by a commercial customer relationship management system, but this is to prove value rather
than to generate revenue or be a long-term solution.

The diagram below shows the current database structure.

![Entity-relationship diagram](talent-tracker.png)

## Application structure
This is a monolithic app. This use case is not complex enough to need microservices. Future feature requests might 
necessitate it but for now monolith all the way.

It uses
- sqlalchemy for the Models
- Flask for the webserver
- the GOVUK Design System for the frontend, although it uses pre-compiled assets rather than the npm method

## TODO:

- add an AuditEvent class
- start adding routes with tests
- implement an `authentication` blueprint with tests


## Contribution guidelines
Please contribute to this repo! Any contributions need to be well-tested and pass all the existing tests.
