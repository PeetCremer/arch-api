# Architecture API (arch-api)
This Web API consumes building limits and height plateaus, splits up the building limits according to the height plateaus, and stores these three entities (building limits, height plateaus and split building limits) in a persistent way.

The API is deployed to: **http://api.arch-api.com**
You can find the documentation here: **http://api.arch-api.com/docs**

## Features
- `splits` (the results of splitting building limits by height plateaus) can be organized into different `projects`
- Supported operations:
    - `POST /projects/{project}/splits` creates a new `split`, gives it an `id`, and stores it in the database
    - `GET /projects/{project}/splits/{id}` returns a previously created `split` by its `id`
    - `GET /projects/{project}/splits` list all `splits` in a `project`
    - `DELETE /projects/{project}/splits/{id}` deletes a previously created `split` by its `id`
    - `DELETE /projects/{project}/splits` deletes all `splits` in a `project`
- Order your `splits` into different `projects`**Splitting** of building limits according to height plateaus using the
- Automatic deployment of docker image to cloud registry using Github Actions

## Development
### Prerequisites
- [Docker](https://www.docker.com/) to conveniently run a MongoDB instance
- Python 3.11 or greater. I recommend installing it with [pyenv](https://github.com/pyenv/pyenv)
- [Poetry](https://python-poetry.org/) for dependency management

### Setup
#### 1. Cloning the repository
Should be obvious

#### 2. Installing dependencies
```
poetry install
```
#### 3. Setting environment variables
Create a `.env` file with the following content in the repository root
```
MONGODB_URL=mongodb://root:example@0.0.0.0:27017/
UVICORN_HOST=127.0.0.1
BASE_URL="http://localhost:8000"
```
or set the environment variables in any other way you prefer.

#### 4. Run the MongoDB instance
```
docker-compose up -d
```
Or with the convenience shell script:
```
./run_dev_stack.sh
```

#### 5. Run the API
Start the local API server on http://localhost:8000 with:
```
poetry run python arch_api
```
The server automatically reloads when you make changes to the code.

### Testing
Run the tests using
```
poetry run pytest .
```
There are unit and integration tests. The integration tests require a running MongoDB instance.

### Visualize the testcases
![title](images/vaterlandsparken.png)
Call the CLI script
```
poetry run python tests/visualize_testcases.py --testcase=<testcase> --base_url=<base_url>
```
to visualize one of the testcases in `tests/testcases/**`.
The `base_url` argument (or your `BASE_URL` environment variable) must point either to a locally running API server or to the deployed API server.

## Deployment
#### 1. Build the Docker image
You can build the `arch-api` API docker container using the covenvience shell script
```
./docker_build.sh
```
which will build the image `europe-west1-docker.pkg.dev/arch-api-403919/arch-api-registry/arch-api:latest`
#### 2. Push it to a Cloud Cloud Registry
You need to push the image to the registry in your cloud.
For Google Cloud Platform, there is a Github Action that builds the image on each push to the `main` branch and pushes it to the GCP registry.

#### 3. Create a VM instance in the cloud
Create a VM instance in your favourite cloud

#### 4. Deploying the API stack
Copy the `docker-compose-prod.yml` and `run_prod_stack.sh` files to the VM instance, for example using `scp`. Then call:
```
./run_prod_stack.sh
```
which will run the `arch-api` docker container alongside a MongoDB container and host the API on port `80` of the VM instance.

In order for this to work, the VM instance needs to have port `80` open for incoming traffic.
Additionally, the VM instance needs to have access to the GCP registry in order to pull the `arch-api` docker image.

## Technologies
```mermaid
graph LR
user([User]) -->|"POST\nbuilding_limits\nheight_plateaus"| validation["Validation\n(pydantic)"] --> fast_api[FastAPI] --> create_split[create split] -->|store split| database[(MongoDB)]
user -->|GET| fast_api -->|fetches split| database
user -->|"POST\nLongitude\nLatitude"| fast_api -->|geoquery| database
```

`arch-api` is build on the following technologies:
- API: [FastAPI](https://fastapi.tiangolo.com/) for serving a REST API in Python
- Database: [MongoDB](https://www.mongodb.com/) for persistently storing the split building limits.
    - MongoDB natively supports [geospatial queries](https://www.mongodb.com/docs/manual/geospatial-queries/) and is therefore a good fit for the use case of querying building limits by location.
    - Enabling geospatial queries is not yet implemented in the API, but planned for the future
- Containerization: [Docker](https://www.docker.com/)
- Cloud hosting: [Google Cloud Platform](https://cloud.google.com/)
    - The containers run in a [Docker Compose](https://docs.docker.com/compose/) cluster in a VM instance
- IO validation:
    - [pydantic](https://docs.pydantic.dev/latest/) for validating input and output of the API.
    - [geojson-pydantic](https://github.com/developmentseed/geojson-pydantic) to support validation of inputs and outputs following the [GeoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946)
- Geometric queries and visualization: [geopandas](https://geopandas.org/)
- Testing: [pytest](https://docs.pytest.org) for unit and integration tests
- Code cleanliness:
    - [mypy](https://mypy-lang.org/) for static type checking.
    - [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

## Next steps
- Improve the CI / CD setup to automatically deploy the API to the cloud from release branches
- Improve CI / CD to include testing when merging Pull Requests
- Implement geospatial queries in the API
- Implement authentication and authorization
- Create more testcases and harden the API against edge cases
