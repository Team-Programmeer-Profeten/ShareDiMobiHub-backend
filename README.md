# ShareDiMobiHub-backend

This project was made for the Centre of Expertise: Smart and Sustainable Cities, to be added to the dashboard deelmobiliteit from CROW.

The way it works is we get a request from the frontend with options for what data is requested and from which municipality, we then request the neccesary data from the api from api.dashboarddeelmobiliteit.nl based on which we create a pdf which is then send back. This report can be used for certain municipality projects.

There is also a login functionality that uses a SQLite database to check if users are from a certain municipality.

The application is meant to run in a docker container and is stateless.